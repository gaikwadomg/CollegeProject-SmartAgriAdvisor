import customtkinter as ctk
from tkinter import messagebox
from ui.frames.content_frame import ContentFrame
from ui.components.cards import ThemeManager, InputGroup
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
        # Top actions
        self.actions_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.add_btn = ctk.CTkButton(
            self.actions_frame,
            text="+ Add New Farm",
            font=ctk.CTkFont(weight="bold"),
            command=self._show_add_dialog
        )
        self.add_btn.pack(side="right")
        
        # Container for farm list
        self.list_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=20)
        
    def refresh_list(self):
        # Clear existing
        for widget in self.list_container.winfo_children():
            widget.destroy()
            
        farms = self.farm_service.get_farms(self.user.id)
        
        if not farms:
            empty_lbl = ctk.CTkLabel(
                self.list_container, 
                text="No farms found. Click 'Add New Farm' to get started.",
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="gray"
            )
            empty_lbl.pack(pady=40)
            return
            
        for farm in farms:
            self._create_farm_card(farm)
            
    def _create_farm_card(self, farm):
        card = ctk.CTkFrame(self.list_container, fg_color=ThemeManager.get_color("card_bg"), corner_radius=10)
        card.pack(fill="x", pady=(0, 15))
        
        # Info section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        title = ctk.CTkLabel(info_frame, text=farm.name, font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(anchor="w")
        
        details_text = f"📍 {farm.location}  |  📏 {farm.area_acres} acres  |  🌱 {farm.current_crop}  |  🪨 {farm.soil_type}"
        details = ctk.CTkLabel(info_frame, text=details_text, font=ctk.CTkFont(size=13))
        details.pack(anchor="w", pady=(5, 0))
        
        # Actions section
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=15, pady=15)
        
        edit_btn = ctk.CTkButton(
            action_frame, 
            text="Edit", 
            width=60, 
            fg_color="transparent", 
            border_width=1,
            command=lambda f=farm: self._show_edit_dialog(f)
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            action_frame, 
            text="Delete", 
            width=60, 
            fg_color="#ef4444", 
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
        dialog.geometry("400x550")
        dialog.grab_set()  # Make modal
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (400 // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (550 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        inputs = {}
        
        # Fields
        fields = [
            ("name", "Farm Name", farm.name if farm else ""),
            ("location", "Location", farm.location if farm else ""),
            ("area_acres", "Area (Acres)", str(farm.area_acres) if farm else "0.0"),
            ("soil_type", "Soil Type", farm.soil_type if farm else ""),
            ("current_crop", "Current Crop", farm.current_crop if farm else ""),
            ("notes", "Notes", farm.notes if farm else "")
        ]
        
        for key, label, val in fields:
            grp = InputGroup(form_frame, label=label)
            grp.insert(0, val)
            grp.pack(fill="x", pady=(0, 10))
            inputs[key] = grp
            
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def save():
            try:
                area = float(inputs['area_acres'].get() or 0.0)
            except ValueError:
                messagebox.showerror("Error", "Area must be a number", parent=dialog)
                return
                
            data = {
                'farm_name' if not farm else 'name': inputs['name'].get(),
                'location': inputs['location'].get(),
                'area_acres': area,
                'soil_type': inputs['soil_type'].get(),
                'current_crop': inputs['current_crop'].get(),
                'notes': inputs['notes'].get()
            }
            
            if farm:
                # Update
                # Rename 'farm_name' back if needed by update_farm
                success, msg = self.farm_service.update_farm(farm.id, **data)
            else:
                # Add
                success, msg = self.farm_service.create_farm(self.user.id, **data)
                
            if success:
                dialog.destroy()
                self.refresh_list()
            else:
                messagebox.showerror("Error", msg, parent=dialog)
                
        save_btn = ctk.CTkButton(btn_frame, text="Save", command=save)
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=1, command=dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
    def _delete_farm(self, farm):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{farm.name}'?\nThis action cannot be undone."
        )
        if confirm:
            success, msg = self.farm_service.delete_farm(farm.id)
            if success:
                self.refresh_list()
            else:
                messagebox.showerror("Error", msg)
