"""
AgriSense AI - Intelligent Pesticide Recommendation UI Frame
==============================================================

Provides a dynamic CustomTkinter interface for pest & disease control
recommendations using Random Forest Machine Learning and Expert Knowledge Base.

Features:
- Dynamic crop-to-disease dropdown filtering
- ML prediction confidence & active ingredient analysis
- Organic/bio-pesticide alternative suggestions
- Safety precautions and pre-harvest interval guidance

Author: AgriSense AI Team
"""

import customtkinter as ctk

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from ui.components.result_panel import ResultPanel
from utils.constants import SEASONS
from utils.logger import get_logger

logger = get_logger(__name__)


class PesticideFrame(ContentFrame):
    """
    Interactive UI frame for AI/ML Pesticide Recommendation.
    """

    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(
            master,
            title='🐛 Pesticide & Pest Control Recommendation',
            subtitle='AI-powered pest & disease management with active ingredient guidance & organic alternatives',
            **kwargs
        )
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        self.current_result = None

        self._load_recommender()
        self._setup_ui()

    def _load_recommender(self):
        try:
            from ml.pesticide.recommend import PesticideRecommender
            self.recommender = PesticideRecommender()
            self.available_crops = self.recommender.get_all_crops()
        except Exception as e:
            logger.error(f"Failed to load PesticideRecommender: {e}")
            self.recommender = None
            self.available_crops = ["Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato", "Apple", "Grape", "Sugarcane", "Banana"]

    def _setup_ui(self):
        # Form Container
        self.form_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.form_card.pack(fill='x', padx=10, pady=(0, 20))

        title_lbl = ctk.CTkLabel(
            self.form_card,
            text="🌿 Crop & Disease Identification",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        title_lbl.pack(pady=(15, 10), padx=15, anchor="w")

        inputs_grid = ctk.CTkFrame(self.form_card, fg_color="transparent")
        inputs_grid.pack(fill="x", padx=15, pady=(0, 15))
        inputs_grid.grid_columnconfigure((0, 1), weight=1)

        self.inputs = {}

        # Crop Selection
        self.inputs['crop'] = InputGroup(
            inputs_grid,
            label='Crop Name',
            input_type='dropdown',
            options=self.available_crops,
            required=True
        )
        self.inputs['crop'].grid(row=0, column=0, padx=10, pady=8, sticky='ew')

        # Disease Selection (Filtered dynamically based on Crop)
        initial_crop = self.available_crops[0] if self.available_crops else "Rice"
        initial_diseases = self.recommender.get_diseases_for_crop(initial_crop) if self.recommender else ["Select Crop"]

        self.inputs['disease'] = InputGroup(
            inputs_grid,
            label='Disease / Pest Symptom',
            input_type='dropdown',
            options=initial_diseases,
            required=True
        )
        self.inputs['disease'].grid(row=0, column=1, padx=10, pady=8, sticky='ew')

        # Season
        self.inputs['season'] = InputGroup(inputs_grid, label='Season', input_type='dropdown', options=SEASONS)
        self.inputs['season'].grid(row=1, column=0, padx=10, pady=8, sticky='ew')

        # Temperature
        self.inputs['temperature'] = InputGroup(inputs_grid, label='Temperature (°C)', placeholder='e.g., 28', input_type='number')
        self.inputs['temperature'].grid(row=1, column=1, padx=10, pady=8, sticky='ew')

        # Humidity
        self.inputs['humidity'] = InputGroup(inputs_grid, label='Humidity (%)', placeholder='e.g., 70', input_type='number')
        self.inputs['humidity'].grid(row=2, column=0, columnspan=2, padx=10, pady=8, sticky='ew')

        # Bind Crop Dropdown change to update Disease Dropdown
        if isinstance(self.inputs['crop'].input, ctk.CTkComboBox):
            self.inputs['crop'].input.configure(command=self._on_crop_changed)

        # Recommend Action Button
        self.predict_btn = ctk.CTkButton(
            self.form_card,
            text="✨ Get AI Pesticide Recommendation",
            font=ThemeManager.get_font("subheading"),
            height=45,
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            command=self.on_recommend
        )
        self.predict_btn.pack(padx=25, pady=(10, 20), fill="x")

        # Results Display Panel
        self.result_panel = ResultPanel(self.content_area, title="AI Pesticide Recommendation")
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

    def _on_crop_changed(self, selected_crop):
        """Update disease dropdown when selected crop changes."""
        if self.recommender:
            diseases = self.recommender.get_diseases_for_crop(selected_crop)
            self.inputs['disease'].set_options(diseases)

    def on_recommend(self):
        """Execute ML pesticide recommendation."""
        crop_val = self.inputs['crop'].get_value()
        disease_val = self.inputs['disease'].get_value()
        season_val = self.inputs['season'].get_value()
        temp_val = float(self.inputs['temperature'].get_value() or 28)
        hum_val = float(self.inputs['humidity'].get_value() or 65)

        if not crop_val or not disease_val:
            self.show_error("Please select a Crop and Disease/Pest symptom.")
            return

        try:
            self.predict_btn.configure(text="Processing AI Recommendation...", state="disabled")
            self.update_idletasks()

            input_data = {
                'crop': crop_val,
                'disease': disease_val,
                'season': season_val,
                'temperature': temp_val,
                'humidity': hum_val
            }

            if not self.recommender:
                from ml.pesticide.recommend import PesticideRecommender
                self.recommender = PesticideRecommender()

            result_data = self.recommender.recommend(**input_data)

            self.current_result = {
                'input': input_data,
                'output': result_data
            }

            # Render Results Panel
            self.result_panel.clear()

            conf_val = result_data.get('confidence', 0.85)
            conf_pct = f"{int(conf_val * 100)}%"

            precautions = result_data.get('safety_precautions', [])
            precautions_str = " | ".join(precautions) if isinstance(precautions, list) else str(precautions)

            results_dict = {
                "Target Crop & Disease": f"{crop_val} – {disease_val}",
                "Recommended Pesticide": f"🐛 {result_data.get('pesticide', 'Mancozeb 75% WP')}",
                "Active Ingredient": result_data.get('active_ingredient', 'N/A'),
                "ML Model Confidence": conf_pct,
                "Spray Dosage": result_data.get('dosage', '2.0 g/L water'),
                "Spray Interval / Schedule": result_data.get('spray_interval', '10-14 days'),
                "Organic / Bio Alternative": f"🌿 {result_data.get('organic_alternative', 'Neem Oil 10,000 PPM')}",
                "Safety & Pre-Harvest Advice": f"⚠️ {precautions_str}"
            }

            self.result_panel.set_results(results_dict)
            self.result_panel.pack(fill='x', padx=10, pady=(0, 20))

            self.save_btn.pack(pady=(0, 20))
            self.save_btn.configure(state="normal")
            self.show_success("Pesticide recommendation generated successfully!")

        except Exception as e:
            logger.error(f"Error in pesticide recommendation: {e}", exc_info=True)
            self.show_error(f"Failed to generate recommendation: {e}")
        finally:
            self.predict_btn.configure(text="✨ Get AI Pesticide Recommendation", state="normal")

    def on_save(self):
        """Save prediction to database."""
        if self.prediction_service and self.current_result:
            try:
                conf = float(self.current_result['output'].get('confidence', 0.85))
                self.prediction_service.save_prediction(
                    user_id=self.user.id,
                    prediction_type='pesticide_recommendation',
                    input_data=self.current_result['input'],
                    result_data=self.current_result['output'],
                    confidence=conf
                )
                self.show_success("Pesticide recommendation saved to database history!")
                self.save_btn.configure(state="disabled")
            except Exception as e:
                logger.error(f"Failed to save recommendation: {e}")
                self.show_error(f"Failed to save record: {e}")
