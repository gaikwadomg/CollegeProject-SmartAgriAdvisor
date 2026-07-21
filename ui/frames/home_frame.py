"""
AgriSense AI - Home Frame (Dashboard Home)
=============================================

Main dashboard home page showing summary stats, quick actions,
and recent activity. This is the first screen users see after login.

Author: AgriSense AI Team
"""

import customtkinter as ctk
from datetime import datetime

from ui.base_frame import ContentFrame
from ui.theme import ThemeManager
from ui.components.card import StatCard
from database.models import Prediction, Farm, DiseaseRecord
from utils.logger import get_logger

logger = get_logger(__name__)


class HomeFrame(ContentFrame):
    """
    Dashboard home page with stat cards, quick actions, and recent activity.
    """

    def __init__(self, master, db, user, prediction_service=None, **kwargs):
        """
        Initialize the home frame.

        Args:
            master: Parent widget
            db: DatabaseManager instance
            user: Current User object
            prediction_service: Optional PredictionService instance
        """
        super().__init__(
            master,
            title=f"Welcome back, {user.username}! 👋",
            subtitle=datetime.now().strftime("%A, %B %d, %Y"),
            **kwargs
        )
        self.db = db
        self.user = user
        self.prediction_service = prediction_service

        self._load_data()
        self._build_content()

    def _load_data(self) -> None:
        """Load dashboard statistics from the database."""
        self.total_predictions = 0
        self.total_farms = 0
        self.healthy_crops = 0
        self.disease_cases = 0
        self.recent_activity = []

        try:
            with self.db.get_session() as session:
                self.total_predictions = (
                    session.query(Prediction)
                    .filter_by(user_id=self.user.id)
                    .count()
                )
                self.total_farms = (
                    session.query(Farm)
                    .filter_by(user_id=self.user.id)
                    .count()
                )

                # Disease stats
                self.disease_cases = (
                    session.query(DiseaseRecord)
                    .filter_by(user_id=self.user.id)
                    .filter(~DiseaseRecord.disease_name.ilike("%healthy%"))
                    .count()
                )
                self.healthy_crops = (
                    session.query(DiseaseRecord)
                    .filter_by(user_id=self.user.id)
                    .filter(DiseaseRecord.disease_name.ilike("%healthy%"))
                    .count()
                )

                # Recent predictions
                recent = (
                    session.query(Prediction)
                    .filter_by(user_id=self.user.id)
                    .order_by(Prediction.created_at.desc())
                    .limit(10)
                    .all()
                )
                self.recent_activity = [
                    {
                        "type": p.prediction_type,
                        "confidence": p.confidence,
                        "created_at": p.created_at,
                        "result_data": p.result_data,
                    }
                    for p in recent
                ]
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")

    def _build_content(self) -> None:
        """Build the dashboard home UI."""
        # ── Stat Cards Row ────────────────────────────────────────────
        stats_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)

        cards_data = [
            ("Total Predictions", str(self.total_predictions), "📊", "#039BE5"),
            ("Registered Farms", str(self.total_farms), "🏡", "#43A047"),
            ("Healthy Crops", str(self.healthy_crops), "🌿", "#00897B"),
            ("Disease Cases", str(self.disease_cases), "🍂", "#EF5350"),
        ]

        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(
                stats_frame,
                title=title,
                value=value,
                icon_text=icon,
                color=color,
                trend_text=""
            )
            card.grid(row=0, column=i, padx=8, sticky="ew")

        # ── Bottom Section: Quick Actions + Recent Activity ───────────
        bottom_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=2)
        bottom_frame.grid_columnconfigure(1, weight=3)
        bottom_frame.grid_rowconfigure(0, weight=1)

        # ── Quick Actions Card ────────────────────────────────────────
        actions_card = ctk.CTkFrame(
            bottom_frame,
            fg_color=ThemeManager.get_color("card"),
            corner_radius=12
        )
        actions_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        actions_title = ctk.CTkLabel(
            actions_card,
            text="⚡ Quick Actions",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        actions_title.pack(pady=(15, 10), padx=15, anchor="w")

        actions_grid = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_grid.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        actions_grid.grid_columnconfigure(0, weight=1)
        actions_grid.grid_columnconfigure(1, weight=1)

        actions = [
            ("🌾 Predict Crop", "crop"),
            ("🌍 Check Soil", "soil"),
            ("🍂 Detect Disease", "disease"),
            ("📊 Estimate Yield", "yield"),
            ("💰 Calc Profit", "cost"),
            ("📄 Gen Report", "reports"),
        ]

        for i, (text, target) in enumerate(actions):
            btn = ctk.CTkButton(
                actions_grid,
                text=text,
                font=ThemeManager.get_font("body"),
                fg_color=ThemeManager.get_color("surface"),
                text_color=ThemeManager.get_color("text"),
                hover_color=ThemeManager.get_color("primary"),
                height=50,
                corner_radius=8,
                command=lambda t=target: self._navigate_to(t)
            )
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="ew")

        # ── Recent Activity Card ──────────────────────────────────────
        activity_card = ctk.CTkFrame(
            bottom_frame,
            fg_color=ThemeManager.get_color("card"),
            corner_radius=12
        )
        activity_card.grid(row=0, column=1, sticky="nsew")

        activity_title = ctk.CTkLabel(
            activity_card,
            text="📋 Recent Activity",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        activity_title.pack(pady=(15, 10), padx=15, anchor="w")

        if not self.recent_activity:
            empty_frame = ctk.CTkFrame(activity_card, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True)
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No recent activity yet.\nStart by making your first prediction! 🌱",
                font=ThemeManager.get_font("body"),
                text_color=ThemeManager.get_color("text_secondary"),
                justify="center"
            )
            empty_label.pack(expand=True)
        else:
            list_frame = ctk.CTkScrollableFrame(
                activity_card,
                fg_color="transparent"
            )
            list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            for item in self.recent_activity:
                item_frame = ctk.CTkFrame(
                    list_frame,
                    fg_color=ThemeManager.get_color("surface"),
                    corner_radius=6
                )
                item_frame.pack(fill="x", pady=2)

                # Type badge
                type_display = item["type"].replace("_", " ").title()
                type_lbl = ctk.CTkLabel(
                    item_frame,
                    text=type_display,
                    font=ThemeManager.get_font("caption"),
                    text_color=ThemeManager.get_color("primary"),
                    width=140
                )
                type_lbl.pack(side="left", padx=10, pady=8)

                # Confidence
                conf = item.get("confidence")
                if conf is not None:
                    conf_lbl = ctk.CTkLabel(
                        item_frame,
                        text=f"{conf*100:.0f}%",
                        font=ThemeManager.get_font("caption"),
                        text_color=ThemeManager.get_color("accent")
                    )
                    conf_lbl.pack(side="left", padx=5)

                # Date
                created = item.get("created_at")
                if created:
                    date_str = created.strftime("%d %b, %I:%M %p")
                    date_lbl = ctk.CTkLabel(
                        item_frame,
                        text=date_str,
                        font=ThemeManager.get_font("caption"),
                        text_color=ThemeManager.get_color("text_secondary")
                    )
                    date_lbl.pack(side="right", padx=10)

    def _navigate_to(self, target: str) -> None:
        """
        Navigate to a different frame via the parent Dashboard.

        Args:
            target: Frame name to navigate to
        """
        # Walk up the widget tree to find the Dashboard
        current = self.master
        while current and not hasattr(current, 'show_frame'):
            current = current.master

        if current and hasattr(current, 'show_frame'):
            if hasattr(current, 'sidebar'):
                current.sidebar.set_active(target)
            current.show_frame(target)
