import customtkinter as ctk
from ui.theme import ThemeManager

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value, icon_text, color, trend_text="", **kwargs):
        super().__init__(
            master, 
            fg_color=ThemeManager.get_color("card"),
            corner_radius=10,
            **kwargs
        )
        self.original_bg = ThemeManager.get_color("card")
        self.hover_bg = ThemeManager.get_color("surface")
        
        self.grid_columnconfigure(1, weight=1)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self, 
            text=icon_text, 
            font=("Segoe UI", 32),
            text_color=color
        )
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=15, sticky="w")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=ThemeManager.get_font("body"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        self.title_label.grid(row=0, column=1, padx=(0, 15), pady=(15, 0), sticky="w")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self, 
            text=str(value), 
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        self.value_label.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="w")
        
        # Trend
        if trend_text:
            self.trend_label = ctk.CTkLabel(
                self,
                text=trend_text,
                font=ThemeManager.get_font("caption"),
                text_color=ThemeManager.get_color("accent")
            )
            self.trend_label.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")

        # Hover binding
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        for child in self.winfo_children():
            child.bind("<Enter>", self.on_hover)
            child.bind("<Leave>", self.on_leave)
            
    def on_hover(self, event):
        self.configure(fg_color=self.hover_bg)
        
    def on_leave(self, event):
        self.configure(fg_color=self.original_bg)
        
    def update_value(self, new_value):
        self.value_label.configure(text=str(new_value))
