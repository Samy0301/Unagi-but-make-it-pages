"""Widgets reutilizables."""
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel


class StarRating(CTkFrame):
    def __init__(self, master, rating=0, command=None, size=20, readonly=False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.rating = rating
        self.command = command
        self.size = size
        self.readonly = readonly
        self.stars = []
        for i in range(5):
            lbl = CTkLabel(self, text="☆", font=("Arial", size), text_color="gold")
            if not readonly:
                lbl.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx + 1))
            lbl.pack(side="left", padx=2)
            self.stars.append(lbl)
        self.update_stars()

    def set_rating(self, value):
        if self.readonly:
            return
        self.rating = value
        self.update_stars()
        if self.command:
            self.command(value)

    def update_stars(self):
        for i, lbl in enumerate(self.stars):
            lbl.configure(text="★" if i < self.rating else "☆")


class IconRating(CTkFrame):
    def __init__(self, master, icon="♥", max_val=5, value=0, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.value = value
        self.icon = icon
        self.labels = []
        for i in range(max_val):
            lbl = CTkLabel(self, text=icon, font=("Arial", 18), text_color="gray")
            lbl.bind("<Button-1>", lambda e, idx=i: self.set_value(idx + 1))
            lbl.pack(side="left", padx=3)
            self.labels.append(lbl)
        self.update_ui()

    def set_value(self, v):
        self.value = v
        self.update_ui()

    def update_ui(self):
        for i, lbl in enumerate(self.labels):
            lbl.configure(text_color="#ff6b6b" if i < self.value else "gray")