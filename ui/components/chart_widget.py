"""
AgriSense AI - Chart Widget
=============================

Matplotlib chart wrapper for CustomTkinter with dark/light theme support.
Includes graceful fallback if Matplotlib backend (_tkagg) is unavailable.

Author: AgriSense AI Team
"""

import customtkinter as ctk
from ui.theme import ThemeManager

HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False


class ChartWidget(ctk.CTkFrame):
    """
    Frame component for embedding Matplotlib charts in CustomTkinter.
    """

    def __init__(self, master, title="", **kwargs):
        super().__init__(
            master,
            fg_color=ThemeManager.get_color("card"),
            corner_radius=10,
            **kwargs
        )
        self.figure = None
        self.canvas = None
        self.title = title

    def clear(self):
        """Clear existing chart elements."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        for widget in self.winfo_children():
            widget.destroy()

    def _show_fallback(self, title, data_dict):
        """Display a formatted text summary when matplotlib backend is unavailable."""
        self.clear()
        title_lbl = ctk.CTkLabel(
            self,
            text=f"📊 {title}",
            font=ThemeManager.get_font("subheading"),
            text_color=ThemeManager.get_color("text")
        )
        title_lbl.pack(pady=(15, 10), padx=15, anchor="w")

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for k, v in data_dict.items():
            row = ctk.CTkFrame(content_frame, fg_color=ThemeManager.get_color("surface"), corner_radius=6)
            row.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(row, text=str(k), font=ThemeManager.get_font("body"), text_color=ThemeManager.get_color("text_secondary"))
            lbl.pack(side="left", padx=10, pady=6)
            val = ctk.CTkLabel(row, text=str(v), font=ThemeManager.get_font("body"), text_color=ThemeManager.get_color("primary"))
            val.pack(side="right", padx=10, pady=6)

    def create_bar_chart(self, data, labels, title="Chart", colors=None):
        """Create a vertical bar chart."""
        if not HAS_MATPLOTLIB:
            self._show_fallback(title, dict(zip(labels, data)))
            return

        self.clear()
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        bg_color = ThemeManager.get_color("card")
        text_color = ThemeManager.get_color("text")
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        bar_colors = colors or [ThemeManager.get_color("primary")] * len(data)
        ax.bar(labels, data, color=bar_colors)
        ax.set_title(title, color=text_color, fontsize=11, fontweight='bold')
        ax.tick_params(colors=text_color, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(text_color)
            spine.set_alpha(0.3)

        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_pie_chart(self, data, labels, title="Chart", colors=None):
        """Create a pie chart."""
        if not HAS_MATPLOTLIB:
            self._show_fallback(title, dict(zip(labels, data)))
            return

        self.clear()
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        bg_color = ThemeManager.get_color("card")
        text_color = ThemeManager.get_color("text")
        fig.patch.set_facecolor(bg_color)

        pie_colors = colors or ['#4CAF50', '#42A5F5', '#FF7043', '#AB47BC', '#FFA726']
        wedges, texts, autotexts = ax.pie(
            data,
            labels=labels,
            autopct='%1.1f%%',
            colors=pie_colors[:len(data)],
            textprops={'color': text_color, 'fontsize': 8}
        )
        ax.set_title(title, color=text_color, fontsize=11, fontweight='bold')
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
