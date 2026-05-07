"""Capa de persistencia JSON."""
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "book_journal_data.json"


class Database:
    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        self.data = self._load()
        self._ensure_structure()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def _ensure_structure(self):
        defaults = {
            "books": [],
            "reviews": [],
            "tracker": {},
            "bookshelf": [],
            "reading_streaks": [],
            "current_streak": None
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
        self.save()

    @staticmethod
    def generate_id():
        return datetime.now().isoformat()

    # --- helpers para rachas ---
    def get_tracker_dates(self):
        """Devuelve set de fechas (date) con lectura registrada."""
        dates = set()
        tracker = self.get("tracker")
        for month_key, days in tracker.items():
            try:
                year, month = map(int, month_key.split("-"))
                for day_str, pages in days.items():
                    if pages and int(pages) > 0:
                        dates.add(datetime(year, month, int(day_str)).date())
            except Exception:
                continue
        return dates

    def recalc_streaks(self):
        """Recalcula rachas históricas y la racha actual."""
        dates = sorted(self.get_tracker_dates())
        if not dates:
            self.set("current_streak", None)
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

        streaks.append({
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "length": (current_end - current_start).days + 1
        })

        # La última racha es la actual si incluye hoy o ayer
        today = datetime.now().date()
        last = streaks[-1]
        last_end = datetime.fromisoformat(last["end"]).date()
        if last_end >= today - timedelta(days=1):
            self.set("current_streak", {
                "start": last["start"],
                "last_date": last["end"],
                "count": last["length"]
            })
            streaks = streaks[:-1]
        else:
            self.set("current_streak", None)

        self.set("reading_streaks", streaks)
