"""Widgets reutilizables."""
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel
from database import PALETA


class StarRating(CTkFrame):
    def __init__(self, master, rating=0, command=None, size=20, readonly=False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.rating = rating
        self.command = command
        self.readonly = readonly
        self.stars = []

        for i in range(5):
            lbl = CTkLabel(self, text="☆", font=("Arial", size), 
                          text_color=PALETA["coral"])
            if not readonly:
                lbl.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx + 1))
            lbl.pack(side="left", padx=2)
            self.stars.append(lbl)

        self.update_stars()

    def set_rating(self, value):
        self.rating = value
        self.update_stars()
        if self.command and not self.readonly:
            self.command(value)

    def update_stars(self):
        for i, lbl in enumerate(self.stars):
            lbl.configure(text="★" if i < self.rating else "☆")