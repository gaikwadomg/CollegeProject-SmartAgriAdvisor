import customtkinter as ctk
from PIL import Image, ImageTk
from ui.theme import ThemeManager
import os

class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, title="Image", max_size=(400, 400), **kwargs):
        super().__init__(
            master, 
            fg_color=ThemeManager.get_color("card"),
            corner_radius=10,
            **kwargs
        )
        self.max_size = max_size
        self.current_image = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        self.title_label.grid(row=0, column=0, pady=(15, 5), padx=15, sticky="w")
        
        self.image_label = ctk.CTkLabel(
            self,
            text="No Image Loaded",
            font=ThemeManager.get_font("body"),
            text_color=ThemeManager.get_color("text_secondary"),
            width=max_size[0],
            height=max_size[1],
            fg_color=ThemeManager.get_color("surface"),
            corner_radius=8
        )
        self.image_label.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")
        
    def load_image(self, path):
        if not os.path.exists(path):
            self.image_label.configure(text="Image Not Found", image=None)
            return
            
        try:
            pil_image = Image.open(path)
            self.set_image(pil_image)
        except Exception as e:
            self.image_label.configure(text=f"Error: {str(e)}", image=None)
            
    def set_image(self, pil_image):
        # Resize maintaining aspect ratio
        pil_image.thumbnail(self.max_size, Image.Resampling.LANCZOS)
        
        self.current_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(pil_image.width, pil_image.height)
        )
        
        self.image_label.configure(text="", image=self.current_image)
        
    def clear(self):
        self.current_image = None
        self.image_label.configure(text="No Image Loaded", image=None)
