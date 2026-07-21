import os
import shutil
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox, filedialog
from pathlib import Path

from ui.core.frames import ContentFrame
from ui.core.theme import ThemeManager
from config.settings import Settings
from database.models import Prediction
from utils.logger import get_logger

logger = get_logger(__name__)

# Fallback utilities if not present in utils.helpers
def create_backup(db_path, backup_dir):
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_dir) / f"agrisense_backup_{timestamp}.sqlite"
    shutil.copy2(db_path, backup_path)
    return str(backup_path)

def get_file_size_display(file_path):
    if not os.path.exists(file_path):
        return "0 B"
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

class SettingsFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title="⚙️ Settings", **kwargs)
        self.db = db
        self.user = user
        
        # Import dynamically to avoid circular dependencies if any
        try:
            from services.export_service import ExportService
            self.export_service = ExportService(self.db)
        except ImportError:
            self.export_service = None
            
        self.setup_ui()
        
    def setup_ui(self):
        scroll_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        
        # Theme Section
        theme_card = ctk.CTkFrame(scroll_frame, fg_color=ThemeManager.get_color("surface"))
        theme_card.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(theme_card, text="Appearance", font=ThemeManager.get_font("heading")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.theme_var = ctk.StringVar(value=ThemeManager.get_theme_mode().capitalize())
        theme_seg = ctk.CTkSegmentedButton(
            theme_card, 
            values=["Dark", "Light"],
            variable=self.theme_var,
            command=self.change_theme,
            font=ThemeManager.get_font()
        )
        theme_seg.pack(anchor="w", padx=10, pady=(0, 10))
        ctk.CTkLabel(theme_card, text="Note: Full theme change may require app restart.", font=ThemeManager.get_font("small")).pack(anchor="w", padx=10, pady=(0, 10))

        # Database Section
        db_card = ctk.CTkFrame(scroll_frame, fg_color=ThemeManager.get_color("surface"))
        db_card.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(db_card, text="Database Management", font=ThemeManager.get_font("heading")).pack(anchor="w", padx=10, pady=(10, 5))
        
        db_btn_frame = ctk.CTkFrame(db_card, fg_color="transparent")
        db_btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(db_btn_frame, text="Backup Database", command=self.backup_db).pack(side="left", padx=(0, 10))
        ctk.CTkButton(db_btn_frame, text="Restore Database", fg_color=ThemeManager.get_color("secondary"), command=self.restore_db).pack(side="left")
        
        # Export Section
        export_card = ctk.CTkFrame(scroll_frame, fg_color=ThemeManager.get_color("surface"))
        export_card.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(export_card, text="Export Data", font=ThemeManager.get_font("heading")).pack(anchor="w", padx=10, pady=(10, 5))
        
        exp_btn_frame = ctk.CTkFrame(export_card, fg_color="transparent")
        exp_btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(exp_btn_frame, text="Export All Predictions (CSV)", command=lambda: self.export_data("predictions")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(exp_btn_frame, text="Export Farm Records (CSV)", command=lambda: self.export_data("farms")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(exp_btn_frame, text="Export Disease Records (CSV)", command=lambda: self.export_data("diseases")).pack(side="left")

        # Danger Zone
        danger_card = ctk.CTkFrame(scroll_frame, fg_color=ThemeManager.get_color("surface"), border_width=1, border_color=ThemeManager.get_color("danger"))
        danger_card.pack(fill="x", pady=20, padx=5)
        
        ctk.CTkLabel(danger_card, text="Danger Zone", text_color=ThemeManager.get_color("danger"), font=ThemeManager.get_font("heading")).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkButton(
            danger_card, 
            text="Clear All Predictions", 
            fg_color=ThemeManager.get_color("danger"),
            hover_color=ThemeManager.get_color("danger_hover"),
            command=self.clear_predictions
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # About / System Info
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=20, padx=5)
        
        db_path_str = str(Settings.DB_PATH)
        db_size = get_file_size_display(db_path_str)
        info_text = f"App Version: 1.0.0\nDatabase: {db_path_str} ({db_size})\nModel Status: Active"
        
        ctk.CTkLabel(info_frame, text=info_text, font=ThemeManager.get_font("small"), text_color=ThemeManager.get_color("text_secondary"), justify="left").pack(anchor="w")

    def change_theme(self, value):
        mode = value.lower()
        ctk.set_appearance_mode(mode)
        # ThemeManager.set_theme(mode) # Assuming this method exists or you just use appearance mode
        logger.info(f"Theme changed to {mode}")
        
    def backup_db(self):
        try:
            exports_dir = Settings.BASE_DIR / 'exports'
            path = create_backup(Settings.DB_PATH, exports_dir)
            messagebox.showinfo("Success", f"Database backed up successfully to:\n{path}")
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to backup database:\n{str(e)}")

    def restore_db(self):
        file_path = filedialog.askopenfilename(
            title="Select Database Backup",
            filetypes=[("SQLite DB", "*.sqlite"), ("All Files", "*.*")]
        )
        if file_path:
            if messagebox.askyesno("Warning", "Restoring a backup will overwrite the current database. Proceed?"):
                try:
                    # Basic restore by closing session and copying file over
                    # In a robust app, ensure all connections are closed
                    shutil.copy2(file_path, Settings.DB_PATH)
                    messagebox.showinfo("Success", "Database restored successfully. Please restart the application.")
                except Exception as e:
                    logger.error(f"Restore failed: {str(e)}")
                    messagebox.showerror("Error", f"Failed to restore database:\n{str(e)}")

    def export_data(self, export_type):
        if not self.export_service:
            messagebox.showerror("Error", "ExportService not available.")
            return
            
        try:
            path = None
            if export_type == "predictions":
                path = self.export_service.export_predictions_csv(self.user.id)
            elif export_type == "farms":
                path = self.export_service.export_farms_csv(self.user.id)
            elif export_type == "diseases":
                path = self.export_service.export_diseases_csv(self.user.id)
                
            if path:
                messagebox.showinfo("Success", f"Data exported successfully to:\n{path}")
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")

    def clear_predictions(self):
        if messagebox.askyesno("Danger", "Are you absolutely sure you want to delete ALL your prediction history? This cannot be undone."):
            session = self.db.get_session()
            try:
                session.query(Prediction).filter_by(user_id=self.user.id).delete()
                session.commit()
                messagebox.showinfo("Success", "All prediction records have been cleared.")
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to clear predictions: {str(e)}")
                messagebox.showerror("Error", f"Failed to clear records:\n{str(e)}")
            finally:
                session.close()
