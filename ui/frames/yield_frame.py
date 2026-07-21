import customtkinter as ctk
from ui.base_frame import ContentFrame
from ui.components.input_group import InputGroup
from ui.components.chart_widget import ChartWidget
from ui.theme import ThemeManager
from ml.yield_pred.predict import YieldPredictor
import pandas as pd
import os

class YieldFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master, 
            title='📊 Yield Prediction', 
            subtitle='Estimate expected crop yield', 
            **kwargs
        )
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        self.predictor = YieldPredictor()
        
        self.crops = self._get_crops()
        self._setup_ui()
        
    def _get_crops(self):
        try:
            if self.predictor.encoder:
                return list(self.predictor.encoder.classes_)
            # Fallback
            return ["Rice", "Maize", "Cotton", "Wheat", "Chickpea", "Potato", "Sugarcane", "Banana", "Tomato", "Soybean"]
        except Exception:
            return ["Rice", "Wheat", "Maize", "Cotton"]
            
    def _setup_ui(self):
        # Input Card
        self.input_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.input_card.pack(fill="x", padx=10, pady=10)
        
        self.input_card.grid_columnconfigure((0, 1), weight=1)
        
        self.inputs = {}
        
        # Row 0
        self.inputs['crop'] = InputGroup(self.input_card, label="Crop", input_type="dropdown", options=self.crops, required=True)
        self.inputs['crop'].grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['farm_size'] = InputGroup(self.input_card, label="Farm Size (Acres)", input_type="number", required=True, min_val=0.1)
        self.inputs['farm_size'].grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Row 1
        self.inputs['rainfall'] = InputGroup(self.input_card, label="Rainfall (mm)", input_type="number", required=True, min_val=0)
        self.inputs['rainfall'].grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['temperature'] = InputGroup(self.input_card, label="Temperature (°C)", input_type="number", required=True)
        self.inputs['temperature'].grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Row 2
        self.inputs['humidity'] = InputGroup(self.input_card, label="Humidity (%)", input_type="number", required=True, min_val=0, max_val=100)
        self.inputs['humidity'].grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['n'] = InputGroup(self.input_card, label="Nitrogen (mg/kg)", input_type="number", required=True)
        self.inputs['n'].grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Row 3
        self.inputs['p'] = InputGroup(self.input_card, label="Phosphorus (mg/kg)", input_type="number", required=True)
        self.inputs['p'].grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.inputs['k'] = InputGroup(self.input_card, label="Potassium (mg/kg)", input_type="number", required=True)
        self.inputs['k'].grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # Predict Button
        self.predict_btn = ctk.CTkButton(
            self.content_area,
            text="Predict Yield",
            font=ThemeManager.get_font("button"),
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("primary_hover"),
            command=self._on_predict
        )
        self.predict_btn.pack(pady=20)
        
        # Results Section (Hidden initially)
        self.results_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        
        # Stats Card
        self.stats_card = ctk.CTkFrame(self.results_frame, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.stats_card.pack(fill="x", padx=10, pady=10)
        
        self.yield_val_label = ctk.CTkLabel(self.stats_card, text="", font=ctk.CTkFont(size=36, weight="bold"), text_color=ThemeManager.get_color("success"))
        self.yield_val_label.pack(pady=(20, 5))
        
        self.total_val_label = ctk.CTkLabel(self.stats_card, text="", font=ThemeManager.get_font("subheading"))
        self.total_val_label.pack(pady=5)
        
        self.conf_val_label = ctk.CTkLabel(self.stats_card, text="", font=ThemeManager.get_font("body"), text_color=ThemeManager.get_color("text_secondary"))
        self.conf_val_label.pack(pady=(5, 20))
        
        # Chart
        self.chart_widget = ChartWidget(self.results_frame)
        self.chart_widget.pack(fill="x", padx=10, pady=10)

    def _validate_inputs(self):
        valid = True
        for key, input_group in self.inputs.items():
            if not input_group.validate():
                valid = False
        return valid

    def _on_predict(self):
        if not self._validate_inputs():
            return
            
        try:
            crop = self.inputs['crop'].get_value()
            farm_size = self.inputs['farm_size'].get_value()
            rainfall = self.inputs['rainfall'].get_value()
            temp = self.inputs['temperature'].get_value()
            hum = self.inputs['humidity'].get_value()
            n = self.inputs['n'].get_value()
            p = self.inputs['p'].get_value()
            k = self.inputs['k'].get_value()
            
            self.show_loading("Predicting yield...")
            
            result = self.predictor.predict(crop, farm_size, rainfall, n, p, k, temp, hum)
            self._display_results(result, crop)
            
            if self.prediction_service and self.user:
                input_data = {
                    'Crop': crop, 'Farm_Size': farm_size, 'Rainfall': rainfall,
                    'Temperature': temp, 'Humidity': hum, 'N': n, 'P': p, 'K': k
                }
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='yield_prediction',
                    input_data=input_data,
                    result=result
                )
            
            self.hide_loading()
            self.show_success("Prediction complete!")
            
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Prediction failed: {str(e)}")

    def _display_results(self, result, crop):
        self.results_frame.pack(fill="both", expand=True)
        
        y_per_ha = result['predicted_yield_per_hectare']
        tot_prod = result['estimated_total_production_kg']
        conf = result['confidence'] * 100
        cat = result['yield_category']
        
        self.yield_val_label.configure(text=f"{y_per_ha:,.2f} kg/ha")
        self.total_val_label.configure(text=f"Total Production: {tot_prod:,.2f} kg ({cat} Yield)")
        self.conf_val_label.configure(text=f"Confidence Score: {conf:.1f}%")
        
        # Simple comparison chart (Predicted vs some arbitrary average for the crop category)
        avg_heuristic = 5000
        if cat == "High": avg_heuristic = 15000
        elif cat == "Low": avg_heuristic = 2000
        
        self.chart_widget.create_bar_chart(
            [y_per_ha, avg_heuristic], 
            ["Predicted", "Average"], 
            f"Yield Comparison for {crop} (kg/ha)", 
            colors=[ThemeManager.get_color("primary"), ThemeManager.get_color("text_secondary")]
        )
