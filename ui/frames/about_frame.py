import customtkinter as ctk
from ui.core.frames import ContentFrame
from ui.core.theme import ThemeManager

class AboutFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title="ℹ️ About AgriSense AI", **kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        scroll_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        
        # Header Section
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        logo_lbl = ctk.CTkLabel(header_frame, text="🌱", font=ThemeManager.get_font(size=64))
        logo_lbl.pack(pady=10)
        
        title_lbl = ctk.CTkLabel(header_frame, text="AgriSense AI v1.0.0", font=ThemeManager.get_font("heading", size=24))
        title_lbl.pack()
        
        subtitle_lbl = ctk.CTkLabel(
            header_frame, 
            text="Intelligent Agriculture Decision Support System", 
            font=ThemeManager.get_font(size=14),
            text_color=ThemeManager.get_color("text_secondary")
        )
        subtitle_lbl.pack(pady=(0, 10))
        
        desc_text = (
            "AgriSense AI leverages advanced machine learning algorithms to provide "
            "actionable insights for farmers. By predicting crop yields, recommending "
            "fertilizers, and detecting plant diseases early, we aim to optimize "
            "agricultural productivity and sustainability."
        )
        desc_lbl = ctk.CTkLabel(
            header_frame, 
            text=desc_text, 
            font=ThemeManager.get_font(), 
            wraplength=600,
            justify="center"
        )
        desc_lbl.pack(pady=10)
        
        # Tech Stack Section
        tech_card = ctk.CTkFrame(scroll_frame, fg_color=ThemeManager.get_color("surface"))
        tech_card.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(tech_card, text="Technology Stack", font=ThemeManager.get_font("heading")).pack(pady=(10, 5))
        
        tech_grid = ctk.CTkFrame(tech_card, fg_color="transparent")
        tech_grid.pack(pady=10)
        
        techs = [
            "Python", "CustomTkinter", "TensorFlow", "Scikit-learn", 
            "SQLAlchemy", "Matplotlib", "OpenCV", "ReportLab"
        ]
        
        for i, tech in enumerate(techs):
            row = i // 4
            col = i % 4
            badge = ctk.CTkLabel(
                tech_grid, 
                text=tech, 
                fg_color=ThemeManager.get_color("accent"), 
                text_color="white",
                corner_radius=5,
                padx=10, 
                pady=5,
                font=ThemeManager.get_font("small")
            )
            badge.grid(row=row, column=col, padx=5, pady=5)
            
        # Future Enhancements Section
        future_card = ctk.CTkFrame(scroll_frame, fg_color=ThemeManager.get_color("surface"))
        future_card.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(future_card, text="Future Enhancements", font=ThemeManager.get_font("heading")).pack(pady=(10, 5))
        
        enhancements = [
            "• Weather API Integration",
            "• Government Scheme Recommendations",
            "• Satellite Data Analysis",
            "• IoT Sensor Integration",
            "• Multi-language Support (Hindi/Marathi)",
            "• Cloud Synchronization",
            "• Mobile App",
            "• Web Dashboard"
        ]
        
        enh_frame = ctk.CTkFrame(future_card, fg_color="transparent")
        enh_frame.pack(pady=10)
        
        for e in enhancements:
            lbl = ctk.CTkLabel(enh_frame, text=e, font=ThemeManager.get_font(), anchor="w")
            lbl.pack(fill="x", pady=2)
            
        # Developer Credits & University
        credits_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        credits_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(credits_frame, text="Developed by Placeholder Name", font=ThemeManager.get_font("bold")).pack()
        ctk.CTkLabel(credits_frame, text="University of XYZ (Department of Computer Science)", font=ThemeManager.get_font()).pack()
        
        # Footer
        footer_lbl = ctk.CTkLabel(
            scroll_frame, 
            text="Built with ❤️ for Indian Agriculture", 
            font=ThemeManager.get_font("small"),
            text_color=ThemeManager.get_color("accent")
        )
        footer_lbl.pack(pady=20)
