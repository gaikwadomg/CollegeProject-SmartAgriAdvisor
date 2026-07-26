import customtkinter as ctk

class ThemeManager:
    _current_theme = "dark"
    
    _themes = {
        "dark": {
            "bg": "#0B1511",
            "surface": "#12201A",
            "card": "#182C24",
            "primary": "#198754",
            "accent": "#2E7D32",
            "text": "#E8E8E8",
            "text_secondary": "#A8B2AE",
            "error": "#EF5350",
            "warning": "#FFA726",
            "success": "#198754"
        },
        "light": {
            "bg": "#F4F6F5",
            "surface": "#FFFFFF",
            "card": "#FFFFFF",
            "primary": "#0F5132",
            "accent": "#198754",
            "text": "#1A2521",
            "text_secondary": "#5C6A65",
            "error": "#C0392B",
            "warning": "#B7950B",
            "success": "#196F3D"
        }
    }
    
    _fonts = {
        "heading": ("Segoe UI", 24, "bold"),
        "subheading": ("Segoe UI", 16, "bold"),
        "body": ("Segoe UI", 13),
        "caption": ("Segoe UI", 11)
    }

    @classmethod
    def get_color(cls, name):
        return cls._themes[cls._current_theme].get(name, "#000000")
        
    @classmethod
    def get_font(cls, name):
        return cls._fonts.get(name, ("Segoe UI", 13))
        
    @classmethod
    def set_theme(cls, theme_name):
        if theme_name in cls._themes:
            cls._current_theme = theme_name
            if theme_name == "dark":
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")

    @classmethod
    def get_theme(cls):
        return cls._current_theme
        
    @classmethod
    def apply_theme(cls, widget):
        pass # Optional styling application
