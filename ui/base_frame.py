import customtkinter as ctk
from ui.theme import ThemeManager

class ContentFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title, subtitle="", **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header Area
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ThemeManager.get_font("heading"),
            text_color=ThemeManager.get_color("text")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Subtitle
        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self.header_frame,
                text=subtitle,
                font=ThemeManager.get_font("body"),
                text_color=ThemeManager.get_color("text_secondary")
            )
            self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
            
        # Separator
        self.separator = ctk.CTkFrame(self, height=2, fg_color=ThemeManager.get_color("card"))
        self.separator.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Message Banner
        self.message_frame = ctk.CTkFrame(self, height=0, fg_color="transparent", corner_radius=8)
        self.message_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.message_frame.grid_remove()  # Hidden by default
        
        self.message_label = ctk.CTkLabel(
            self.message_frame,
            text="",
            font=ThemeManager.get_font("body"),
            text_color="#FFFFFF"
        )
        self.message_label.pack(pady=10, padx=15, fill="x")
        
        # Main Content Area - Subclasses should add widgets here
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=3, column=0, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        
        # Loading State
        self.loading_frame = ctk.CTkFrame(self, fg_color=ThemeManager.get_color("bg"))
        self.loading_label = ctk.CTkLabel(
            self.loading_frame, 
            text="Loading...",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("primary")
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self._message_timer = None

    def _show_message(self, message, color):
        if self._message_timer:
            self.after_cancel(self._message_timer)
            
        self.message_frame.configure(fg_color=color)
        self.message_label.configure(text=message)
        self.message_frame.grid()
        
        # Auto-dismiss after 5 seconds
        self._message_timer = self.after(5000, self._hide_message)
        
    def _hide_message(self):
        self.message_frame.grid_remove()
        self._message_timer = None
        
    def show_error(self, message):
        self._show_message(f"❌ {message}", ThemeManager.get_color("error"))
        
    def show_success(self, message):
        self._show_message(f"✅ {message}", ThemeManager.get_color("success"))
        
    def show_loading(self, message="Loading..."):
        self.loading_label.configure(text=message)
        self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.loading_frame.lift()
        
    def hide_loading(self):
        self.loading_frame.place_forget()
