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
        self._version = 0

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"[Database] Error al guardar: {e}")

    def _ensure_structure(self):
        defaults = {
            "books": [],
            "reviews": [],
            "tracker": {},
            "bookshelf": [],
            "reading_streaks": [],
            "current_streak": {"count": 0},
            "tbr": [],
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
        self.save()

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