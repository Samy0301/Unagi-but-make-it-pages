"""To Be Read list."""
from datetime import datetime

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkScrollableFrame
from tkinter import messagebox

from database import Database


class TBRFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(
            self, text="🎯 TBR - To Be Read", font=("Helvetica", 28, "bold")
        ).pack(pady=(20, 10))

        top = CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        self.entry_tbr = CTkEntry(
            top, width=400, placeholder_text="Título del libro..."
        )
        self.entry_tbr.pack(side="left", padx=5)
        CTkButton(top, text="+ Añadir a TBR", command=self.add_tbr).pack(
            side="left", padx=5
        )

        self.scroll = CTkScrollableFrame(
            self, width=900, height=550, fg_color="transparent"
        )
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render()

    def render(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        tbr_list = self.db.get("tbr")
        if not tbr_list:
            CTkLabel(
                self.scroll, text="Tu TBR está vacío 📭", font=("Arial", 16)
            ).pack(pady=50)
            return

        for item in tbr_list:
            row = CTkFrame(self.scroll, corner_radius=10, border_width=1)
            row.pack(fill="x", pady=5, padx=5)
            CTkLabel(row, text=item["titulo"], font=("Arial", 14, "bold")).pack(
                side="left", padx=15, pady=10
            )
            CTkLabel(row, text=item.get("fecha_add", ""), font=("Arial", 10)).pack(
                side="left", padx=10
            )
            CTkButton(
                row, text="✓ Leído", width=80,
                command=lambda i=item: self.mark_read(i)
            ).pack(side="right", padx=10)
            CTkButton(
                row, text="🗑", width=40, fg_color="red", hover_color="darkred",
                command=lambda i=item: self.delete_tbr(i)
            ).pack(side="right", padx=5)

    def add_tbr(self):
        text = self.entry_tbr.get().strip()
        if text:
            tbr = self.db.get("tbr")
            tbr.append({
                "id": Database.generate_id(),
                "titulo": text,
                "fecha_add": datetime.now().strftime("%Y-%m-%d")
            })
            self.db.set("tbr", tbr)
            self.entry_tbr.delete(0, "end")
            self.render()

    def delete_tbr(self, item):
        tbr = self.db.get("tbr")
        tbr = [x for x in tbr if x.get("id") != item.get("id")]
        self.db.set("tbr", tbr)
        self.render()

    def mark_read(self, item):
        books = self.db.get("books")
        books.append({
            "id": Database.generate_id(),
            "titulo": item["titulo"],
            "autor": "",
            "rating": 0,
            "estado": "Leído"
        })
        self.db.set("books", books)
        self.delete_tbr(item)
        messagebox.showinfo("¡Excelente!", "Libro movido a tu Biblioteca 📖")
