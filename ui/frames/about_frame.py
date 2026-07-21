import customtkinter as ctk

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager


class AboutFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title="ℹ️ About AgriSense AI", subtitle="System overview and technology stack", **kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        # Header Section
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        logo_lbl = ctk.CTkLabel(header_frame, text="🌱", font=("Segoe UI", 56))
        logo_lbl.pack(pady=(5, 5))
        
        title_lbl = ctk.CTkLabel(header_frame, text="AgriSense AI v1.0.0", font=ThemeManager.get_font("heading"), text_color=ThemeManager.get_color("primary"))
        title_lbl.pack()
        
        subtitle_lbl = ctk.CTkLabel(
            header_frame, 
            text="Intelligent Agriculture Decision Support System", 
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        subtitle_lbl.pack(pady=(0, 10))
        
        desc_text = (
            "AgriSense AI leverages machine learning and deep learning algorithms to provide "
            "data-driven recommendations for farmers. From selecting the optimal crop and "
            "fertilizer to detecting plant diseases early and estimating profit margins, "
            "AgriSense AI empowers modern agriculture with actionable intelligence."
        )
        desc_lbl = ctk.CTkLabel(
            header_frame, 
            text=desc_text, 
            font=ThemeManager.get_font("body"), 
            wraplength=650,
            justify="center",
            text_color=ThemeManager.get_color("text")
        )
        desc_lbl.pack(pady=10)
        
        # Tech Stack Section
        tech_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=10)
        tech_card.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(tech_card, text="Technology Stack", font=ThemeManager.get_font("subheading"), text_color=ThemeManager.get_color("text")).pack(pady=(15, 10))
        
        tech_grid = ctk.CTkFrame(tech_card, fg_color="transparent")
        tech_grid.pack(pady=(0, 15))
        
        techs = [
            "Python 3.12+", "CustomTkinter", "TensorFlow/MobileNet", "Scikit-Learn", 
            "SQLAlchemy / SQLite", "Matplotlib", "OpenCV", "ReportLab PDF"
        ]
        
        for i, tech in enumerate(techs):
            row = i // 4
            col = i % 4
            badge = ctk.CTkLabel(
                tech_grid, 
                text=tech, 
                fg_color=ThemeManager.get_color("primary"), 
                text_color="white",
                corner_radius=6,
                padx=12, 
                pady=6,
                font=ThemeManager.get_font("caption")
            )
            badge.grid(row=row, column=col, padx=6, pady=6)
            
        # Future Enhancements Section
        future_card = ctk.CTkFrame(self.content_area, fg_color=ThemeManager.get_color("card"), corner_radius=10)
        future_card.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(future_card, text="Future Enhancements", font=ThemeManager.get_font("subheading"), text_color=ThemeManager.get_color("text")).pack(pady=(15, 10))
        
        enhancements = [
            "🌤 Weather API Real-time Integration",
            "🏛 Government Scheme Recommendations",
            "🛰 Satellite & Drone Remote Sensing Analysis",
            "📡 IoT Soil Sensor Data Integration",
            "🗣 Multi-language Support (Hindi / Marathi)",
            "☁️ Cloud Synchronization & Mobile App"
        ]
        
        enh_frame = ctk.CTkFrame(future_card, fg_color="transparent")
        enh_frame.pack(pady=(0, 15), padx=20)
        
        for e in enhancements:
            lbl = ctk.CTkLabel(enh_frame, text=e, font=ThemeManager.get_font("body"), text_color=ThemeManager.get_color("text_secondary"), anchor="w")
            lbl.pack(fill="x", pady=3)
            
        # Footer
        footer_lbl = ctk.CTkLabel(
            self.content_area, 
            text="Built with ❤️ for Indian Agriculture 🇮🇳", 
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("primary")
        )
        footer_lbl.pack(pady=20)
