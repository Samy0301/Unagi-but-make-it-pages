"""Capa de persistencia JSON para Book Journal."""
import json
import os
from datetime import datetime

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
            "tbr": [],
            "challenges": []
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
