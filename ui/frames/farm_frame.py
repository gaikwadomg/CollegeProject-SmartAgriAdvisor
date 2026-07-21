import customtkinter as ctk
from tkinter import messagebox

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.input_group import InputGroup
from services.farm_service import FarmService
from utils.logger import get_logger

logger = get_logger(__name__)


class FarmFrame(ContentFrame):
    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        super().__init__(master, title='🏡 Farm Records', subtitle='Manage your farm details and land records', **kwargs)
        
        self.db = db
        self.user = user
        self.farm_service = FarmService(self.db)
        
        self._setup_ui()
        self.refresh_list()
        
    def _setup_ui(self):
        self.actions_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        self.add_btn = ctk.CTkButton(
            self.actions_frame,
            text="+ Add New Farm",
            font=ThemeManager.get_font("subheading"),
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            command=self._show_add_dialog
        )
        self.add_btn.pack(side="right")
        
        self.list_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=10)
        
    def refresh_list(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()
            
        farms = self.farm_service.get_farms(self.user.id)
        
        if not farms:
            empty_lbl = ctk.CTkLabel(
                self.list_container, 
                text="No farms registered yet. Click '+ Add New Farm' to get started! 🌾",
                font=ThemeManager.get_font("body"),
                text_color=ThemeManager.get_color("text_secondary")
            )
            empty_lbl.pack(pady=40)
            return
            
        for farm in farms:
            self._create_farm_card(farm)
            
    def _create_farm_card(self, farm):
        card = ctk.CTkFrame(self.list_container, fg_color=ThemeManager.get_color("card"), corner_radius=10)
        card.pack(fill="x", pady=(0, 15))
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        farm_name = getattr(farm, 'farm_name', getattr(farm, 'name', 'Farm'))
        title = ctk.CTkLabel(info_frame, text=farm_name, font=ThemeManager.get_font("subheading"), text_color=ThemeManager.get_color("text"))
        title.pack(anchor="w")
        
        details_text = f"📍 {farm.location or 'N/A'}  |  📏 {farm.area_acres} acres  |  🌱 {farm.current_crop or 'N/A'}  |  🪨 {farm.soil_type or 'N/A'}"
        details = ctk.CTkLabel(info_frame, text=details_text, font=ThemeManager.get_font("body"), text_color=ThemeManager.get_color("text_secondary"))
        details.pack(anchor="w", pady=(5, 0))
        
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=15, pady=15)
        
        edit_btn = ctk.CTkButton(
            action_frame, 
            text="Edit", 
            width=70, 
            fg_color="transparent", 
            border_width=1,
            border_color=ThemeManager.get_color("primary"),
            text_color=ThemeManager.get_color("text"),
            command=lambda f=farm: self._show_edit_dialog(f)
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            action_frame, 
            text="Delete", 
            width=70, 
            fg_color=ThemeManager.get_color("error"),
            hover_color="#dc2626",
            command=lambda f=farm: self._delete_farm(f)
        )
        delete_btn.pack(side="left", padx=5)

    def _show_add_dialog(self):
        self._open_form_dialog("Add New Farm")

    def _show_edit_dialog(self, farm):
        self._open_form_dialog("Edit Farm", farm)

    def _open_form_dialog(self, title, farm=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x580")
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (420 // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (580 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        inputs = {}
        
        farm_name_val = getattr(farm, 'farm_name', getattr(farm, 'name', '')) if farm else ""
        fields = [
            ("farm_name", "Farm Name", farm_name_val),
            ("location", "Location", farm.location if farm else ""),
            ("area_acres", "Area (Acres)", str(farm.area_acres) if farm else "0.0"),
            ("soil_type", "Soil Type", farm.soil_type if farm else ""),
            ("current_crop", "Current Crop", farm.current_crop if farm else ""),
            ("notes", "Notes", farm.notes if farm else "")
        ]
        
        for key, label, val in fields:
            grp = InputGroup(form_frame, label=label, placeholder="")
            grp.pack(fill="x", pady=(0, 8))
            if val:
                grp.entry.insert(0, val)
            inputs[key] = grp
            
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))
        
        def save():
            try:
                area = float(inputs['area_acres'].get_value() or 0.0)
            except ValueError:
                messagebox.showerror("Error", "Area must be a valid number", parent=dialog)
                return
                
            fn = inputs['farm_name'].get_value()
            if not fn:
                messagebox.showerror("Error", "Farm Name is required", parent=dialog)
                return

            if farm:
                success, msg = self.farm_service.update_farm(
                    farm.id,
                    farm_name=fn,
                    location=inputs['location'].get_value(),
                    area_acres=area,
                    soil_type=inputs['soil_type'].get_value(),
                    current_crop=inputs['current_crop'].get_value(),
                    notes=inputs['notes'].get_value()
                )
            else:
                success, msg = self.farm_service.create_farm(
                    user_id=self.user.id,
                    farm_name=fn,
                    location=inputs['location'].get_value(),
                    area_acres=area,
                    soil_type=inputs['soil_type'].get_value(),
                    current_crop=inputs['current_crop'].get_value(),
                    notes=inputs['notes'].get_value()
                )
                
            if success:
                dialog.destroy()
                self.refresh_list()
            else:
                messagebox.showerror("Error", msg, parent=dialog)
                
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color=ThemeManager.get_color("primary"),
            command=save
        )
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=1, command=dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
    def _delete_farm(self, farm):
        farm_name = getattr(farm, 'farm_name', getattr(farm, 'name', 'Farm'))
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{farm_name}'?\nThis action cannot be undone."
        )
        if confirm:
            success, msg = self.farm_service.delete_farm(farm.id)
            if success:
                self.refresh_list()
            else:
                messagebox.showerror("Error", msg)
