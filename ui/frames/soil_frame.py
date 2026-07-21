import customtkinter as ctk
from ui.base_frame import ContentFrame
from ui.components.input_group import InputGroup
from ui.components.chart_widget import ChartWidget
from ui.theme import ThemeManager
from ml.soil.analyze import SoilHealthAnalyzer

class SoilFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master, 
            title='🌍 Soil Health Analysis', 
            subtitle='Analyze your soil composition and get recommendations', 
            **kwargs
        )
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        self.analyzer = SoilHealthAnalyzer()
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Input Card
        self.input_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.input_card.pack(fill="x", padx=10, pady=10)
        
        self.input_card.grid_columnconfigure((0, 1), weight=1)
        
        self.inputs = {}
        
        # Row 0
        self.inputs['n'] = InputGroup(self.input_card, label="Nitrogen (mg/kg)", input_type="number", required=True)
        self.inputs['n'].grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['p'] = InputGroup(self.input_card, label="Phosphorus (mg/kg)", input_type="number", required=True)
        self.inputs['p'].grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Row 1
        self.inputs['k'] = InputGroup(self.input_card, label="Potassium (mg/kg)", input_type="number", required=True)
        self.inputs['k'].grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['ph'] = InputGroup(self.input_card, label="pH Level", input_type="number", required=True, min_val=0, max_val=14)
        self.inputs['ph'].grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Row 2
        self.inputs['oc'] = InputGroup(self.input_card, label="Organic Carbon (%)", input_type="number", required=True)
        self.inputs['oc'].grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['moisture'] = InputGroup(self.input_card, label="Moisture (%)", input_type="number", required=True, min_val=0, max_val=100)
        self.inputs['moisture'].grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Analyze Button
        self.analyze_btn = ctk.CTkButton(
            self.content_area,
            text="Analyze Soil",
            font=ThemeManager.get_font("button"),
            fg_color=ThemeManager.get_color("success"),
            hover_color=ThemeManager.get_color("success_hover"),
            command=self._on_analyze
        )
        self.analyze_btn.pack(pady=20)
        
        # Results Section (Hidden initially)
        self.results_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Score Card
        self.score_card = ctk.CTkFrame(self.results_frame, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.score_card.pack(fill="x", padx=10, pady=10)
        
        self.score_label = ctk.CTkLabel(self.score_card, text="", font=ctk.CTkFont(size=48, weight="bold"))
        self.score_label.pack(pady=(20, 5))
        
        self.grade_label = ctk.CTkLabel(self.score_card, text="", font=ThemeManager.get_font("subheading"))
        self.grade_label.pack(pady=(0, 20))
        
        # NPK Chart
        self.chart_widget = ChartWidget(self.results_frame)
        self.chart_widget.pack(fill="x", padx=10, pady=10)
        
        # Deficiencies & Suggestions Card
        self.info_card = ctk.CTkFrame(self.results_frame, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.info_card.pack(fill="x", padx=10, pady=10)
        
        self.info_text = ctk.CTkTextbox(self.info_card, height=200, font=ThemeManager.get_font("body"), fg_color="transparent")
        self.info_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.info_text.configure(state="disabled")

    def _validate_inputs(self):
        valid = True
        for key, input_group in self.inputs.items():
            if not input_group.validate():
                valid = False
        return valid

    def _on_analyze(self):
        if not self._validate_inputs():
            return
            
        try:
            n = self.inputs['n'].get_value()
            p = self.inputs['p'].get_value()
            k = self.inputs['k'].get_value()
            ph = self.inputs['ph'].get_value()
            oc = self.inputs['oc'].get_value()
            moisture = self.inputs['moisture'].get_value()
            
            self.show_loading("Analyzing soil health...")
            
            result = self.analyzer.analyze(n, p, k, ph, oc, moisture)
            self._display_results(result)
            
            if self.prediction_service and self.user:
                input_data = {'N': n, 'P': p, 'K': k, 'pH': ph, 'OC': oc, 'Moisture': moisture}
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='soil_analysis',
                    input_data=input_data,
                    result=result
                )
            
            self.hide_loading()
            self.show_success("Analysis complete!")
            
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Analysis failed: {str(e)}")

    def _display_results(self, result):
        self.results_frame.pack(fill="both", expand=True)
        
        # Update Score
        score = result['health_score']
        grade = result['health_grade']
        
        color = ThemeManager.get_color("success")
        if score < 40:
            color = ThemeManager.get_color("error")
        elif score < 60:
            color = ThemeManager.get_color("warning")
            
        self.score_label.configure(text=f"{score}/100", text_color=color)
        self.grade_label.configure(text=f"Grade: {grade}", text_color=color)
        
        # Update Chart
        npk = result['npk_data']
        labels = ['Nitrogen', 'Phosphorus', 'Potassium']
        current_vals = [npk['nitrogen']['current'], npk['phosphorus']['current'], npk['potassium']['current']]
        self.chart_widget.create_bar_chart(
            current_vals, 
            labels, 
            "NPK Current Levels (mg/kg)", 
            colors=[color] * 3
        )
        
        # Update Text
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        
        text = "📝 SOIL HEALTH REPORT\n\n"
        
        if result['deficiencies']:
            text += "⚠️ DEFICIENCIES:\n"
            for d in result['deficiencies']:
                text += f"- {d['nutrient']}: {d['current']} (Optimal: {d['optimal_range']})\n"
            text += "\n"
            
        if result['excesses']:
            text += "⚠️ EXCESSES:\n"
            for e in result['excesses']:
                text += f"- {e['nutrient']}: {e['current']} (Optimal: {e['optimal_range']})\n"
            text += "\n"
            
        text += f"💧 pH Level: {result['ph_status']['value']} ({result['ph_status']['classification']})\n"
        text += f"🌱 Organic Carbon: {result['organic_carbon_status']['value']}% ({result['organic_carbon_status']['classification']})\n"
        text += f"💦 Moisture: {result['moisture_status']['value']}% ({result['moisture_status']['classification']})\n\n"
        
        text += "💡 RECOMMENDATIONS:\n"
        for s in result['suggestions']:
            text += f"• {s}\n"
            
        self.info_text.insert("1.0", text)
        self.info_text.configure(state="disabled")
