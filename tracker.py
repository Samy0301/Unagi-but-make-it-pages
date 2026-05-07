"""Reading Tracker con dona, libros leyendo y rachas."""
import math
import calendar
from datetime import date, datetime, timedelta

import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkOptionMenu, CTkScrollableFrame
)
from tkinter import Canvas

from database import Database


def lerp_color(c1, c2, t):
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t)
    )


def color_for_pages(pages):
    if pages == 0 or pages == "None" or pages == "":
        return "#1f1f1f"
    try:
        p = int(pages)
    except (ValueError, TypeError):
        return "#1f1f1f"
    if p <= 0:
        return "#1f1f1f"
    stops = [
        (1,   "#3a3a5c"),
        (10,  "#3498db"),
        (30,  "#2ecc71"),
        (50,  "#f1c40f"),
        (80,  "#e67e22"),
        (120, "#e74c3c"),
    ]
    if p >= stops[-1][0]:
        return stops[-1][1]
    for i in range(len(stops) - 1):
        low, c_low = stops[i]
        high, c_high = stops[i + 1]
        if low <= p <= high:
            t = (p - low) / (high - low)
            return lerp_color(c_low, c_high, t)
    return stops[0][1]


class TrackerFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="📅 Reading Tracker", font=("Helvetica", 28, "bold")).pack(pady=(15, 5))

        main = CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        left = CTkFrame(main, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        ctrl = CTkFrame(left, fg_color="transparent")
        ctrl.pack(pady=5)
        self.month_var = ctk.StringVar(value=str(date.today().month))
        self.year_var = ctk.StringVar(value=str(date.today().year))
        CTkOptionMenu(ctrl, values=[str(i) for i in range(1, 13)], variable=self.month_var, width=80).pack(side="left", padx=5)
        CTkOptionMenu(ctrl, values=[str(i) for i in range(2024, 2031)], variable=self.year_var, width=100).pack(side="left", padx=5)
        CTkButton(ctrl, text="Cargar", command=self.render_tracker, width=80).pack(side="left", padx=10)

        self.canvas = Canvas(left, width=520, height=520, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=10)

        legend = CTkFrame(left, fg_color="transparent")
        legend.pack(pady=5)
        samples = [1, 10, 30, 50, 80, 120]
        for p in samples:
            c = color_for_pages(p)
            box = CTkFrame(legend, width=25, height=15, fg_color=c, corner_radius=3)
            box.pack(side="left", padx=2)
            CTkLabel(legend, text=f"{p}", font=("Arial", 9)).pack(side="left", padx=(0, 10))

        inp = CTkFrame(left, fg_color="transparent")
        inp.pack(pady=10)
        CTkLabel(inp, text="Día:").pack(side="left", padx=5)
        self.entry_day = CTkEntry(inp, width=50)
        self.entry_day.pack(side="left", padx=5)
        CTkLabel(inp, text="Páginas:").pack(side="left", padx=5)
        self.entry_pages = CTkEntry(inp, width=80)
        self.entry_pages.pack(side="left", padx=5)
        CTkButton(inp, text="Registrar", command=self.log_day).pack(side="left", padx=10)

        right = CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")

        CTkLabel(right, text="📖 Leyendo ahora", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 5))
        self.reading_scroll = CTkScrollableFrame(right, width=280, height=180, fg_color="transparent")
        self.reading_scroll.pack(fill="x", pady=5)

        self.streak_frame = CTkFrame(right, corner_radius=10, border_width=2)
        self.streak_frame.pack(fill="x", pady=15)
        self.streak_label = CTkLabel(self.streak_frame, text="🔥 Racha actual: 0 días", font=("Arial", 14, "bold"))
        self.streak_label.pack(pady=10)

        CTkLabel(right, text="📜 Historial de rachas", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(5, 5))
        self.streaks_scroll = CTkScrollableFrame(right, width=280, height=200, fg_color="transparent")
        self.streaks_scroll.pack(fill="x", pady=5)

        self.render_tracker()
        self.render_reading()
        self.render_streaks()

    def render_reading(self):
        for w in self.reading_scroll.winfo_children():
            w.destroy()
        books = [b for b in self.db.get("books") if b.get("estado") == "leyendo"]
        if not books:
            CTkLabel(self.reading_scroll, text="No estás leyendo nada ahora.", font=("Arial", 11)).pack(pady=10)
            return
        for b in books:
            row = CTkFrame(self.reading_scroll, corner_radius=8, border_width=1)
            row.pack(fill="x", pady=3)
            CTkLabel(row, text=b.get("titulo", ""), font=("Arial", 11, "bold")).pack(side="left", padx=10, pady=5)

    def render_streaks(self):
        self.db.recalc_streaks()
        current = self.db.get("current_streak")
        if current:
            self.streak_label.configure(text=f"🔥 Racha actual: {current['count']} días")
        else:
            self.streak_label.configure(text="🔥 Sin racha activa")

        for w in self.streaks_scroll.winfo_children():
            w.destroy()

        streaks = self.db.get("reading_streaks")
        if not streaks:
            CTkLabel(self.streaks_scroll, text="Aún no hay rachas registradas.", font=("Arial", 11)).pack(pady=10)
            return
        for s in reversed(streaks):
            row = CTkFrame(self.streaks_scroll, corner_radius=8, border_width=1)
            row.pack(fill="x", pady=3)
            start = datetime.fromisoformat(s["start"]).strftime("%d/%m/%Y")
            end = datetime.fromisoformat(s["end"]).strftime("%d/%m/%Y")
            CTkLabel(row, text=f"{start} → {end}", font=("Arial", 10)).pack(side="left", padx=10, pady=5)
            CTkLabel(row, text=f"{s['length']} días", font=("Arial", 10, "bold")).pack(side="right", padx=10, pady=5)

    def render_tracker(self):
        self.canvas.delete("all")
        cx, cy = 260, 260
        r_outer, r_inner = 220, 150

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        days_in_month = calendar.monthrange(year, month)[1]
        tracker_data = self.db.get("tracker").get(f"{year}-{month:02d}", {})

        for day in range(1, days_in_month + 1):
            angle_start = (day - 1) * (360 / days_in_month) - 90
            angle_end = day * (360 / days_in_month) - 90

            pages = tracker_data.get(str(day), 0)
            color = color_for_pages(pages)

            self._draw_arc(cx, cy, r_outer, r_inner, angle_start, angle_end, color)

            mid_angle = (angle_start + angle_end) / 2
            rad = (r_outer + r_inner) / 2
            x = cx + rad * 0.85 * math.cos(math.radians(mid_angle))
            y = cy + rad * 0.85 * math.sin(math.radians(mid_angle))

            self.canvas.create_text(x, y, text=str(day), fill="white", font=("Arial", 9, "bold"))

            if pages and str(pages).isdigit() and int(pages) > 0:
                x2 = cx + (r_inner - 25) * math.cos(math.radians(mid_angle))
                y2 = cy + (r_inner - 25) * math.sin(math.radians(mid_angle))
                self.canvas.create_text(x2, y2, text=str(pages), fill="white",
                                        font=("Arial", 8, "bold"))

        self.canvas.create_oval(cx - 70, cy - 70, cx + 70, cy + 70,
                                fill="#2b2b2b", outline="#444", width=2)
        total = sum(int(v) for v in tracker_data.values() if str(v).isdigit())
        self.canvas.create_text(cx, cy - 10, text="📚", font=("Arial", 30))
        self.canvas.create_text(cx, cy + 25, text=f"{total} pág.", fill="white",
                                font=("Arial", 11, "bold"))

    def _draw_arc(self, cx, cy, r_out, r_in, a1, a2, color):
        points = []
        steps = 24
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
        if not pages.isdigit():
            return
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        key = f"{year}-{month:02d}"
        tracker = self.db.get("tracker")
        if key not in tracker:
            tracker[key] = {}
        tracker[key][day] = int(pages)
        self.db.set("tracker", tracker)
        self.db.recalc_streaks()
        self.render_tracker()
        self.render_streaks()