import customtkinter as ctk
from ui.frames.content_frame import ContentFrame
from ui.components.cards import ThemeManager, InputGroup, ResultPanel
from ui.components.chart_widget import ChartWidget
from utils.logger import get_logger

try:
    from utils.helpers import format_currency
except ImportError:
    def format_currency(val):
        return f"₹{val:,.2f}"

logger = get_logger(__name__)

class CostFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title='💰 Cost & Profit Analysis', subtitle='Estimate costs, revenue, and profit for your crop', **kwargs)
        
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Layout: Left side inputs, Right side results & charts
        self.main_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        
        # --- Left Column: Inputs ---
        self.input_card = ctk.CTkFrame(self.main_container, fg_color=ThemeManager.get_color("card_bg"), corner_radius=12)
        self.input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        input_title = ctk.CTkLabel(self.input_card, text="Cost & Revenue Inputs", font=ctk.CTkFont(size=16, weight="bold"))
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
            self.inputs[key] = InputGroup(self.input_card, label=label, placeholder="0")
            self.inputs[key].pack(fill="x", padx=15, pady=5)
            
        revenue = [
            ("Expected Yield (kg)", "yield"),
            ("Selling Price (₹/kg)", "price")
        ]
        
        for label, key in revenue:
            self.inputs[key] = InputGroup(self.input_card, label=label, placeholder="0")
            self.inputs[key].pack(fill="x", padx=15, pady=5)
            
        self.calc_btn = ctk.CTkButton(
            self.input_card,
            text="Calculate",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
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
            # Gather values (default to 0 if empty)
            vals = {}
            for k, inp in self.inputs.items():
                val_str = inp.get().strip()
                vals[k] = float(val_str) if val_str else 0.0
                
            total_investment = vals['seed'] + vals['fertilizer'] + vals['pesticide'] + vals['labor'] + vals['other']
            expected_revenue = vals['yield'] * vals['price']
            profit_loss = expected_revenue - total_investment
            roi = (profit_loss / total_investment * 100) if total_investment > 0 else 0
            break_even = (total_investment / vals['price']) if vals['price'] > 0 else 0
            
            # Update Results
            self.results_panel.clear()
            self.results_panel.add_detail("Total Investment", format_currency(total_investment))
            self.results_panel.add_detail("Expected Revenue", format_currency(expected_revenue))
            
            pl_color = "green" if profit_loss >= 0 else "red"
            self.results_panel.add_detail("Profit / Loss", format_currency(profit_loss), text_color=pl_color)
            self.results_panel.add_detail("ROI", f"{roi:.2f}%", text_color=pl_color)
            self.results_panel.add_detail("Break-even Yield", f"{break_even:.2f} kg")
            
            # Update Charts
            cost_labels = ["Seed", "Fertilizer", "Pesticide", "Labor", "Other"]
            cost_values = [vals['seed'], vals['fertilizer'], vals['pesticide'], vals['labor'], vals['other']]
            
            if sum(cost_values) > 0:
                self.pie_chart.plot_pie_chart(
                    labels=cost_labels,
                    sizes=cost_values,
                    title="Cost Breakdown"
                )
                
            self.bar_chart.plot_bar_chart(
                categories=["Investment", "Revenue", "Profit"],
                values=[total_investment, expected_revenue, profit_loss],
                title="Financial Summary",
                ylabel="Amount (₹)"
            )
            
            # Optionally save to database
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
                
        except ValueError:
            self.results_panel.clear()
            self.results_panel.add_detail("Error", "Please enter valid numeric values for all fields.", text_color="red")
        except Exception as e:
            logger.error(f"Cost calculation error: {e}")
            self.results_panel.clear()
            self.results_panel.add_detail("Error", "An unexpected error occurred.", text_color="red")
