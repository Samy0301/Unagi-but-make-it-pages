"""Reading Tracker con dona, libros leyendo y rachas."""
import math
import calendar
import os
from datetime import date, datetime, timedelta

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkOptionMenu, CTkScrollableFrame
from tkinter import Canvas

from PIL import Image

try:
    from customtkinter import CTkImage
except ImportError:
    CTkImage = None

from database import Database, PALETA


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
        return "#C8E0F0"
    try:
        p = int(pages)
    except (ValueError, TypeError):
        return "#C8E0F0"
    if p <= 0:
        return "#C8E0F0"
    stops = [
        (1,   "#29B6F6"),
        (10,  "#00E5FF"),
        (20,  "#00E676"),
        (35,  "#76FF03"),
        (50,  "#FFEA00"),
        (70,  "#FF9100"),
        (90,  "#FF3D00"),
        (120, "#D500F9"),
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


MONTH_COLORS = {
    1:  "#00B0FF", 2:  "#E040FB", 3:  "#00E676", 4:  "#FFEA00",
    5:  "#FF9100", 6:  "#FF1744", 7:  "#D50000", 8:  "#FF6D00",
    9:  "#FFAB00", 10: "#651FFF", 11: "#3D5AFE", 12: "#00BFA5",
}

MONTH_NAMES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


class TrackerFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="Reading Tracker", font=("Helvetica", 28, "bold")).pack(pady=(15, 5))

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
        CTkOptionMenu(ctrl, values=[str(i) for i in range(2026, 2036)], variable=self.year_var, width=100).pack(side="left", padx=5)
        CTkButton(ctrl, text="Cargar", command=self.render_tracker, width=80).pack(side="left", padx=10)

        self.canvas = Canvas(left, width=520, height=520, bg="#D0EBF5", highlightthickness=0)
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
        CTkLabel(inp, text="Dia:").pack(side="left", padx=5)
        self.entry_day = CTkEntry(inp, width=50)
        self.entry_day.pack(side="left", padx=5)
        CTkLabel(inp, text="Paginas:").pack(side="left", padx=5)
        self.entry_pages = CTkEntry(inp, width=80)
        self.entry_pages.pack(side="left", padx=5)
        CTkButton(inp, text="Registrar", command=self.log_day).pack(side="left", padx=10)

        right = CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")

        CTkLabel(right, text="Leyendo ahora", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 5))
        self.reading_scroll = CTkScrollableFrame(right, width=280, height=180, fg_color="transparent")
        self.reading_scroll.pack(fill="x", pady=5)

        self.streak_frame = CTkFrame(right, corner_radius=10, border_width=2,
                                     border_color="#2E86C1", fg_color="#FFFFFF")
        self.streak_frame.pack(fill="x", pady=15)
        self.streak_label = CTkLabel(self.streak_frame, text="Racha actual: 0 dias", font=("Arial", 14, "bold"))
        self.streak_label.pack(pady=10)

        CTkLabel(right, text="Historial de rachas", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(5, 5))
        self.streaks_scroll = CTkScrollableFrame(right, width=280, height=200, fg_color="transparent")
        self.streaks_scroll.pack(fill="x", pady=5)

        self.render_tracker()
        self.render_reading()
        self.render_streaks()

    def _load_cover_mini(self, path, size=(35, 50)):
        if not path or not os.path.exists(path):
            return None
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            if CTkImage:
                return CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            pass
        return None

    def render_reading(self):
        """Render simple sin pool: tipicamente 0-3 libros."""
        for w in list(self.reading_scroll.winfo_children()):
            w.destroy()

        books = [b for b in self.db.get("books") if b.get("estado") == "leyendo"]
        if not books:
            CTkLabel(self.reading_scroll, text="No estas leyendo nada ahora.", font=("Arial", 11)).pack(pady=10)
            return

        for b in books:
            row = CTkFrame(self.reading_scroll, corner_radius=10, border_width=1,
                           height=70, border_color="#2E86C1", fg_color="#FFFFFF")
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)

            cover = CTkFrame(row, width=35, height=50, corner_radius=4, fg_color="#FFFFFF")
            cover.pack(side="left", padx=(10, 8), pady=10)
            cover.pack_propagate(False)
            img = self._load_cover_mini(b.get("foto"))
            if img:
                CTkLabel(cover, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
            else:
                CTkLabel(cover, text="Libro", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")

            text_frame = CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="y", expand=True, pady=8)
            CTkLabel(text_frame, text=b.get("titulo", "Sin titulo"), font=("Arial", 12, "bold")).pack(anchor="w")
            CTkLabel(text_frame, text=b.get("autor", ""), font=("Arial", 10), text_color="#5DADE2").pack(anchor="w")

    def render_streaks(self):
        self.db.recalc_streaks()
        current = self.db.get("current_streak")
        count = current.get("count", 0) if current else 0
        self.streak_label.configure(
            text=f"Racha actual: {count} dias" if count > 0 else "Racha actual: 0 dias"
        )

        for w in list(self.streaks_scroll.winfo_children()):
            w.destroy()

        streaks = self.db.get("reading_streaks")
        if not streaks:
            CTkLabel(self.streaks_scroll, text="Aun no hay rachas registradas.", font=("Arial", 11)).pack(pady=10)
            return

        for s in reversed(streaks):
            row = CTkFrame(self.streaks_scroll, corner_radius=8, border_width=1)
            row.pack(fill="x", pady=3)
            start = datetime.fromisoformat(s["start"]).strftime("%d/%m/%Y")
            end = datetime.fromisoformat(s["end"]).strftime("%d/%m/%Y")
            CTkLabel(row, text=f"{start} -> {end}", font=("Arial", 10)).pack(side="left", padx=10, pady=5)
            CTkLabel(row, text=f"{s['length']} dias", font=("Arial", 10, "bold")).pack(side="right", padx=10, pady=5)

    def render_tracker(self):
        self.canvas.delete("all")
        cx, cy = 260, 260
        r_outer, r_inner = 220, 150

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        days_in_month = calendar.monthrange(year, month)[1]
        tracker_data = self.db.get("tracker").get(f"{year}-{month:02d}", {})
        month_color = MONTH_COLORS.get(month, "#FFFFFF")

        # Anillo decorativo
        self.canvas.create_oval(cx - r_outer - 8, cy - r_outer - 8,
                                cx + r_outer + 8, cy + r_outer + 8,
                                fill="", outline=month_color, width=4)

        angle_per_day = 360 / days_in_month

        for day in range(1, days_in_month + 1):
            angle_start = (day - 1) * angle_per_day - 90
            angle_end = day * angle_per_day - 90

            pages = tracker_data.get(str(day), 0)
            color = color_for_pages(pages)

            self._draw_arc(cx, cy, r_outer, r_inner, angle_start, angle_end, color)

            mid_angle = (angle_start + angle_end) / 2
            rad = (r_outer + r_inner) / 2
            x = cx + rad * 0.85 * math.cos(math.radians(mid_angle))
            y = cy + rad * 0.85 * math.sin(math.radians(mid_angle))

            self.canvas.create_text(x, y, text=str(day), fill="#2C3E50", font=("Arial", 9, "bold"))

            if pages and str(pages).isdigit() and int(pages) > 0:
                x2 = cx + (r_inner - 25) * math.cos(math.radians(mid_angle))
                y2 = cy + (r_inner - 25) * math.sin(math.radians(mid_angle))
                self.canvas.create_text(x2, y2, text=str(pages), fill="#2C3E50",
                                        font=("Arial", 8, "bold"))

        # Circulo central
        self.canvas.create_oval(cx - 70, cy - 70, cx + 70, cy + 70,
                                fill=month_color, outline="#2E86C1", width=2)
        total = sum(int(v) for v in tracker_data.values() if str(v).isdigit())

        self.canvas.create_text(cx, cy - 18, text=MONTH_NAMES.get(month, ""),
                                fill="#2C3E50", font=("Arial", 16, "bold"))
        self.canvas.create_text(cx, cy + 12, text=f"{total} pag.", fill="#2C3E50",
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
        if not day.isdigit() or not pages.isdigit():
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

    def refresh(self):
        self.render_tracker()
        self.render_reading()
        self.render_streaks()