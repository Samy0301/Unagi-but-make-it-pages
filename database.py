"""Capa de persistencia JSON."""
import json
import os
import threading
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════════
#  PALETA DE COLORES - PLAYA & CIELO
# ═══════════════════════════════════════════════════════════════════
PALETA = {
    "bg_main": "#C8E0F0",
    "bg_panel": "#A8D4E8",
    "bg_card": "#E0F0F5",
    "bg_input": "#F0F8FB",
    "bg_header": "#8FB8D8",
    "bg_dark": "#0F3A5C",
    "ocean": "#1E6BA8",
    "sky": "#3D8BC8",
    "sand": "#E89C20",
    "sun": "#E08000",
    "coral": "#D06010",
    "seafoam": "#2AB8B0",
    "wave_dark": "#0F3A5C",
    "sand_light": "#F0D060",
    "rose": "#F0B0A8",
    "text_main": "#1A2D3D",
    "text_secondary": "#3D6A88",
    "text_light": "#C8E0F0",
    "text_muted": "#607080",
    "border": "#88B8D8",
    "border_accent": "#3D8BC8",
    "shadow": "#A0B0B8",
}

DATA_FILE = "book_journal_data.json"


class Database:
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.data = self._load()
        self._version = 0
        self._timer = None
        self._lock = threading.Lock()
        self._ensure_structure()

    def _load(self):
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self):
        """Guarda inmediatamente a disco. Llamar al cerrar la app."""
        with self._lock:
            try:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except OSError as e:
                print(f"[Database] Error al guardar: {e}")

    def _schedule_save(self, delay=0.3):
        """Guardado diferido: si llegan 10 cambios en 300 ms, solo se escribe 1 vez."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(delay, self.save)
            self._timer.daemon = True
            self._timer.start()

    def _ensure_structure(self):
        defaults = {
            "books": [],
            "reviews": [],
            "tracker": {},
            "bookshelf": [],
            "reading_streaks": [],
            "current_streak": {"count": 0},
            "shelf_config": {"shelves": [140, 300, 460]},
            "challenges": {"reto_lector": {}, "collect_colors": {}, "bracket": {}}
        }
        changed = False
        for key, val in defaults.items():
            if key not in self.data:
                self.data[key] = val
                changed = True
        if changed:
            self.save()

    def get(self, key):
        return self.data.get(key, [])

    def set(self, key, value):
        self.data[key] = value
        self._version += 1
        self._schedule_save()

    def get_version(self):
        return self._version

    @staticmethod
    def generate_id():
        return datetime.now().isoformat()

    def get_tracker_dates(self):
        dates = set()
        tracker = self.get("tracker")
        for month_key, days in tracker.items():
            try:
                year, month = map(int, month_key.split("-"))
                for day_str, pages in days.items():
                    if pages and str(pages).isdigit() and int(pages) > 0:
                        dates.add(datetime(year, month, int(day_str)).date())
            except Exception:
                continue
        return dates

    def recalc_streaks(self):
        dates = sorted(self.get_tracker_dates())
        if not dates:
            self.set("current_streak", {"count": 0})
            self.set("reading_streaks", [])
            return

        streaks = []
        current_start = dates[0]
        current_end = dates[0]

        for i in range(1, len(dates)):
            if dates[i] == current_end + timedelta(days=1):
                current_end = dates[i]
            else:
                streaks.append({
                    "start": current_start.isoformat(),
                    "end": current_end.isoformat(),
                    "length": (current_end - current_start).days + 1
                })
                current_start = dates[i]
                current_end = dates[i]

        last_streak = {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "length": (current_end - current_start).days + 1
        }

        today = datetime.now().date()
        last_end = current_end

        if last_end < today - timedelta(days=1):
            streaks.append(last_streak)
            self.set("current_streak", {"count": 0})
        else:
            self.set("current_streak", {
                "start": last_streak["start"],
                "last_date": last_streak["end"],
                "count": last_streak["length"]
            })

        self.set("reading_streaks", streaks)