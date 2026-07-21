import customtkinter as ctk
from ui.theme import ThemeManager

class LoadingSpinner(ctk.CTkFrame):
    def __init__(self, master, message="Loading...", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.message = message
        self._is_running = False
        self._animation_step = 0
        self._dots = ["", ".", "..", "..."]
        
        self.label = ctk.CTkLabel(
            self,
            text=self.message,
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("primary")
        )
        self.label.pack(pady=10, padx=20)
        
    def _animate(self):
        if not self._is_running:
            return
            
        self._animation_step = (self._animation_step + 1) % len(self._dots)
        self.label.configure(text=f"{self.message}{self._dots[self._animation_step]}")
        self.after(400, self._animate)
        
    def show(self):
        self._is_running = True
        self.pack(expand=True, fill="both")
        self._animate()
        
    def hide(self):
        self._is_running = False
        self.pack_forget()

class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, master, message="Processing...", **kwargs):
        super().__init__(
            master, 
            fg_color=ThemeManager.get_color("bg"),
            **kwargs
        )
        # Using a solid background matching the theme since opacity isn't easily supported in CTkFrame
        self.spinner = LoadingSpinner(self, message=message)
        
    def show(self):
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.spinner.show()
        self.lift()
        
    def hide(self):
        self.spinner.hide()
        self.place_forget()
