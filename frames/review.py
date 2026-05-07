"""Formulario de reseña detallada (Lectura Concluida)."""
import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkTextbox, CTkScrollableFrame, CTkRadioButton
)
from tkinter import messagebox

from database import Database
from widgets import StarRating, IconRating


class ReviewFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(
            self, text="✍️ Lectura Concluida", font=("Helvetica", 28, "bold")
        ).pack(pady=(20, 10))

        self.scroll = CTkScrollableFrame(
            self, width=950, height=620, fg_color="transparent"
        )
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.build_form()

    def build_form(self):
        f = self.scroll

        # Título y Autor
        r0 = CTkFrame(f, fg_color="transparent")
        r0.pack(fill="x", pady=10)

        CTkLabel(r0, text="TÍTULO:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        self.entry_titulo = CTkEntry(r0, width=600, height=35)
        self.entry_titulo.pack(anchor="w", padx=20, pady=5)

        CTkLabel(r0, text="AUTOR:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        self.entry_autor = CTkEntry(r0, width=600, height=35)
        self.entry_autor.pack(anchor="w", padx=20, pady=5)

        # Fechas y páginas
        r1 = CTkFrame(f, fg_color="transparent")
        r1.pack(fill="x", pady=10)

        fields = [
            ("Fecha Inicio", "fecha_inicio"),
            ("Fecha Final", "fecha_final"),
            ("N° Páginas", "paginas")
        ]
        for text, attr in fields:
            col = CTkFrame(r1, fg_color="transparent")
            col.pack(side="left", padx=20)
            CTkLabel(col, text=text + ":", font=("Arial", 11, "bold")).pack(anchor="w")
            entry = CTkEntry(col, width=150)
            entry.pack()
            setattr(self, f"entry_{attr}", entry)

        # Formato y Género
        r2 = CTkFrame(f, fg_color="transparent")
        r2.pack(fill="x", pady=10, padx=20)
        CTkLabel(r2, text="Formato:", font=("Arial", 12, "bold")).pack(side="left")
        self.formato_var = ctk.StringVar(value="Físico")
        for val in ["Físico", "Digital", "Audiolibro"]:
            CTkRadioButton(r2, text=val, variable=self.formato_var, value=val).pack(
                side="left", padx=10
            )

        CTkLabel(r2, text="Género:", font=("Arial", 12, "bold")).pack(
            side="left", padx=(30, 0)
        )
        self.entry_genero = CTkEntry(r2, width=200)
        self.entry_genero.pack(side="left", padx=10)

        # Rating general
        r3 = CTkFrame(f, fg_color="transparent")
        r3.pack(fill="x", pady=15, padx=20)
        CTkLabel(r3, text="Calificación General:", font=("Arial", 14, "bold")).pack(
            side="left"
        )
        self.stars_general = StarRating(r3, rating=0, size=28)
        self.stars_general.pack(side="left", padx=20)

        # Personajes
        r4 = CTkFrame(f, fg_color="transparent")
        r4.pack(fill="x", pady=10, padx=20)
        CTkLabel(r4, text="Personaje Favorito:").pack(side="left")
        self.entry_fav = CTkEntry(r4, width=200)
        self.entry_fav.pack(side="left", padx=10)
        CTkLabel(r4, text="Personaje Odiado:").pack(side="left", padx=(20, 0))
        self.entry_hate = CTkEntry(r4, width=200)
        self.entry_hate.pack(side="left", padx=10)

        # Sentimientos
        r5 = CTkFrame(f, fg_color="transparent")
        r5.pack(fill="x", pady=15, padx=20)

        feelings = [
            ("Amor", "♥", "amor"),
            ("Enojo", "😠", "enojo"),
            ("Tristeza", "💧", "tristeza"),
            ("Plot", "✦", "plot"),
            ("Reflexión", "🧠", "reflexion"),
            ("Felicidad", "☺", "felicidad"),
            ("Hot", "🔥", "hot")
        ]
        self.feelings = {}
        for name, icon, key in feelings:
            col = CTkFrame(r5, fg_color="transparent")
            col.pack(side="left", padx=12)
            CTkLabel(col, text=name, font=("Arial", 10, "bold")).pack()
            ir = IconRating(col, icon=icon, max_val=5)
            ir.pack()
            self.feelings[key] = ir

        # Frases
        r6 = CTkFrame(f, fg_color="transparent")
        r6.pack(fill="x", pady=10, padx=20)
        CTkLabel(r6, text="FRASES DESTACADAS:", font=("Arial", 12, "bold")).pack(
            anchor="w"
        )
        self.text_frases = CTkTextbox(f, width=800, height=100, corner_radius=10)
        self.text_frases.pack(padx=20, pady=5, fill="x")

        # Reseña
        r7 = CTkFrame(f, fg_color="transparent")
        r7.pack(fill="x", pady=10, padx=20)
        CTkLabel(r7, text="RESEÑA:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.text_resena = CTkTextbox(f, width=800, height=150, corner_radius=10)
        self.text_resena.pack(padx=20, pady=5, fill="x")

        # Guardar
        CTkButton(
            f,
            text="💾 Guardar Reseña",
            command=self.save_review,
            height=40,
            font=("Arial", 14, "bold")
        ).pack(pady=20)

    def save_review(self):
        review = {
            "id": Database.generate_id(),
            "titulo": self.entry_titulo.get().strip(),
            "autor": self.entry_autor.get().strip(),
            "fecha_inicio": self.entry_fecha_inicio.get().strip(),
            "fecha_final": self.entry_fecha_final.get().strip(),
            "paginas": self.entry_paginas.get().strip(),
            "formato": self.formato_var.get(),
            "genero": self.entry_genero.get().strip(),
            "rating": self.stars_general.rating,
            "personaje_fav": self.entry_fav.get().strip(),
            "personaje_odiado": self.entry_hate.get().strip(),
            "sentimientos": {k: v.value for k, v in self.feelings.items()},
            "frases": self.text_frases.get("1.0", "end").strip(),
            "resena": self.text_resena.get("1.0", "end").strip()
        }
        reviews = self.db.get("reviews")
        reviews.append(review)
        self.db.set("reviews", reviews)
        messagebox.showinfo("Éxito", "¡Reseña guardada correctamente!")
