"""
AgriSense AI - Login Frame
=============================

Centered login card with username/password fields, show/hide password,
remember me checkbox, and forgot password link.

Author: AgriSense AI Team
"""

import customtkinter as ctk
from tkinter import messagebox
from ui.theme import ThemeManager


class LoginFrame(ctk.CTkFrame):
    """
    Login screen with a centered card-style form.
    
    Validates inputs locally before calling the auth_callback.
    The auth_callback is expected to handle success/failure
    externally (main.py calls show_error on this frame if login fails).
    """

    def __init__(self, master, auth_callback, **kwargs):
        """
        Initialize the login frame.

        Args:
            master: Parent widget
            auth_callback: Function(username, password) called on login attempt.
                           Does NOT return a value - uses show_error() on failure.
        """
        super().__init__(
            master,
            fg_color=ThemeManager.get_color("bg"),
            **kwargs
        )
        self.auth_callback = auth_callback

        # Configure grid to center the login card
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Login Card
        self.card = ctk.CTkFrame(
            self,
            width=420,
            height=530,
            fg_color=ThemeManager.get_color("card"),
            corner_radius=15
        )
        self.card.grid(row=1, column=1)
        self.card.grid_propagate(False)

        self._build_card_content()

        # Bind Enter key to login
        self.master.bind('<Return>', lambda e: self._attempt_login())

    def _build_card_content(self) -> None:
        """Build the login card UI elements."""
        # Logo/Icon
        icon = ctk.CTkLabel(
            self.card,
            text="🌱",
            font=("Segoe UI", 48),
            text_color=ThemeManager.get_color("primary")
        )
        icon.pack(pady=(40, 5))

        # Title
        title = ctk.CTkLabel(
            self.card,
            text="AgriSense AI",
            font=ThemeManager.get_font("heading"),
            text_color=ThemeManager.get_color("text")
        )
        title.pack(pady=(0, 5))

        # Subtitle
        subtitle = ctk.CTkLabel(
            self.card,
            text="Sign in to continue",
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        subtitle.pack(pady=(0, 25))

        # Error Label (hidden by default)
        self.error_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ThemeManager.get_font("caption"),
            text_color=ThemeManager.get_color("error"),
            wraplength=280
        )
        # Don't pack yet - shown only on error

        # Username
        self.username_input = ctk.CTkEntry(
            self.card,
            placeholder_text="👤  Username",
            width=300,
            height=42,
            font=ThemeManager.get_font("body"),
            fg_color=ThemeManager.get_color("surface"),
            border_color=ThemeManager.get_color("surface"),
            corner_radius=8
        )
        self.username_input.pack(pady=(0, 12))

        # Password
        self.password_input = ctk.CTkEntry(
            self.card,
            placeholder_text="🔒  Password",
            width=300,
            height=42,
            font=ThemeManager.get_font("body"),
            show="•",
            fg_color=ThemeManager.get_color("surface"),
            border_color=ThemeManager.get_color("surface"),
            corner_radius=8
        )
        self.password_input.pack(pady=(0, 10))

        # Options Frame (Remember me + Show password)
        options_frame = ctk.CTkFrame(self.card, fg_color="transparent", width=300)
        options_frame.pack(fill="x", padx=60, pady=(0, 20))

        self.remember_var = ctk.BooleanVar(value=False)
        remember_cb = ctk.CTkCheckBox(
            options_frame,
            text="Remember me",
            variable=self.remember_var,
            font=ThemeManager.get_font("caption"),
            checkbox_width=18,
            checkbox_height=18
        )
        remember_cb.pack(side="left")

        self.show_pass_var = ctk.BooleanVar(value=False)
        show_pass_cb = ctk.CTkCheckBox(
            options_frame,
            text="Show Password",
            variable=self.show_pass_var,
            command=self._toggle_password,
            font=ThemeManager.get_font("caption"),
            checkbox_width=18,
            checkbox_height=18
        )
        show_pass_cb.pack(side="right")

        # Login Button
        login_btn = ctk.CTkButton(
            self.card,
            text="Sign In",
            width=300,
            height=45,
            font=("Segoe UI", 15, "bold"),
            fg_color=ThemeManager.get_color("primary"),
            hover_color=ThemeManager.get_color("accent"),
            corner_radius=8,
            command=self._attempt_login
        )
        login_btn.pack(pady=(5, 15))

        # Forgot Password
        forgot_btn = ctk.CTkButton(
            self.card,
            text="Forgot Password?",
            fg_color="transparent",
            text_color=ThemeManager.get_color("text_secondary"),
            hover_color=ThemeManager.get_color("surface"),
            font=ThemeManager.get_font("caption"),
            command=self._forgot_password
        )
        forgot_btn.pack()

    def _toggle_password(self) -> None:
        """Toggle password visibility."""
        if self.show_pass_var.get():
            self.password_input.configure(show="")
        else:
            self.password_input.configure(show="•")

    def _attempt_login(self) -> None:
        """Validate inputs and call the auth callback."""
        username = self.username_input.get().strip()
        password = self.password_input.get()

        # Clear previous errors
        self.error_label.pack_forget()
        self.username_input.configure(border_color=ThemeManager.get_color("surface"))
        self.password_input.configure(border_color=ThemeManager.get_color("surface"))

        # Validate
        if not username:
            self.username_input.configure(border_color=ThemeManager.get_color("error"))
            self.show_error("Username is required")
            return

        if not password:
            self.password_input.configure(border_color=ThemeManager.get_color("error"))
            self.show_error("Password is required")
            return

        # Call the auth callback (main.py handles success/failure)
        self.auth_callback(username, password)

    def show_error(self, message: str) -> None:
        """
        Display an error message on the login card.

        Args:
            message: Error text to display
        """
        self.error_label.configure(text=message)
        self.error_label.pack(pady=(0, 10), before=self.username_input)
        self.username_input.configure(border_color=ThemeManager.get_color("error"))
        self.password_input.configure(border_color=ThemeManager.get_color("error"))

    def _forgot_password(self) -> None:
        """Show forgot password information dialog."""
        messagebox.showinfo(
            "Forgot Password",
            "Please contact your system administrator to reset your password.\n\n"
            "Default credentials:\n"
            "Username: admin\n"
            "Password: admin123"
        )
