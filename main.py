"""
AgriSense AI - Application Entry Point
========================================

Main module that initializes and launches the AgriSense AI desktop
application. Orchestrates the startup sequence:

    1. Ensure required directories exist
    2. Initialize database and create tables
    3. Create default admin user if needed
    4. Show splash screen
    5. Show login screen
    6. Launch main dashboard on successful auth

Usage:
    python main.py

Author: AgriSense AI Team
Version: 1.0.0
"""

import sys
import os

# ── Ensure project root is on sys.path ────────────────────────────────
# This allows absolute imports like 'from config.settings import Settings'
# to work regardless of where the script is launched from.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import customtkinter as ctk

from config.settings import Settings
from utils.logger import get_logger
from database.database import DatabaseManager
from services.auth_service import AuthService
from services.prediction_service import PredictionService

logger = get_logger("main")


class AgriSenseApp:
    """
    Main application controller.
    
    Manages the application lifecycle including initialization,
    screen transitions (splash → login → dashboard), and cleanup.
    """

    def __init__(self):
        """Initialize the application and all core services."""
        logger.info("=" * 60)
        logger.info(f"  {Settings.APP_NAME} v{Settings.VERSION}")
        logger.info(f"  {Settings.APP_SUBTITLE}")
        logger.info("=" * 60)

        # ── Step 1: Create required directories ───────────────────────
        Settings.ensure_directories()
        logger.info("Application directories verified")

        # ── Step 2: Initialize database ───────────────────────────────
        self.db_manager = DatabaseManager()
        self.db_manager.init_db()
        logger.info("Database initialized")

        # ── Step 3: Initialize services ───────────────────────────────
        self.auth_service = AuthService(self.db_manager)
        self.prediction_service = PredictionService(self.db_manager)

        # ── Step 4: Create default admin if needed ────────────────────
        self.auth_service.ensure_default_admin()

        # ── Step 5: Configure CustomTkinter ───────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # ── Step 6: Create root window ────────────────────────────────
        self.root = ctk.CTk()
        self.root.title(Settings.APP_NAME)
        self.root.geometry(f"{Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
        self.root.minsize(Settings.MIN_WINDOW_WIDTH, Settings.MIN_WINDOW_HEIGHT)

        # Center the window on screen
        self._center_window(self.root, Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Current user (set after login)
        self.current_user = None

        # ── Step 7: Show splash then login ────────────────────────────
        self._show_splash()

    def _center_window(self, window, width: int, height: int) -> None:
        """Center a window on the screen."""
        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    # ── Screen Flow ───────────────────────────────────────────────────

    def _show_splash(self) -> None:
        """Display the splash screen and transition to login."""
        from ui.splash import SplashScreen

        logger.info("Showing splash screen")

        # Hide main window during splash
        self.root.withdraw()

        splash = SplashScreen(
            master=self.root,
            on_complete=self._show_login
        )
        splash.start()

    def _show_login(self) -> None:
        """Display the login screen."""
        from ui.login import LoginFrame

        logger.info("Showing login screen")

        # Show main window and clear it
        self.root.deiconify()
        for widget in self.root.winfo_children():
            widget.destroy()

        # Resize for login
        self.root.geometry(f"{Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
        self._center_window(self.root, Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT)

        # Create login frame
        self.login_frame = LoginFrame(
            master=self.root,
            auth_callback=self._on_login
        )
        self.login_frame.pack(fill="both", expand=True)

    def _on_login(self, username: str, password: str) -> None:
        """
        Handle login attempt from the login frame.

        Args:
            username: Entered username
            password: Entered password
        """
        success, user = self.auth_service.authenticate(username, password)

        if success and user:
            self.current_user = user
            logger.info(f"Login successful for: {user.username}")
            self._show_dashboard()
        else:
            # Show error on login frame
            if hasattr(self, 'login_frame'):
                self.login_frame.show_error("Invalid username or password. Please try again.")
            logger.warning(f"Login failed for: {username}")

    def _show_dashboard(self) -> None:
        """Display the main dashboard after successful login."""
        from ui.dashboard import Dashboard

        logger.info("Launching dashboard")

        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create dashboard
        self.dashboard = Dashboard(
            master=self.root,
            user=self.current_user,
            db_manager=self.db_manager,
            prediction_service=self.prediction_service,
            on_logout=self._on_logout
        )
        self.dashboard.pack(fill="both", expand=True)

    def _on_logout(self) -> None:
        """Handle logout - return to login screen."""
        logger.info(f"User '{self.current_user.username}' logged out")
        self.current_user = None
        self._show_login()

    def _on_closing(self) -> None:
        """Handle application close."""
        logger.info("Application closing")
        self.root.destroy()

    # ── Run ───────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the application main loop."""
        logger.info("Starting application main loop")
        self.root.mainloop()
        logger.info("Application terminated")


# ══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

def main():
    """Application entry point."""
    try:
        app = AgriSenseApp()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
