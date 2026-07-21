import customtkinter as ctk
from ui.theme import ThemeManager

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, current_user, on_navigate, on_logout, **kwargs):
        super().__init__(
            master, 
            width=250,
            fg_color=ThemeManager.get_color("surface"),
            corner_radius=0,
            **kwargs
        )
        self.grid_propagate(False)
        self.pack_propagate(False)
        
        self.current_user = current_user
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        
        self.buttons = {}
        self.active_button = None
        
        self._build_ui()
        
    def _build_ui(self):
        # User Info Section
        user_frame = ctk.CTkFrame(self, fg_color="transparent")
        user_frame.pack(fill="x", pady=20, padx=15)
        
        avatar_label = ctk.CTkLabel(
            user_frame,
            text="👤",
            font=("Segoe UI", 32),
            text_color=ThemeManager.get_color("primary")
        )
        avatar_label.pack(side="left", padx=(0, 10))
        
        info_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        username = self.current_user.username if self.current_user else "User"
        role = self.current_user.role if self.current_user else "Admin"
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=username,
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        name_label.pack(anchor="w")
        
        role_label = ctk.CTkLabel(
            info_frame,
            text=role.capitalize(),
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        role_label.pack(anchor="w")
        
        # Separator
        sep = ctk.CTkFrame(self, height=1, fg_color=ThemeManager.get_color("card"))
        sep.pack(fill="x", padx=15, pady=(0, 10))
        
        # Scrollable Menu
        self.menu_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=ThemeManager.get_color("card"),
            scrollbar_button_hover_color=ThemeManager.get_color("primary")
        )
        self.menu_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Navigation Items
        menu_items = [
            ("🏠 Dashboard", "home"),
            ("🌾 Crop Recommendation", "crop"),
            ("🧪 Fertilizer", "fertilizer"),
            ("🐛 Pesticide", "pesticide"),
            ("🍂 Disease Detection", "disease"),
            ("📊 Yield Prediction", "yield"),
            ("🌍 Soil Health", "soil"),
            ("💧 Irrigation", "irrigation"),
            ("💰 Cost & Profit", "cost"),
            ("🏡 Farm Records", "farm"),
            ("📄 Reports", "reports"),
            ("⚙️ Settings", "settings"),
            ("ℹ️ About", "about")
        ]
        
        for text, name in menu_items:
            self._create_menu_button(text, name)
            
        # Logout Section
        logout_sep = ctk.CTkFrame(self, height=1, fg_color=ThemeManager.get_color("card"))
        logout_sep.pack(fill="x", padx=15, pady=(10, 10))
        
        logout_btn = ctk.CTkButton(
            self,
            text="🚪 Logout",
            font=ThemeManager.get_font("body"),
            fg_color="transparent",
            text_color=ThemeManager.get_color("error"),
            hover_color=ThemeManager.get_color("card"),
            anchor="w",
            command=self.on_logout
        )
        logout_btn.pack(fill="x", padx=15, pady=(0, 15))
        
    def _create_menu_button(self, text, name):
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            font=ThemeManager.get_font("body"),
            fg_color="transparent",
            text_color=ThemeManager.get_color("text"),
            hover_color=ThemeManager.get_color("card"),
            anchor="w",
            height=40,
            command=lambda n=name: self._handle_click(n)
        )
        btn.pack(fill="x", padx=10, pady=2)
        self.buttons[name] = btn
        
    def _handle_click(self, name):
        self.set_active(name)
        self.on_navigate(name)
        
    def set_active(self, name):
        if self.active_button:
            self.buttons[self.active_button].configure(
                fg_color="transparent",
                text_color=ThemeManager.get_color("text")
            )
            
        if name in self.buttons:
            self.buttons[name].configure(
                fg_color=ThemeManager.get_color("primary"),
                text_color="#FFFFFF"
            )
            self.active_button = name
