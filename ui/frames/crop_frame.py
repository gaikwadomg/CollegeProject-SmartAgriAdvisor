import customtkinter as ctk
from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from ui.components.result_panel import ResultPanel
from utils.constants import CROPS, SOIL_TYPES, SEASONS
from utils.validators import validate_crop_inputs, validate_required
from utils.logger import get_logger

logger = get_logger(__name__)

class CropFrame(ContentFrame):
    """
    Crop recommendation UI frame.
    """
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master, 
            db=db, 
            user=user, 
            title='🌾 Crop Recommendation', 
            subtitle='Find the best crop for your conditions', 
            **kwargs
        )
        self.prediction_service = prediction_service
        self.theme = ThemeManager.get_theme()
        
        self._setup_ui()

    def _setup_ui(self):
        # Form Container
        self.form_card = ctk.CTkFrame(self, fg_color=self.theme.get('card_bg', '#ffffff'), corner_radius=10)
        self.form_card.pack(fill='x', padx=20, pady=20)
        
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_columnconfigure(1, weight=1)

        self.inputs = {}
        
        # 1. Nitrogen
        self.inputs['N'] = InputGroup(
            self.form_card, label='Nitrogen (N)', placeholder='e.g., 50', 
            input_type='number', tooltip_text='Soil nitrogen content (mg/kg)'
        )
        self.inputs['N'].grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        # 2. Phosphorus
        self.inputs['P'] = InputGroup(self.form_card, label='Phosphorus (P)', placeholder='e.g., 40', input_type='number')
        self.inputs['P'].grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        # 3. Potassium
        self.inputs['K'] = InputGroup(self.form_card, label='Potassium (K)', placeholder='e.g., 35', input_type='number')
        self.inputs['K'].grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        
        # 4. Temperature
        self.inputs['temperature'] = InputGroup(self.form_card, label='Temperature (°C)', placeholder='e.g., 25', input_type='number')
        self.inputs['temperature'].grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        # 5. Humidity
        self.inputs['humidity'] = InputGroup(self.form_card, label='Humidity (%)', placeholder='e.g., 70', input_type='number')
        self.inputs['humidity'].grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        
        # 6. pH
        self.inputs['ph'] = InputGroup(self.form_card, label='pH', placeholder='e.g., 6.5', input_type='number')
        self.inputs['ph'].grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        
        # 7. Rainfall
        self.inputs['rainfall'] = InputGroup(self.form_card, label='Rainfall (mm)', placeholder='e.g., 200', input_type='number')
        self.inputs['rainfall'].grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        # Predict Button
        self.predict_btn = ctk.CTkButton(
            self.form_card, 
            text="Predict",
            fg_color=self.theme.get('success', '#28a745'),
            hover_color=self.theme.get('success_hover', '#218838'),
            command=self.on_predict
        )
        self.predict_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=20, sticky='ew')

        # Results Panel (initially hidden)
        self.result_panel = ResultPanel(self, title="Prediction Results")
        
        # Save Button
        self.save_btn = ctk.CTkButton(
            self,
            text="Save to Database",
            command=self.on_save,
            state="disabled"
        )
        
        self.current_result = None

    def on_predict(self):
        try:
            self.predict_btn.configure(text="Predicting...", state="disabled")
            self.update_idletasks()
            
            # Fetch and validate inputs
            try:
                n = float(self.inputs['N'].get_value() or 0)
                p = float(self.inputs['P'].get_value() or 0)
                k = float(self.inputs['K'].get_value() or 0)
                temp = float(self.inputs['temperature'].get_value() or 0)
                humidity = float(self.inputs['humidity'].get_value() or 0)
                ph = float(self.inputs['ph'].get_value() or 0)
                rainfall = float(self.inputs['rainfall'].get_value() or 0)
            except ValueError:
                self.show_error("Please enter valid numeric values for all fields.")
                return

            if not validate_crop_inputs(n, p, k, temp, humidity, ph, rainfall):
                self.show_error("Invalid input values. Please check.")
                return

            try:
                from ml.crop.predict import CropPredictor
                predictor = CropPredictor()
                result = predictor.predict(n, p, k, temp, humidity, ph, rainfall)
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                self.show_error(f'Prediction failed: {e}')
                return
                
            self.current_result = {
                'input': {'N': n, 'P': p, 'K': k, 'temperature': temp, 'humidity': humidity, 'ph': ph, 'rainfall': rainfall},
                'output': result
            }
            
            # Display results
            self.result_panel.pack(fill='x', padx=20, pady=10)
            self.result_panel.clear()
            
            recs = result.get('recommendations', [])
            for idx, rec in enumerate(recs[:3]):
                confidence_str = f"{rec.get('confidence', 0)*100:.1f}%"
                self.result_panel.add_row(f"#{idx+1} {rec.get('crop', 'Unknown').capitalize()}", confidence_str)
            
            top_crop = recs[0].get('crop', 'Unknown').capitalize() if recs else "Unknown"
            self.result_panel.add_row("Growing Tips", f"Ensure optimal moisture and nutrient balance for {top_crop}.")
            
            self.save_btn.pack(pady=10)
            self.save_btn.configure(state="normal")
                
        finally:
            self.predict_btn.configure(text="Predict", state="normal")
            
    def on_save(self):
        if self.prediction_service and self.current_result:
            try:
                recs = self.current_result['output'].get('recommendations', [])
                top_confidence = recs[0].get('confidence', 0.0) if recs else 0.0
                
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='crop_recommendation',
                    input_data=self.current_result['input'],
                    result_data=self.current_result['output'],
                    confidence=top_confidence
                )
                self.show_success("Prediction saved successfully!")
                self.save_btn.configure(state="disabled")
            except Exception as e:
                logger.error(f"Failed to save prediction: {e}")
                self.show_error(f"Failed to save: {e}")
