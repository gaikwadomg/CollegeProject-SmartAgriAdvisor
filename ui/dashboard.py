"""
AgriSense AI - Main Dashboard
================================

The primary application shell after login. Contains the sidebar
navigation and content area. Handles frame switching between
all application modules.

Author: AgriSense AI Team
"""

import customtkinter as ctk

from ui.theme import ThemeManager
from ui.sidebar import Sidebar
from database.database import DatabaseManager
from services.prediction_service import PredictionService
from utils.logger import get_logger

logger = get_logger(__name__)


class Dashboard(ctk.CTkFrame):
    """
    Main dashboard frame containing sidebar and content area.
    
    Acts as the application shell that hosts all module frames.
    Frame switching is handled by destroying the old frame and
    creating a new instance of the requested module.
    """

    def __init__(
        self,
        master,
        user,
        db_manager: DatabaseManager,
        prediction_service: PredictionService,
        on_logout=None,
        **kwargs
    ):
        """
        Initialize the dashboard.

        Args:
            master: Parent widget (root CTk window)
            user: Authenticated User object
            db_manager: DatabaseManager instance
            prediction_service: PredictionService instance
            on_logout: Callback for logout action
        """
        super().__init__(master, fg_color=ThemeManager.get_color("bg"), **kwargs)

        self.user = user
        self.db_manager = db_manager
        self.prediction_service = prediction_service
        self.on_logout_callback = on_logout
        self.current_frame = None

        # Layout: sidebar (left) + content (right)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_ui()

        # Show home by default
        self.sidebar.set_active("home")
        self.show_frame("home")

    def _build_ui(self) -> None:
        """Build the sidebar and content container."""
        # ── Sidebar ───────────────────────────────────────────────────
        self.sidebar = Sidebar(
            self,
            current_user=self.user,
            on_navigate=self.show_frame,
            on_logout=self._logout
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # ── Content Area ──────────────────────────────────────────────
        self.content_container = ctk.CTkFrame(
            self,
            fg_color=ThemeManager.get_color("bg"),
            corner_radius=0
        )
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def _get_frame_class(self, frame_name: str):
        """
        Lazy-import and return the frame class for a given module name.
        
        This avoids importing all frame modules at startup and allows
        new frames to be added without modifying the imports.

        Args:
            frame_name: Module identifier (e.g., 'home', 'crop', 'fertilizer')

        Returns:
            Frame class or None
        """
        frame_map = {
            "home": ("ui.frames.home_frame", "HomeFrame"),
            "crop": ("ui.frames.crop_frame", "CropFrame"),
            "fertilizer": ("ui.frames.fertilizer_frame", "FertilizerFrame"),
            "pesticide": ("ui.frames.pesticide_frame", "PesticideFrame"),
            "disease": ("ui.frames.disease_frame", "DiseaseFrame"),
            "yield": ("ui.frames.yield_frame", "YieldFrame"),
            "soil": ("ui.frames.soil_frame", "SoilFrame"),
            "irrigation": ("ui.frames.irrigation_frame", "IrrigationFrame"),
            "cost": ("ui.frames.cost_frame", "CostFrame"),
            "farm": ("ui.frames.farm_frame", "FarmFrame"),
            "reports": ("ui.frames.reports_frame", "ReportsFrame"),
            "settings": ("ui.frames.settings_frame", "SettingsFrame"),
            "about": ("ui.frames.about_frame", "AboutFrame"),
        }

        if frame_name not in frame_map:
            logger.warning(f"Unknown frame: {frame_name}")
            return None

        module_path, class_name = frame_map[frame_name]

        try:
            import importlib
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Frame '{frame_name}' not yet implemented: {e}")
            return None

    def show_frame(self, frame_name: str) -> None:
        """
        Switch the content area to display the requested module frame.

        Args:
            frame_name: Name of the frame to show
        """
        # Destroy the current frame
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

        # Get the frame class
        frame_class = self._get_frame_class(frame_name)

        if frame_class is not None:
            try:
                self.current_frame = frame_class(
                    master=self.content_container,
                    db=self.db_manager,
                    user=self.user,
                    prediction_service=self.prediction_service
                )
                self.current_frame.grid(row=0, column=0, sticky="nsew")
                logger.info(f"Switched to frame: {frame_name}")
            except TypeError:
                # Some frames may not accept prediction_service yet
                try:
                    self.current_frame = frame_class(
                        master=self.content_container,
                        db=self.db_manager,
                        user=self.user
                    )
                    self.current_frame.grid(row=0, column=0, sticky="nsew")
                    logger.info(f"Switched to frame: {frame_name} (legacy init)")
                except Exception as e:
                    logger.error(f"Failed to create frame '{frame_name}': {e}")
                    self._show_placeholder(frame_name)
        else:
            self._show_placeholder(frame_name)

        # Update sidebar active state
        self.sidebar.set_active(frame_name)

    def _show_placeholder(self, frame_name: str) -> None:
        """Show a placeholder for frames not yet implemented."""
        from ui.base_frame import ContentFrame

        display_name = frame_name.replace("_", " ").title()
        self.current_frame = ContentFrame(
            self.content_container,
            title=display_name,
            subtitle="Coming soon"
        )
        placeholder_label = ctk.CTkLabel(
            self.current_frame.content_area,
            text=f"🚧 {display_name} module is under construction.",
            font=ThemeManager.get_font("body"),
            text_color=ThemeManager.get_color("text_secondary")
        )
        placeholder_label.pack(pady=50)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _logout(self) -> None:
        """Handle logout action."""
        logger.info(f"User '{self.user.username}' logging out from dashboard")
        if self.on_logout_callback:
            self.on_logout_callback()
