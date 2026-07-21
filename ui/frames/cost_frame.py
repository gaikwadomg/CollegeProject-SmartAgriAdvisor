import customtkinter as ctk

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from ui.components.result_panel import ResultPanel
from ui.components.chart_widget import ChartWidget
from utils.logger import get_logger
from utils.helpers import format_currency

logger = get_logger(__name__)


class CostFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title='💰 Cost & Profit Analysis', subtitle='Estimate costs, revenue, and profit for your crop', **kwargs)
        
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.main_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        
        # --- Left Column: Inputs ---
        self.input_card = ctk.CTkFrame(self.main_container, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        input_title = ctk.CTkLabel(self.input_card, text="Cost & Revenue Inputs", font=ThemeManager.get_font("subheading"))
        input_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        self.inputs = {}
        
        costs = [
            ("Seed Cost (₹)", "seed"),
            ("Fertilizer Cost (₹)", "fertilizer"),
            ("Pesticide Cost (₹)", "pesticide"),
            ("Labor Cost (₹)", "labor"),
            ("Electricity/Other Cost (₹)", "other")
        ]
        
        for label, key in costs:
            self.inputs[key] = InputGroup(self.input_card, label=label, placeholder="0", input_type="number")
            self.inputs[key].pack(fill="x", padx=15, pady=5)
            
        revenue = [
            ("Expected Yield (kg)", "yield"),
            ("Selling Price (₹/kg)", "price")
        ]
        
        for label, key in revenue:
            self.inputs[key] = InputGroup(self.input_card, label=label, placeholder="0", input_type="number")
            self.inputs[key].pack(fill="x", padx=15, pady=5)
            
        self.calc_btn = ctk.CTkButton(
            self.input_card,
            text="Calculate",
            font=ThemeManager.get_font("subheading"),
            height=45,
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            command=self._calculate
        )
        self.calc_btn.pack(pady=20, padx=15, fill="x")
        
        # --- Right Column: Results & Charts ---
        self.results_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.results_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.results_panel = ResultPanel(self.results_container, title="Analysis Results")
        self.results_panel.pack(fill="x", pady=(0, 15))
        
        self.charts_frame = ctk.CTkFrame(self.results_container, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True)
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(1, weight=1)
        
        self.pie_chart = ChartWidget(self.charts_frame)
        self.pie_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.bar_chart = ChartWidget(self.charts_frame)
        self.bar_chart.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
    def _calculate(self):
        try:
            vals = {}
            for k, inp in self.inputs.items():
                val_raw = inp.get_value()
                try:
                    vals[k] = float(val_raw) if val_raw else 0.0
                except (ValueError, TypeError):
                    vals[k] = 0.0
                
            total_investment = vals['seed'] + vals['fertilizer'] + vals['pesticide'] + vals['labor'] + vals['other']
            expected_revenue = vals['yield'] * vals['price']
            profit_loss = expected_revenue - total_investment
            roi = (profit_loss / total_investment * 100) if total_investment > 0 else 0
            break_even = (total_investment / vals['price']) if vals['price'] > 0 else 0
            
            # Update Results
            results_dict = {
                "Total Investment": format_currency(total_investment),
                "Expected Revenue": format_currency(expected_revenue),
                "Profit / Loss": format_currency(profit_loss),
                "ROI": f"{roi:.2f}%",
                "Break-even Yield": f"{break_even:.2f} kg"
            }
            self.results_panel.set_results(results_dict)
            
            # Update Charts
            cost_labels = ["Seed", "Fertilizer", "Pesticide", "Labor", "Other"]
            cost_values = [vals['seed'], vals['fertilizer'], vals['pesticide'], vals['labor'], vals['other']]
            
            if sum(cost_values) > 0:
                self.pie_chart.create_pie_chart(
                    data=cost_values,
                    labels=cost_labels,
                    title="Cost Breakdown"
                )
                
            self.bar_chart.create_bar_chart(
                data=[total_investment, expected_revenue, profit_loss],
                labels=["Investment", "Revenue", "Profit"],
                title="Financial Summary"
            )
            
            if self.prediction_service:
                input_data = {
                    'seed_cost': vals['seed'],
                    'fertilizer_cost': vals['fertilizer'],
                    'pesticide_cost': vals['pesticide'],
                    'labor_cost': vals['labor'],
                    'other_cost': vals['other'],
                    'expected_yield': vals['yield'],
                    'selling_price': vals['price']
                }
                result_data = {
                    'total_investment': total_investment,
                    'expected_revenue': expected_revenue,
                    'profit': profit_loss,
                    'roi': roi,
                    'break_even_yield': break_even
                }
                
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type="cost_estimation",
                    input_data=input_data,
                    result_data=result_data,
                    farm_id=None
                )
                
        except Exception as e:
            logger.error(f"Cost calculation error: {e}")
            self.show_error("An error occurred during calculation.")
