import customtkinter as ctk
from ui.theme import ThemeManager

class InputGroup(ctk.CTkFrame):
    def __init__(self, master, label, placeholder="", input_type="text", options=None, required=False, tooltip_text="", min_val=None, max_val=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.input_type = input_type
        self.required = required
        self.min_val = min_val
        self.max_val = max_val
        
        self.grid_columnconfigure(0, weight=1)
        
        label_text = f"{label} {'*' if required else ''}"
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=ThemeManager.get_font("body"),
            text_color=ThemeManager.get_color("text")
        )
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        if input_type == "dropdown":
            self.input = ctk.CTkComboBox(
                self,
                values=options if options else [],
                font=ThemeManager.get_font("body"),
                fg_color=ThemeManager.get_color("surface"),
                border_color=ThemeManager.get_color("card"),
                button_color=ThemeManager.get_color("primary"),
                button_hover_color=ThemeManager.get_color("accent")
            )
            if options:
                self.input.set(options[0])
        else:
            self.input = ctk.CTkEntry(
                self,
                placeholder_text=placeholder,
                font=ThemeManager.get_font("body"),
                fg_color=ThemeManager.get_color("surface"),
                border_color=ThemeManager.get_color("card")
            )
            
        self.input.grid(row=1, column=0, sticky="ew")
        
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("error")
        )
        self.error_label.grid(row=2, column=0, sticky="w")
        self.error_label.grid_remove()
        
    def get_value(self):
        val = self.input.get().strip() if isinstance(self.input, ctk.CTkEntry) else self.input.get()
        if self.input_type == "number" and val:
            try:
                return float(val)
            except ValueError:
                return val
        return val
        
    def validate(self):
        val = self.get_value()
        self.clear_error()
        
        if self.required and not val:
            self.show_error("This field is required.")
            return False
            
        if self.input_type == "number" and val:
            try:
                num_val = float(val)
                if self.min_val is not None and num_val < self.min_val:
                    self.show_error(f"Minimum value is {self.min_val}.")
                    return False
                if self.max_val is not None and num_val > self.max_val:
                    self.show_error(f"Maximum value is {self.max_val}.")
                    return False
            except ValueError:
                self.show_error("Please enter a valid number.")
                return False
                
        return True
        
    def show_error(self, message):
        self.input.configure(border_color=ThemeManager.get_color("error"))
        self.error_label.configure(text=message)
        self.error_label.grid()
        
    def clear_error(self):
        self.input.configure(border_color=ThemeManager.get_color("card"))
        self.error_label.grid_remove()
        
    def clear(self):
        self.clear_error()
        if isinstance(self.input, ctk.CTkEntry):
            self.input.delete(0, 'end')
