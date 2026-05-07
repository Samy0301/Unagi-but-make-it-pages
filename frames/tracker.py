"""Reading Tracker circular por mes."""
import math
import calendar
from datetime import date

import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkOptionMenu
)
from tkinter import Canvas

from database import Database


class TrackerFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(
            self, text="📅 Reading Tracker", font=("Helvetica", 28, "bold")
        ).pack(pady=(20, 10))

        # Selector mes/año
        ctrl = CTkFrame(self, fg_color="transparent")
        ctrl.pack(pady=10)

        self.month_var = ctk.StringVar(value=str(date.today().month))
        self.year_var = ctk.StringVar(value=str(date.today().year))

        CTkOptionMenu(
            ctrl, values=[str(i) for i in range(1, 13)],
            variable=self.month_var, width=80
        ).pack(side="left", padx=5)
        CTkOptionMenu(
            ctrl, values=[str(i) for i in range(2024, 2031)],
            variable=self.year_var, width=100
        ).pack(side="left", padx=5)
        CTkButton(ctrl, text="Cargar", command=self.render_tracker, width=80).pack(
            side="left", padx=10
        )

        # Canvas para tracker circular
        self.canvas = Canvas(
            self, width=600, height=600, bg="#1a1a1a", highlightthickness=0
        )
        self.canvas.pack(pady=20)

        # Leyenda
        legend = CTkFrame(self, fg_color="transparent")
        legend.pack(pady=10)
        colors = [
            ("#3a3a3a", "0-10"), ("#5c5c5c", "11-20"), ("#7e7e7e", "21-40"),
            ("#a0a0a0", "41-70"), ("#c2c2c2", "70+"), ("#1f1f1f", "Nada")
        ]
        for col, label in colors:
            box = CTkFrame(legend, width=20, height=20, fg_color=col, corner_radius=4)
            box.pack(side="left", padx=5)
            CTkLabel(legend, text=label, font=("Arial", 10)).pack(
                side="left", padx=(0, 15)
            )

        # Panel de entrada rápida
        self.input_frame = CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=10)
        CTkLabel(self.input_frame, text="Día:").pack(side="left", padx=5)
        self.entry_day = CTkEntry(self.input_frame, width=50)
        self.entry_day.pack(side="left", padx=5)
        CTkLabel(self.input_frame, text="Páginas:").pack(side="left", padx=5)
        self.entry_pages = CTkEntry(self.input_frame, width=80)
        self.entry_pages.pack(side="left", padx=5)
        CTkButton(
            self.input_frame, text="Registrar", command=self.log_day
        ).pack(side="left", padx=10)

        self.render_tracker()

    def render_tracker(self):
        self.canvas.delete("all")

        cx, cy = 300, 300
        r_outer, r_inner = 250, 180

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        days_in_month = calendar.monthrange(year, month)[1]

        tracker_data = self.db.get("tracker").get(f"{year}-{month:02d}", {})

        for day in range(1, days_in_month + 1):
            angle_start = (day - 1) * (360 / days_in_month) - 90
            angle_end = day * (360 / days_in_month) - 90

            pages = tracker_data.get(str(day), 0)
            color = self._color_for_pages(pages)

            self._draw_arc(cx, cy, r_outer, r_inner, angle_start, angle_end, color)

            mid_angle = (angle_start + angle_end) / 2
            rad = (r_outer + r_inner) / 2
            x = cx + rad * 0.85 * math.cos(math.radians(mid_angle))
            y = cy + rad * 0.85 * math.sin(math.radians(mid_angle))

            self.canvas.create_text(
                x, y, text=str(day), fill="white", font=("Arial", 10, "bold")
            )

        # Centro decorativo
        self.canvas.create_oval(
            cx - 80, cy - 80, cx + 80, cy + 80,
            fill="#2b2b2b", outline="#444", width=2
        )
        self.canvas.create_text(cx, cy, text="📚\n🌸", font=("Arial", 40))

    def _color_for_pages(self, pages):
        if pages == 0 or pages == "None":
            return "#1f1f1f"
        p = int(pages)
        if p <= 10:
            return "#3a3a3a"
        if p <= 20:
            return "#5c5c5c"
        if p <= 40:
            return "#7e7e7e"
        if p <= 70:
            return "#a0a0a0"
        return "#c2c2c2"

    def _draw_arc(self, cx, cy, r_out, r_in, a1, a2, color):
        points = []
        steps = 20
        for i in range(steps + 1):
            a = math.radians(a1 + (a2 - a1) * i / steps)
            points.append(cx + r_out * math.cos(a))
            points.append(cy + r_out * math.sin(a))
        for i in range(steps + 1):
            a = math.radians(a2 - (a2 - a1) * i / steps)
            points.append(cx + r_in * math.cos(a))
            points.append(cy + r_in * math.sin(a))
        self.canvas.create_polygon(points, fill=color, outline="")

    def log_day(self):
        day = self.entry_day.get().strip()
        pages = self.entry_pages.get().strip()
        if not day.isdigit():
            return
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        key = f"{year}-{month:02d}"
        tracker = self.db.get("tracker")
        if key not in tracker:
            tracker[key] = {}
        tracker[key][day] = pages
        self.db.set("tracker", tracker)
        self.render_tracker()
