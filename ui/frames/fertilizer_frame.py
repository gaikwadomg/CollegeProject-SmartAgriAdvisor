"""
AgriSense AI - Intelligent Fertilizer Recommendation UI Frame
===============================================================

Provides a clean, interactive CustomTkinter interface for soil-based
and crop-based fertilizer recommendations using Random Forest ML models.

Author: AgriSense AI Team
"""

import customtkinter as ctk

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from ui.components.result_panel import ResultPanel
from utils.constants import CROPS, SOIL_TYPES
from utils.logger import get_logger

logger = get_logger(__name__)


class FertilizerFrame(ContentFrame):
    """
    Interactive UI frame for AI/ML Fertilizer Recommendation.
    """

    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master,
            title='🧪 Fertilizer Recommendation',
            subtitle='Get AI-driven fertilizer suggestions tailored to your soil & crop requirements',
            **kwargs
        )
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        self.current_result = None

        self._setup_ui()

    def _setup_ui(self):
        # Top Card Container
        self.form_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.form_card.pack(fill='x', padx=10, pady=(0, 20))

        title_lbl = ctk.CTkLabel(
            self.form_card,
            text="🌾 Soil Composition & Crop Parameters",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        title_lbl.pack(pady=(15, 10), padx=15, anchor="w")

        inputs_grid = ctk.CTkFrame(self.form_card, fg_color="transparent")
        inputs_grid.pack(fill="x", padx=15, pady=(0, 15))
        inputs_grid.grid_columnconfigure((0, 1), weight=1)

        self.inputs = {}

        # Column 1
        self.inputs['crop'] = InputGroup(inputs_grid, label='Crop Type', input_type='dropdown', options=CROPS, required=True)
        self.inputs['crop'].grid(row=0, column=0, padx=10, pady=8, sticky='ew')

        self.inputs['soil_type'] = InputGroup(inputs_grid, label='Soil Type', input_type='dropdown', options=SOIL_TYPES, required=True)
        self.inputs['soil_type'].grid(row=0, column=1, padx=10, pady=8, sticky='ew')

        self.inputs['temperature'] = InputGroup(inputs_grid, label='Temperature (°C)', placeholder='e.g., 26.5', input_type='number', required=True)
        self.inputs['temperature'].grid(row=1, column=0, padx=10, pady=8, sticky='ew')

        self.inputs['humidity'] = InputGroup(inputs_grid, label='Humidity (%)', placeholder='e.g., 65', input_type='number', required=True)
        self.inputs['humidity'].grid(row=1, column=1, padx=10, pady=8, sticky='ew')

        # Column 2
        self.inputs['moisture'] = InputGroup(inputs_grid, label='Soil Moisture (%)', placeholder='e.g., 42', input_type='number', required=True)
        self.inputs['moisture'].grid(row=2, column=0, padx=10, pady=8, sticky='ew')

        self.inputs['N'] = InputGroup(inputs_grid, label='Nitrogen (N) mg/kg', placeholder='e.g., 45', input_type='number', required=True)
        self.inputs['N'].grid(row=2, column=1, padx=10, pady=8, sticky='ew')

        self.inputs['P'] = InputGroup(inputs_grid, label='Phosphorus (P) mg/kg', placeholder='e.g., 22', input_type='number', required=True)
        self.inputs['P'].grid(row=3, column=0, padx=10, pady=8, sticky='ew')

        self.inputs['K'] = InputGroup(inputs_grid, label='Potassium (K) mg/kg', placeholder='e.g., 30', input_type='number', required=True)
        self.inputs['K'].grid(row=3, column=1, padx=10, pady=8, sticky='ew')

        # Recommend Action Button
        self.predict_btn = ctk.CTkButton(
            self.form_card,
            text="✨ Get AI Fertilizer Recommendation",
            font=ThemeManager.get_font("subheading"),
            height=45,
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            command=self.on_recommend
        )
        self.predict_btn.pack(padx=25, pady=(10, 20), fill="x")

        # Results Display Panel
        self.result_panel = ResultPanel(self.content_area, title="AI Recommendation Results")
        self.result_panel.pack(fill='x', padx=10, pady=(0, 20))
        self.result_panel.pack_forget()

        # Save Button
        self.save_btn = ctk.CTkButton(
            self.content_area,
            text="💾 Save Recommendation to History",
            font=ThemeManager.get_font("subheading"),
            height=40,
            fg_color=ThemeManager.get_color("surface"),
            hover_color=ThemeManager.get_color("card"),
            text_color=ThemeManager.get_color("text"),
            command=self.on_save,
            state="disabled"
        )
        self.save_btn.pack(pady=(0, 20))
        self.save_btn.pack_forget()

    def on_recommend(self):
        """Execute AI fertilizer recommendation."""
        # Validate fields
        all_valid = True
        for key, input_grp in self.inputs.items():
            if not input_grp.validate():
                all_valid = False

        if not all_valid:
            self.show_error("Please fill in all required fields with valid values.")
            return

        try:
            self.predict_btn.configure(text="Processing AI Recommendation...", state="disabled")
            self.update_idletasks()

            crop_val = self.inputs['crop'].get_value()
            soil_val = self.inputs['soil_type'].get_value()
            temp_val = float(self.inputs['temperature'].get_value() or 25)
            hum_val = float(self.inputs['humidity'].get_value() or 60)
            moist_val = float(self.inputs['moisture'].get_value() or 40)
            n_val = float(self.inputs['N'].get_value() or 40)
            p_val = float(self.inputs['P'].get_value() or 20)
            k_val = float(self.inputs['K'].get_value() or 20)

            input_data = {
                'crop_type': crop_val,
                'soil_type': soil_val,
                'temperature': temp_val,
                'humidity': hum_val,
                'moisture': moist_val,
                'nitrogen': n_val,
                'phosphorus': p_val,
                'potassium': k_val
            }

            from ml.fertilizer.predict import FertilizerPredictor
            predictor = FertilizerPredictor()
            result_data = predictor.predict(**input_data)

            self.current_result = {
                'input': input_data,
                'output': result_data
            }

            # Render Results Panel
            self.result_panel.clear()

            conf_pct = f"{int(result_data.get('confidence', 0.9) * 100)}%"
            fert_display = f"🧪 {result_data.get('fertilizer', 'Urea')} ({result_data.get('nutrient_composition', 'Balanced')})"

            results_dict = {
                "Recommended Fertilizer": fert_display,
                "ML Model Confidence": conf_pct,
                "Application Dosage": result_data.get('quantity', '45 kg / acre'),
                "Nutrient Content": result_data.get('nutrient_composition', 'N/A'),
                "Organic Alternative": f"🌿 {result_data.get('organic_alternative', 'Compost')}",
                "Application Schedule": result_data.get('application_advice', 'Apply in split doses.'),
                "Safety Instructions": result_data.get('safety_tips', 'Avoid direct leaf contact.')
            }

            self.result_panel.set_results(results_dict)
            self.result_panel.pack(fill='x', padx=10, pady=(0, 20))

            self.save_btn.pack(pady=(0, 20))
            self.save_btn.configure(state="normal")
            self.show_success("Fertilizer recommendation calculated successfully!")

        except Exception as e:
            logger.error(f"Error in fertilizer recommendation: {e}", exc_info=True)
            self.show_error(f"Failed to calculate recommendation: {e}")
        finally:
            self.predict_btn.configure(text="✨ Get AI Fertilizer Recommendation", state="normal")

    def on_save(self):
        """Save prediction to database."""
        if self.prediction_service and self.current_result:
            try:
                conf = float(self.current_result['output'].get('confidence', 0.9))
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='fertilizer_recommendation',
                    input_data=self.current_result['input'],
                    result_data=self.current_result['output'],
                    confidence=conf
                )
                self.show_success("Fertilizer recommendation saved to database history!")
                self.save_btn.configure(state="disabled")
            except Exception as e:
                logger.error(f"Failed to save recommendation: {e}")
                self.show_error(f"Failed to save record: {e}")
