import customtkinter as ctk
from ui.base_frame import ContentFrame
from ui.components.input_group import InputGroup
from ui.theme import ThemeManager
from ml.irrigation.recommend import IrrigationRecommender
from utils.constants import SEASONS, CROP_WATER_REQUIREMENTS

class IrrigationFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master, 
            title='💧 Irrigation Recommendation', 
            subtitle='Get personalized watering schedules and amounts',
            **kwargs
        )
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        self.recommender = IrrigationRecommender()
        
        self.crops = list(CROP_WATER_REQUIREMENTS.keys())
        if "default" in self.crops: self.crops.remove("default")
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Input Card
        self.input_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.input_card.pack(fill="x", padx=10, pady=10)
        
        self.input_card.grid_columnconfigure((0, 1), weight=1)
        
        self.inputs = {}
        
        self.inputs['crop'] = InputGroup(self.input_card, label="Crop", input_type="dropdown", options=self.crops, required=True)
        self.inputs['crop'].grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['season'] = InputGroup(self.input_card, label="Season", input_type="dropdown", options=SEASONS, required=True)
        self.inputs['season'].grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.inputs['moisture'] = InputGroup(self.input_card, label="Soil Moisture (%)", input_type="number", required=True, min_val=0, max_val=100)
        self.inputs['moisture'].grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['rainfall'] = InputGroup(self.input_card, label="Recent Rainfall (mm)", input_type="number", required=True, min_val=0)
        self.inputs['rainfall'].grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.inputs['temperature'] = InputGroup(self.input_card, label="Temperature (°C)", input_type="number", required=True)
        self.inputs['temperature'].grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Predict Button
        self.recommend_btn = ctk.CTkButton(
            self.content_area,
            text="Get Recommendation",
            font=ThemeManager.get_font("button"),
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("primary_hover"),
            command=self._on_recommend
        )
        self.recommend_btn.pack(pady=20)
        
        # Results Section
        self.results_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Info Card
        self.info_card = ctk.CTkFrame(self.results_frame, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.info_card.pack(fill="x", padx=10, pady=10)
        
        self.water_val_label = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=32, weight="bold"), text_color="#039BE5")
        self.water_val_label.pack(pady=(20, 5))
        
        self.method_label = ctk.CTkLabel(self.info_card, text="", font=ThemeManager.get_font("subheading"))
        self.method_label.pack(pady=5)
        
        self.freq_label = ctk.CTkLabel(self.info_card, text="", font=ThemeManager.get_font("body"))
        self.freq_label.pack(pady=5)
        
        self.total_label = ctk.CTkLabel(self.info_card, text="", font=ThemeManager.get_font("body"), text_color=ThemeManager.get_color("text_secondary"))
        self.total_label.pack(pady=(5, 15))
        
        # Water Gauge
        self.gauge_label = ctk.CTkLabel(self.info_card, text="Relative Water Need", font=ThemeManager.get_font("caption"))
        self.gauge_label.pack()
        
        self.gauge = ctk.CTkProgressBar(self.info_card, width=300, height=20, progress_color="#039BE5", fg_color=ThemeManager.get_color("surface"))
        self.gauge.pack(pady=(0, 20))
        self.gauge.set(0)
        
        # Textbox for tips
        self.tips_text = ctk.CTkTextbox(self.results_frame, height=150, font=ThemeManager.get_font("body"), fg_color=ThemeManager.get_color("card"))
        self.tips_text.pack(fill="x", padx=10, pady=10)
        self.tips_text.configure(state="disabled")

    def _validate_inputs(self):
        valid = True
        for key, input_group in self.inputs.items():
            if not input_group.validate():
                valid = False
        return valid

    def _on_recommend(self):
        if not self._validate_inputs():
            return
            
        try:
            crop = self.inputs['crop'].get_value()
            season = self.inputs['season'].get_value()
            moisture = self.inputs['moisture'].get_value()
            rainfall = self.inputs['rainfall'].get_value()
            temp = self.inputs['temperature'].get_value()
            
            self.show_loading("Generating schedule...")
            
            result = self.recommender.recommend(crop, season, moisture, rainfall, temp)
            self._display_results(result, crop)
            
            if self.prediction_service and self.user:
                input_data = {
                    'Crop': crop, 'Season': season, 'Moisture': moisture, 
                    'Rainfall': rainfall, 'Temperature': temp
                }
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='irrigation_recommendation',
                    input_data=input_data,
                    result=result
                )
            
            self.hide_loading()
            self.show_success("Recommendation complete!")
            
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Failed: {str(e)}")

    def _display_results(self, result, crop):
        self.results_frame.pack(fill="both", expand=True)
        
        req_mm = result['water_requirement_mm_per_day']
        self.water_val_label.configure(text=f"{req_mm} mm/day")
        self.method_label.configure(text=f"Method: {result['irrigation_method']}")
        self.freq_label.configure(text=f"Frequency: {result['irrigation_frequency']}")
        
        liters = result['daily_water_needed_liters_per_acre']
        month_liters = result['monthly_water_estimate_liters']
        self.total_label.configure(text=f"~{liters:,.0f} L/acre daily | ~{month_liters:,.0f} L/acre monthly")
        
        # Update gauge (max assumed ~15mm/day for display)
        val = min(1.0, req_mm / 15.0)
        self.gauge.set(val)
        
        # Update tips
        self.tips_text.configure(state="normal")
        self.tips_text.delete("1.0", "end")
        
        text = "🔧 ADJUSTMENTS APPLIED:\n"
        if result['adjustments']:
            for a in result['adjustments']:
                text += f"- {a}\n"
        else:
            text += "- None\n"
            
        text += "\n💡 EXPERT TIPS:\n"
        if result['tips']:
            for t in result['tips']:
                text += f"• {t}\n"
        else:
            text += "• Monitor soil moisture regularly.\n"
            
        self.tips_text.insert("1.0", text)
        self.tips_text.configure(state="disabled")
