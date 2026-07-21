"""
AgriSense AI - Splash Screen
===============================

Animated splash screen displayed during application startup.
Shows the app logo, tagline, and an animated progress bar
before transitioning to the login screen.

Author: AgriSense AI Team
"""

import customtkinter as ctk
from ui.theme import ThemeManager


class SplashScreen(ctk.CTkToplevel):
    """
    Frameless splash window with animated progress bar.
    
    Shows for ~3 seconds while the app initializes, then
    calls the on_complete callback to transition to login.
    """

    def __init__(self, master=None, on_complete=None):
        """
        Initialize the splash screen.

        Args:
            master: Parent window (usually the root CTk)
            on_complete: Callback to invoke when splash finishes
        """
        super().__init__(master)
        self.on_complete = on_complete

        # ── Window Configuration ──────────────────────────────────────
        self.title("AgriSense AI")
        self.overrideredirect(True)        # Frameless window
        self.attributes('-topmost', True)  # Stay on top

        # Size and center
        width, height = 600, 400
        self.geometry(f"{width}x{height}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.configure(fg_color=ThemeManager.get_color("bg"))

        # ── Build UI ─────────────────────────────────────────────────
        self._build_ui()

        # ── Animation State ──────────────────────────────────────────
        self.progress_value = 0.0

    def _build_ui(self) -> None:
        """Construct the splash screen UI elements."""
        # Decorative plant emoji
        icon_label = ctk.CTkLabel(
            self,
            text="🌱",
            font=("Segoe UI", 64),
            text_color=ThemeManager.get_color("primary")
        )
        icon_label.pack(pady=(60, 10))

        # App Name
        title_label = ctk.CTkLabel(
            self,
            text="AgriSense AI",
            font=("Segoe UI", 36, "bold"),
            text_color=ThemeManager.get_color("primary")
        )
        title_label.pack(pady=(0, 5))

        # Tagline
        tagline_label = ctk.CTkLabel(
            self,
            text="Intelligent Agriculture Decision Support System",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        tagline_label.pack(pady=(0, 20))

        # Version (bottom)
        version_label = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        version_label.pack(side="bottom", pady=20)

        # Progress Bar (bottom)
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=10,
            fg_color=ThemeManager.get_color("surface"),
            progress_color=ThemeManager.get_color("primary"),
            corner_radius=5
        )
        self.progress_bar.pack(side="bottom", pady=(0, 20))
        self.progress_bar.set(0)

        # Status Label (above progress)
        self.status_label = ctk.CTkLabel(
            self,
            text="Initializing...",
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        self.status_label.pack(side="bottom", pady=(0, 5))

    def start(self) -> None:
        """Start the splash animation."""
        self.after(50, self._animate_progress)

    def _animate_progress(self) -> None:
        """Animate the progress bar and update status text."""
        self.progress_value += 0.02
        self.progress_bar.set(min(self.progress_value, 1.0))

        # Update status text at different stages
        if self.progress_value < 0.3:
            self.status_label.configure(text="Loading models...")
        elif self.progress_value < 0.6:
            self.status_label.configure(text="Connecting to database...")
        elif self.progress_value < 0.9:
            self.status_label.configure(text="Preparing interface...")
        else:
            self.status_label.configure(text="Ready!")

        if self.progress_value >= 1.0:
            self.destroy()
            if self.on_complete:
                self.on_complete()
        else:
            self.after(60, self._animate_progress)
