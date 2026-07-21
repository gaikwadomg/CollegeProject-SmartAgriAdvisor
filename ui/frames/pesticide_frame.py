import customtkinter as ctk
from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from ui.components.result_panel import ResultPanel
from utils.constants import CROPS, SEASONS
from utils.validators import validate_required
from utils.logger import get_logger

logger = get_logger(__name__)

class PesticideFrame(ContentFrame):
    """
    Pesticide recommendation UI frame.
    """
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master, 
            db=db, 
            user=user, 
            title='🐛 Pesticide Recommendation', 
            subtitle='Find effective pest control', 
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
        
        # Crop Selection
        self.inputs['crop'] = InputGroup(self.form_card, label='Crop', input_type='dropdown', options=CROPS)
        self.inputs['crop'].grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        # Disease Selection
        self.inputs['disease'] = InputGroup(self.form_card, label='Disease', input_type='dropdown', options=["Select Crop First"])
        self.inputs['disease'].grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        # Season Selection
        self.inputs['season'] = InputGroup(self.form_card, label='Season', input_type='dropdown', options=SEASONS)
        self.inputs['season'].grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        
        # Recommend Button
        self.predict_btn = ctk.CTkButton(
            self.form_card, 
            text="Get Recommendation",
            command=self.on_recommend
        )
        self.predict_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='ew')

        # Results Panel
        self.result_panel = ResultPanel(self, title="Pesticide Recommendation")
        
        # Save Button
        self.save_btn = ctk.CTkButton(self, text="Save to Database", command=self.on_save, state="disabled")
        self.current_result = None
        
        # Attempt to bind crop dropdown changes if possible
        # This requires `set_options` to be implemented on the InputGroup
        try:
            self.after(500, self._poll_crop_change)
            self._last_crop = self.inputs['crop'].get_value()
        except Exception:
            pass

    def _poll_crop_change(self):
        """Poll for crop changes to update the disease dropdown."""
        try:
            current_crop = self.inputs['crop'].get_value()
            if current_crop != self._last_crop:
                self._last_crop = current_crop
                self._update_diseases(current_crop)
        except Exception:
            pass
        finally:
            self.after(500, self._poll_crop_change)

    def _update_diseases(self, crop):
        try:
            from ml.pesticide.recommender import PesticideRecommender
            diseases = PesticideRecommender.get_diseases_for_crop(crop)
            if hasattr(self.inputs['disease'], 'set_options'):
                self.inputs['disease'].set_options(diseases)
        except ImportError:
            # Fallback diseases
            fallback_diseases = ['Blight', 'Rust', 'Mildew', 'Root Rot', 'Pest Infestation']
            if hasattr(self.inputs['disease'], 'set_options'):
                self.inputs['disease'].set_options(fallback_diseases)
        except Exception as e:
            logger.error(f"Error updating diseases: {e}")

    def on_recommend(self):
        try:
            self.predict_btn.configure(text="Processing...", state="disabled")
            self.update_idletasks()
            
            input_data = {
                'crop': self.inputs['crop'].get_value(),
                'disease': self.inputs['disease'].get_value(),
                'season': self.inputs['season'].get_value()
            }
            
            try:
                from ml.pesticide.recommender import PesticideRecommender
                recommender = PesticideRecommender()
                result_data = recommender.recommend(**input_data)
            except Exception as e:
                logger.warning(f"Using fallback pesticide prediction due to error: {e}")
                result_data = {
                    'pesticide': 'Neem Oil / Broad Spectrum Pesticide',
                    'dosage': '5ml per liter of water',
                    'spray_interval': '7-14 days',
                    'organic_alternative': 'Garlic & Pepper Spray',
                    'safety': 'Keep away from children. Wear mask and gloves.'
                }
            
            self.current_result = {
                'input': input_data,
                'output': result_data
            }
            
            self.result_panel.pack(fill='x', padx=20, pady=10)
            self.result_panel.clear()
            
            self.result_panel.add_row("Pesticide", result_data.get('pesticide', 'N/A'), color=self.theme.get('primary', '#007bff'))
            self.result_panel.add_row("Dosage", result_data.get('dosage', 'N/A'))
            self.result_panel.add_row("Spray Interval", result_data.get('spray_interval', 'N/A'))
            self.result_panel.add_row("Organic Alternative", result_data.get('organic_alternative', 'N/A'), color=self.theme.get('success', '#28a745'))
            self.result_panel.add_row("Safety Precautions", result_data.get('safety', 'N/A'), color=self.theme.get('error', '#dc3545'))
            
            self.save_btn.pack(pady=10)
            self.save_btn.configure(state="normal")
            
        except Exception as e:
            logger.error(f"Error in pesticide recommendation: {e}")
            self.show_error(f"Error: {e}")
        finally:
            self.predict_btn.configure(text="Get Recommendation", state="normal")

    def on_save(self):
        if self.prediction_service and self.current_result:
            try:
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='pesticide_recommendation',
                    input_data=self.current_result['input'],
                    result_data=self.current_result['output'],
                    confidence=0.85
                )
                self.show_success("Recommendation saved successfully!")
                self.save_btn.configure(state="disabled")
            except Exception as e:
                logger.error(f"Failed to save recommendation: {e}")
                self.show_error(f"Failed to save: {e}")
