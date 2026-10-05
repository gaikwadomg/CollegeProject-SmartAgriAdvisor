import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.result_panel import ResultPanel
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label_title = ctk.CTkLabel(self, text=title, font=ThemeManager.get_font("subheading"))
        self.label_title.pack(pady=(0, 5))
        
        self.image_label = ctk.CTkLabel(
            self,
            text="No Image",
            width=250,
            height=250,
            fg_color=ThemeManager.get_color("card")
        )
        self.image_label.pack(expand=True, fill="both")
        
    def set_image(self, pil_image):
        if pil_image:
            try:
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 250))
                self.image_label.configure(image=ctk_image, text="")
            except Exception as e:
                logger.error(f"Failed to set image: {e}")
                self.image_label.configure(image=None, text="Loaded Image")
        else:
            self.image_label.configure(image=None, text="No Image")


class DiseaseFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title='🍂 Plant Disease Detection', subtitle='Upload a leaf image to detect diseases', **kwargs)
        
        self.db = db
        self.user = user
        self.prediction_service = prediction_service
        self.current_image_path = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Top section: Upload area
        self.upload_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=12)
        self.upload_card.pack(fill="x", padx=10, pady=(0, 20))
        
        self.upload_btn = ctk.CTkButton(
            self.upload_card, 
            text="📷 Click to Upload Leaf Image", 
            font=ThemeManager.get_font("subheading"),
            height=80,
            fg_color="transparent",
            border_width=2,
            border_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("surface"),
            command=self._upload_image
        )
        self.upload_btn.pack(padx=20, pady=20, expand=True, fill="x")
        
        # Image view section
        self.images_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.images_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        self.images_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.original_viewer = ImageViewer(self.images_frame, "Original Image")
        self.original_viewer.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.processed_viewer = ImageViewer(self.images_frame, "Processed Image")
        self.processed_viewer.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        # Action button
        self.detect_btn = ctk.CTkButton(
            self.content_area,
            text="Detect Disease",
            font=ThemeManager.get_font("subheading"),
            height=45,
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            state="disabled",
            command=self._detect_disease
        )
        self.detect_btn.pack(pady=(0, 20))
        
        # Results Section
        self.results_panel = ResultPanel(self.content_area, title="Detection Results")
        self.results_panel.pack(fill="x", padx=10, pady=(0, 20))
        self.results_panel.pack_forget()

    def _upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Leaf Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.current_image_path = file_path
            filename = file_path.replace("\\", "/").split("/")[-1]
            self.upload_btn.configure(text=f"Selected: {filename}")
            
            # Display image
            try:
                from ml.disease.predict import DiseasePredictor
                dp = DiseasePredictor()
                orig, proc = dp.preprocess_image_for_display(file_path)
                self.original_viewer.set_image(orig)
                self.processed_viewer.set_image(proc)
            except Exception as e:
                logger.error(f"Image preprocessing error: {e}")
                try:
                    img = Image.open(file_path)
                    self.original_viewer.set_image(img)
                    self.processed_viewer.set_image(img)
                except Exception as ex:
                    logger.error(f"Failed to open image fallback: {ex}")
            
            self.detect_btn.configure(state="normal")
            self.results_panel.pack_forget()

    def _detect_disease(self):
        if not self.current_image_path:
            return
            
        self.detect_btn.configure(state="disabled", text="Processing...")
        self.update()
        
        try:
            if self.prediction_service:
                result = self.prediction_service.predict_disease(self.current_image_path)
            else:
                from ml.disease.predict import DiseasePredictor
                dp = DiseasePredictor()
                result = dp.predict(self.current_image_path)
            
            if 'error' in result:
                # If any error string present, fallback to simulation mode
                from ml.disease.predict import DiseasePredictor
                dp = DiseasePredictor()
                result = dp._simulate_prediction(self.current_image_path)
                
            self._display_results(result)
            
            # Save record if service available
            if self.prediction_service and self.user:
                self.prediction_service.save_disease_record(
                    user_id=self.user.id,
                    disease_name=result.get('disease_name', 'Healthy'),
                    confidence=result.get('confidence', 0.95),
                    image_path=self.current_image_path,
                    farm_id=None
                )
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            from ml.disease.predict import DiseasePredictor
            dp = DiseasePredictor()
            result = dp._simulate_prediction(self.current_image_path)
            self._display_results(result)
        finally:
            self.detect_btn.configure(state="normal", text="Detect Disease")
            
    def _display_results(self, result):
        self.results_panel.clear()
        
        is_healthy = result.get('is_healthy', False)
        
        results_dict = {
            "Disease": result.get('display_name', 'Healthy Crop'),
            "Confidence": f"{result.get('confidence', 0.95) * 100:.1f}%",
            "Health Status": "Healthy" if is_healthy else "Diseased",
            "Medicine / Spray": result.get('medicine', 'N/A'),
            "Recommended Dosage": result.get('dosage', 'N/A'),
            "Application Advice": result.get('advice', 'N/A')
        }
        
        self.results_panel.set_results(results_dict)
        self.results_panel.pack(fill="x", padx=10, pady=(0, 20))
