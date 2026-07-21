import customtkinter as ctk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import ThemeManager

class ChartWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master, 
            fg_color=ThemeManager.get_color("card"),
            corner_radius=10,
            **kwargs
        )
        
        self.figure = None
        self.canvas = None
        
        # Setup dark theme for matplotlib based on app theme
        self._setup_matplotlib_theme()
        
    def _setup_matplotlib_theme(self):
        theme = ThemeManager.get_theme()
        bg_color = ThemeManager.get_color("card")
        text_color = ThemeManager.get_color("text")
        grid_color = ThemeManager.get_color("surface")
        
        matplotlib.rcParams.update({
            'figure.facecolor': bg_color,
            'axes.facecolor': bg_color,
            'axes.edgecolor': grid_color,
            'axes.labelcolor': text_color,
            'text.color': text_color,
            'xtick.color': text_color,
            'ytick.color': text_color,
            'grid.color': grid_color,
            'font.size': 10,
            'axes.titlesize': 12
        })
        
    def _create_canvas(self, fig):
        self.clear()
        self.figure = fig
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, padx=10, pady=10)
        
    def clear(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure:
            self.figure.clf()
            self.figure = None
            
    def create_bar_chart(self, data, labels, title, colors=None):
        if not colors:
            colors = [ThemeManager.get_color("primary")] * len(data)
            
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.bar(labels, data, color=colors)
        ax.set_title(title)
        ax.tick_params(axis='x', rotation=45 if len(labels) > 4 else 0)
        fig.tight_layout()
        
        self._create_canvas(fig)
        
    def create_pie_chart(self, data, labels, title, colors=None):
        if not colors:
            colors = [
                ThemeManager.get_color("primary"),
                ThemeManager.get_color("accent"),
                ThemeManager.get_color("warning"),
                ThemeManager.get_color("error"),
                "#8E24AA", "#039BE5"
            ]
            
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(title)
        fig.tight_layout()
        
        self._create_canvas(fig)
        
    def create_line_chart(self, x_data, y_data, title):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(x_data, y_data, marker='o', linestyle='-', color=ThemeManager.get_color("primary"))
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.7)
        fig.tight_layout()
        
        self._create_canvas(fig)
        
    def create_radar_chart(self, categories, values, title):
        import numpy as np
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, polar=True)
        
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        values_loop = list(values)
        values_loop += values_loop[:1]
        
        ax.plot(angles, values_loop, linewidth=2, linestyle='solid', color=ThemeManager.get_color("primary"))
        ax.fill(angles, values_loop, alpha=0.25, color=ThemeManager.get_color("primary"))
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(title, y=1.1)
        fig.tight_layout()
        
        self._create_canvas(fig)
