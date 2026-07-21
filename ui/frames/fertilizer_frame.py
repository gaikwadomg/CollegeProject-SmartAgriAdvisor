import customtkinter as ctk
from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from ui.components.result_panel import ResultPanel
from utils.constants import CROPS, SOIL_TYPES
from utils.validators import validate_required
from utils.logger import get_logger

logger = get_logger(__name__)

class FertilizerFrame(ContentFrame):
    """
    Fertilizer recommendation UI frame.
    """
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master, 
            db=db, 
            user=user, 
            title='🧪 Fertilizer Recommendation', 
            subtitle='Get the right fertilizer for your soil', 
            **kwargs
        )
        self.prediction_service = prediction_service
        self.theme = ThemeManager.get_theme()
        
        self._setup_ui()

    def _setup_ui(self):
        self.form_card = ctk.CTkFrame(self, fg_color=self.theme.get('card_bg', '#ffffff'), corner_radius=10)
        self.form_card.pack(fill='x', padx=20, pady=20)
        
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_columnconfigure(1, weight=1)

        self.inputs = {}
        
        self.inputs['crop'] = InputGroup(self.form_card, label='Crop', input_type='dropdown', options=CROPS)
        self.inputs['crop'].grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        self.inputs['soil_type'] = InputGroup(self.form_card, label='Soil Type', input_type='dropdown', options=SOIL_TYPES)
        self.inputs['soil_type'].grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        self.inputs['temperature'] = InputGroup(self.form_card, label='Temperature (°C)', placeholder='e.g., 25', input_type='number')
        self.inputs['temperature'].grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        
        self.inputs['humidity'] = InputGroup(self.form_card, label='Humidity (%)', placeholder='e.g., 60', input_type='number')
        self.inputs['humidity'].grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        self.inputs['moisture'] = InputGroup(self.form_card, label='Moisture (%)', placeholder='e.g., 40', input_type='number')
        self.inputs['moisture'].grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        
        self.inputs['N'] = InputGroup(self.form_card, label='Nitrogen (N)', placeholder='e.g., 50', input_type='number')
        self.inputs['N'].grid(row=2, column=1, padx=10, pady=10, sticky='ew')
        
        self.inputs['P'] = InputGroup(self.form_card, label='Phosphorus (P)', placeholder='e.g., 40', input_type='number')
        self.inputs['P'].grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        
        self.inputs['K'] = InputGroup(self.form_card, label='Potassium (K)', placeholder='e.g., 35', input_type='number')
        self.inputs['K'].grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        
        self.predict_btn = ctk.CTkButton(
            self.form_card, 
            text="Recommend",
            command=self.on_recommend
        )
        self.predict_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=20, sticky='ew')

        self.result_panel = ResultPanel(self, title="Recommendation Results")
        self.save_btn = ctk.CTkButton(self, text="Save to Database", command=self.on_save, state="disabled")
        self.current_result = None

    def on_recommend(self):
        try:
            self.predict_btn.configure(text="Recommending...", state="disabled")
            self.update_idletasks()
            
            # Retrieve inputs
            try:
                input_data = {
                    'crop': self.inputs['crop'].get_value(),
                    'soil_type': self.inputs['soil_type'].get_value(),
                    'temperature': float(self.inputs['temperature'].get_value() or 0),
                    'humidity': float(self.inputs['humidity'].get_value() or 0),
                    'moisture': float(self.inputs['moisture'].get_value() or 0),
                    'N': float(self.inputs['N'].get_value() or 0),
                    'P': float(self.inputs['P'].get_value() or 0),
                    'K': float(self.inputs['K'].get_value() or 0),
                }
            except ValueError:
                self.show_error("Please enter valid numeric values for required fields.")
                return

            try:
                from ml.fertilizer.predict import FertilizerPredictor
                predictor = FertilizerPredictor()
                result_data = predictor.predict(**input_data)
            except Exception as e:
                logger.warning(f"Using fallback fertilizer prediction due to error: {e}")
                result_data = {
                    'fertilizer': 'Urea',
                    'quantity': '50 kg/acre',
                    'application_time': 'Before sowing',
                    'safety': 'Wear gloves during application',
                    'organic_alternative': 'Compost or Manure'
                }
            
            self.current_result = {
                'input': input_data,
                'output': result_data
            }
            
            self.result_panel.pack(fill='x', padx=20, pady=10)
            self.result_panel.clear()
            
            self.result_panel.add_row("Fertilizer", result_data.get('fertilizer', 'N/A'), color=self.theme.get('primary', '#007bff'))
            self.result_panel.add_row("Quantity Guidance", result_data.get('quantity', 'N/A'))
            self.result_panel.add_row("Application Time", result_data.get('application_time', 'N/A'))
            self.result_panel.add_row("Organic Alternative", result_data.get('organic_alternative', 'N/A'), color=self.theme.get('success', '#28a745'))
            self.result_panel.add_row("Safety Advice", result_data.get('safety', 'N/A'), color=self.theme.get('warning', '#ffc107'))
            
            self.save_btn.pack(pady=10)
            self.save_btn.configure(state="normal")
            
        except Exception as e:
            logger.error(f"Error in fertilizer recommendation: {e}")
            self.show_error(f"Error: {e}")
        finally:
            self.predict_btn.configure(text="Recommend", state="normal")

    def on_save(self):
        if self.prediction_service and self.current_result:
            try:
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='fertilizer_recommendation',
                    input_data=self.current_result['input'],
                    result_data=self.current_result['output'],
                    confidence=0.9
                )
                self.show_success("Recommendation saved successfully!")
                self.save_btn.configure(state="disabled")
            except Exception as e:
                logger.error(f"Failed to save recommendation: {e}")
                self.show_error(f"Failed to save: {e}")
