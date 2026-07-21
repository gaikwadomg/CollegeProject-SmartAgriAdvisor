import os
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

from ui.core.frames import ContentFrame
from ui.core.theme import ThemeManager
from services.report_service import ReportService
from utils.logger import get_logger

logger = get_logger(__name__)

class ReportsFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title="📄 Reports", **kwargs)
        self.db = db
        self.user = user
        self.report_service = ReportService(self.db)
        
        self.setup_ui()
        self.load_reports()
        
    def setup_ui(self):
        # Action Bar
        action_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 20))
        
        self.report_type_var = ctk.StringVar(value="Prediction Report")
        self.type_dropdown = ctk.CTkOptionMenu(
            action_frame,
            values=["Prediction Report", "Farm Report", "Disease Report"],
            variable=self.report_type_var,
            width=200,
            font=ThemeManager.get_font()
        )
        self.type_dropdown.pack(side="left", padx=(0, 10))
        
        generate_btn = ctk.CTkButton(
            action_frame,
            text="Generate Report",
            font=ThemeManager.get_font("bold"),
            fg_color=ThemeManager.get_color("accent"),
            hover_color=ThemeManager.get_color("accent_hover"),
            command=self.generate_report
        )
        generate_btn.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh List",
            font=ThemeManager.get_font("bold"),
            fg_color=ThemeManager.get_color("secondary"),
            hover_color=ThemeManager.get_color("secondary_hover"),
            command=self.load_reports,
            width=100
        )
        refresh_btn.pack(side="right")
        
        # Reports List Area (Scrollable)
        self.list_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def generate_report(self):
        report_type = self.report_type_var.get()
        
        # Show loading state indirectly by changing cursor or simply blocking (for brevity, basic approach)
        self.type_dropdown.configure(state="disabled")
        self.master.config(cursor="wait")
        self.update_idletasks()
        
        try:
            if report_type == "Prediction Report":
                path = self.report_service.generate_prediction_report(self.user.id)
            elif report_type == "Farm Report":
                path = self.report_service.generate_farm_report(self.user.id)
            elif report_type == "Disease Report":
                path = self.report_service.generate_disease_report(self.user.id)
            
            messagebox.showinfo("Success", f"Report generated successfully:\n{path}")
            self.load_reports()
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
        finally:
            self.type_dropdown.configure(state="normal")
            self.master.config(cursor="")
            
    def load_reports(self):
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        reports = self.report_service.get_reports(self.user.id)
        
        if not reports:
            lbl = ctk.CTkLabel(self.list_frame, text="No reports generated yet.", font=ThemeManager.get_font())
            lbl.pack(pady=20)
            return
            
        for r in reports:
            self.create_report_card(r)

    def create_report_card(self, report_data):
        card = ctk.CTkFrame(self.list_frame, fg_color=ThemeManager.get_color("surface"))
        card.pack(fill="x", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        title_lbl = ctk.CTkLabel(
            info_frame, 
            text=report_data['title'], 
            font=ThemeManager.get_font("heading", size=14)
        )
        title_lbl.pack(anchor="w")
        
        date_str = report_data['created_at'].strftime("%Y-%m-%d %H:%M")
        desc_lbl = ctk.CTkLabel(
            info_frame, 
            text=f"Type: {report_data['report_type'].capitalize()} | Generated: {date_str}", 
            font=ThemeManager.get_font("small"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        desc_lbl.pack(anchor="w")
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)
        
        open_btn = ctk.CTkButton(
            btn_frame,
            text="Open",
            width=80,
            command=lambda path=report_data['file_path']: self.open_report(path)
        )
        open_btn.pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            width=80,
            fg_color=ThemeManager.get_color("danger"),
            hover_color=ThemeManager.get_color("danger_hover"),
            command=lambda rid=report_data['id']: self.delete_report(rid)
        )
        del_btn.pack(side="left", padx=5)

    def open_report(self, file_path):
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                messagebox.showerror("Error", "File not found.")
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def delete_report(self, report_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this report?"):
            self.report_service.delete_report(report_id)
            self.load_reports()
