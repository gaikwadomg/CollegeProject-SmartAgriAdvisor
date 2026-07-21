import os
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from services.report_service import ReportService
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportsFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title="📄 Reports", subtitle="Generate and view application PDF reports", **kwargs)
        self.db = db
        self.user = user
        self.report_service = ReportService(self.db)
        
        self.setup_ui()
        self.load_reports()
        
    def setup_ui(self):
        action_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 20))
        
        self.report_type_var = ctk.StringVar(value="Prediction Report")
        self.type_dropdown = ctk.CTkOptionMenu(
            action_frame,
            values=["Prediction Report", "Farm Report", "Disease Report"],
            variable=self.report_type_var,
            width=220,
            font=ThemeManager.get_font("body")
        )
        self.type_dropdown.pack(side="left", padx=(0, 10))
        
        generate_btn = ctk.CTkButton(
            action_frame,
            text="Generate Report",
            font=ThemeManager.get_font("subheading"),
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            command=self.generate_report
        )
        generate_btn.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh List",
            font=ThemeManager.get_font("body"),
            fg_color=ThemeManager.get_color("surface"),
            hover_color=ThemeManager.get_color("card"),
            text_color=ThemeManager.get_color("text"),
            command=self.load_reports,
            width=110
        )
        refresh_btn.pack(side="right")
        
        self.list_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def generate_report(self):
        report_type = self.report_type_var.get()
        self.type_dropdown.configure(state="disabled")
        self.update_idletasks()
        
        try:
            if report_type == "Prediction Report":
                path = self.report_service.generate_prediction_report(self.user.id)
            elif report_type == "Farm Report":
                path = self.report_service.generate_farm_report(self.user.id)
            elif report_type == "Disease Report":
                path = self.report_service.generate_disease_report(self.user.id)
            else:
                path = self.report_service.generate_prediction_report(self.user.id)
            
            messagebox.showinfo("Success", f"Report generated successfully:\n{path}")
            self.load_reports()
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
        finally:
            self.type_dropdown.configure(state="normal")
            
    def load_reports(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        reports = self.report_service.get_reports(self.user.id)
        
        if not reports:
            lbl = ctk.CTkLabel(
                self.list_frame,
                text="No reports generated yet. Select a report type above and click 'Generate Report'!",
                font=ThemeManager.get_font("body"),
                text_color=ThemeManager.get_color("text_secondary")
            )
            lbl.pack(pady=30)
            return
            
        for r in reports:
            self.create_report_card(r)

    def create_report_card(self, report_data):
        card = ctk.CTkFrame(self.list_frame, fg_color=ThemeManager.get_color("card"), corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=12)
        
        title_str = getattr(report_data, 'title', 'Report')
        title_lbl = ctk.CTkLabel(
            info_frame, 
            text=title_str, 
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        title_lbl.pack(anchor="w")
        
        created_at = getattr(report_data, 'created_at', datetime.now())
        date_str = created_at.strftime("%Y-%m-%d %H:%M") if isinstance(created_at, datetime) else str(created_at)
        rtype = getattr(report_data, 'report_type', 'prediction')
        desc_lbl = ctk.CTkLabel(
            info_frame, 
            text=f"Type: {rtype.capitalize()}  |  Generated: {date_str}", 
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        desc_lbl.pack(anchor="w", pady=(3, 0))
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=15, pady=12)
        
        filepath = getattr(report_data, 'file_path', '')
        open_btn = ctk.CTkButton(
            btn_frame,
            text="Open PDF",
            width=90,
            fg_color=ThemeManager.get_color("primary"),
            command=lambda path=filepath: self.open_report(path)
        )
        open_btn.pack(side="left", padx=5)

    def open_report(self, file_path):
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                messagebox.showerror("Error", "File not found.")
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
