import customtkinter as ctk

class ThemeManager:
    _current_theme = "dark"
    
    _themes = {
        "dark": {
            "bg": "#0f1117",
            "surface": "#1a1d27",
            "card": "#232736",
            "primary": "#4CAF50",
            "accent": "#66BB6A",
            "text": "#E8E8E8",
            "text_secondary": "#9E9E9E",
            "error": "#EF5350",
            "warning": "#FFA726",
            "success": "#66BB6A"
        },
        "light": {
            "bg": "#F5F5F5",
            "surface": "#FFFFFF",
            "card": "#FFFFFF",
            "primary": "#2E7D32",
            "accent": "#43A047",
            "text": "#212121",
            "text_secondary": "#757575",
            "error": "#EF5350",
            "warning": "#FFA726",
            "success": "#66BB6A"
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
