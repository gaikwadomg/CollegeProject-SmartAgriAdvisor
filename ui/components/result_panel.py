import customtkinter as ctk
from ui.theme import ThemeManager

class ResultPanel(ctk.CTkFrame):
    def __init__(self, master, title="Results", **kwargs):
        super().__init__(
            master, 
            fg_color=ThemeManager.get_color("card"),
            corner_radius=10,
            **kwargs
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")
        
        self.separator = ctk.CTkFrame(self, height=2, fg_color=ThemeManager.get_color("surface"))
        self.separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        
        self.results_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.results_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(1, weight=1)
        
        self.row_count = 0
        
    def add_row(self, label, value, color=None):
        if color is None:
            color = ThemeManager.get_color("text")
            
        lbl = ctk.CTkLabel(
            self.results_frame,
            text=label,
            font=ThemeManager.get_font("body"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        lbl.grid(row=self.row_count, column=0, sticky="w", pady=5)
        
        val_lbl = ctk.CTkLabel(
            self.results_frame,
            text=str(value),
            font=ThemeManager.get_font("body"),
            text_color=color
        )
        val_lbl.grid(row=self.row_count, column=1, sticky="e", pady=5)
        
        self.row_count += 1
        
    def set_results(self, results_dict):
        self.clear()
        for key, value in results_dict.items():
            color = ThemeManager.get_color("text")
            if isinstance(value, tuple) and len(value) == 2:
                val, color_name = value
                if color_name in ["good", "success"]:
                    color = ThemeManager.get_color("success")
                elif color_name in ["warn", "warning"]:
                    color = ThemeManager.get_color("warning")
                elif color_name in ["bad", "error", "danger"]:
                    color = ThemeManager.get_color("error")
                self.add_row(key, val, color)
            else:
                self.add_row(key, value)
                
    def clear(self):
        for child in self.results_frame.winfo_children():
            child.destroy()
        self.row_count = 0
