"""Reviews en formato libro abierto con navegacion de paginas."""
from datetime import datetime

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkTextbox, CTkRadioButton
from tkinter import messagebox

from database import Database
from widgets import StarRating, IconRating


class ReviewFrame(CTkFrame):
    PAGE_W = 460
    PAGE_H = 620

    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="✍️ Lectura Concluida", font=("Helvetica", 28, "bold")).pack(pady=(10, 5))

        self.book = CTkFrame(self, fg_color="#2b2b2b", corner_radius=4, border_width=3)
        self.book.pack(pady=10)

        self.left_page = CTkFrame(self.book, width=self.PAGE_W, height=self.PAGE_H,
                                  fg_color="#f5f5f5", corner_radius=0)
        self.left_page.pack(side="left", padx=(4, 1))
        self.left_page.pack_propagate(False)

        self.spine = CTkFrame(self.book, width=10, height=self.PAGE_H, fg_color="#1a1a1a", corner_radius=0)
        self.spine.pack(side="left")

        self.right_page = CTkFrame(self.book, width=self.PAGE_W, height=self.PAGE_H,
                                   fg_color="#f5f5f5", corner_radius=0)
        self.right_page.pack(side="left", padx=(1, 4))
        self.right_page.pack_propagate(False)

        nav = CTkFrame(self, fg_color="transparent")
        nav.pack(pady=10)
        CTkButton(nav, text="◀ Anterior", command=self.prev_spread, width=120).pack(side="left", padx=10)
        self.page_label = CTkLabel(nav, text="Pagina 1", font=("Arial", 12, "bold"))
        self.page_label.pack(side="left", padx=10)
        CTkButton(nav, text="Siguiente ▶", command=self.next_spread, width=120).pack(side="left", padx=10)

        self.spread_idx = 0
        self.render_spread()

    def render_spread(self):
        for w in self.left_page.winfo_children():
            w.destroy()
        for w in self.right_page.winfo_children():
            w.destroy()

        reviews = self.db.get("reviews")
        left_idx = self.spread_idx * 2
        right_idx = left_idx + 1
        total_reviews = len(reviews)

        if total_reviews == 0:
            self.render_blank_form(self.left_page, 1)
            self.render_empty_page(self.right_page, 2)
            self.page_label.configure(text="Pagina 1 de 1")
            return

        if left_idx < total_reviews:
            self.render_review_readonly(self.left_page, reviews[left_idx], left_idx + 1)
        else:
            self.render_blank_form(self.left_page, left_idx + 1)

        if right_idx < total_reviews:
            self.render_review_readonly(self.right_page, reviews[right_idx], right_idx + 1)
        else:
            self.render_blank_form(self.right_page, right_idx + 1)

        total_pages = total_reviews + 1
        self.page_label.configure(text=f"Paginas {left_idx + 1}-{right_idx + 1} de {total_pages}")

    def render_empty_page(self, parent, num):
        scroll = ctk.CTkScrollableFrame(parent, width=self.PAGE_W - 20, height=self.PAGE_H - 20,
                                        fg_color="#f5f5f5")
        scroll.pack(padx=10, pady=10, fill="both", expand=True)
        CTkLabel(scroll, text=f"— Pagina {num} —", text_color="#888",
                 font=("Arial", 10)).pack(pady=5)
        CTkLabel(scroll, text="📄", text_color="gray",
                 font=("Arial", 48)).pack(pady=20)

    def render_review_readonly(self, parent, review, num):
        scroll = ctk.CTkScrollableFrame(parent, width=self.PAGE_W - 20, height=self.PAGE_H - 20,
                                        fg_color="#f5f5f5")
        scroll.pack(padx=10, pady=10, fill="both", expand=True)

        CTkLabel(scroll, text=f"— Pagina {num} —", text_color="#888", font=("Arial", 10)).pack()
        CTkLabel(scroll, text=review.get("titulo", "Sin titulo"),
                 text_color="#222", font=("Arial", 16, "bold"), wraplength=380).pack(pady=(5, 2))
        CTkLabel(scroll, text=f"de {review.get('autor', 'Autor desconocido')}",
                 text_color="#555", font=("Arial", 11)).pack()

        meta = CTkFrame(scroll, fg_color="transparent")
        meta.pack(pady=8)
        CTkLabel(meta, text=f"📅 {review.get('fecha_inicio','')} → {review.get('fecha_final','')}",
                 text_color="#444", font=("Arial", 9)).pack(side="left", padx=5)
        CTkLabel(meta, text=f"📖 {review.get('paginas','')} pag.",
                 text_color="#444", font=("Arial", 9)).pack(side="left", padx=5)
        CTkLabel(meta, text=f"🎭 {review.get('genero','')}",
                 text_color="#444", font=("Arial", 9)).pack(side="left", padx=5)

        fmt = review.get("formato", "fisico")
        fmt_emoji = {"fisico": "📖", "digital": "💻", "audiolibro": "🎧"}
        CTkLabel(scroll, text=f"{fmt_emoji.get(fmt,'')} {fmt.capitalize()}",
                 text_color="#444", font=("Arial", 9)).pack()

        stars = CTkFrame(scroll, fg_color="transparent")
        stars.pack(pady=5)
        for i in range(5):
            CTkLabel(stars, text="★" if i < review.get("rating", 0) else "☆",
                     text_color="gold", font=("Arial", 16)).pack(side="left")

        if review.get("personaje_fav"):
            CTkLabel(scroll, text=f"❤️ Favorito: {review['personaje_fav']}",
                     text_color="#333", font=("Arial", 10)).pack(anchor="w", padx=10)
        if review.get("personaje_odiado"):
            CTkLabel(scroll, text=f"💀 Odiado: {review['personaje_odiado']}",
                     text_color="#333", font=("Arial", 10)).pack(anchor="w", padx=10)

        if review.get("sentimientos"):
            sent = CTkFrame(scroll, fg_color="transparent")
            sent.pack(pady=5)
            icons = {"amor": "♥", "enojo": "😠", "tristeza": "💧",
                     "plot": "✦", "reflexion": "🧠", "felicidad": "☺", "hot": "🔥"}
            for k, v in review["sentimientos"].items():
                if v > 0:
                    CTkLabel(sent, text=f"{icons.get(k,k)} {v}", text_color="#555",
                             font=("Arial", 9)).pack(side="left", padx=4)

        if review.get("frases"):
            CTkLabel(scroll, text="Frases destacadas", text_color="#666",
                     font=("Arial", 10, "italic")).pack(anchor="w", padx=10, pady=(10, 2))
            CTkLabel(scroll, text=review["frases"], text_color="#333",
                     font=("Arial", 9), wraplength=380).pack(anchor="w", padx=10)

        if review.get("resena"):
            CTkLabel(scroll, text="Resena:", text_color="#666",
                     font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 2))
            CTkLabel(scroll, text=review["resena"], text_color="#333",
                     font=("Arial", 9), wraplength=380).pack(anchor="w", padx=10)

    def render_blank_form(self, parent, num):
        scroll = ctk.CTkScrollableFrame(parent, width=self.PAGE_W - 20, height=self.PAGE_H - 20,
                                        fg_color="#f5f5f5")
        scroll.pack(padx=10, pady=10, fill="both", expand=True)

        CTkLabel(scroll, text=f"— Pagina {num} —", text_color="#888", font=("Arial", 10)).pack()
        CTkLabel(scroll, text="Nueva Resena", text_color="#222",
                 font=("Arial", 16, "bold")).pack(pady=(5, 10))

        def row_label(parent, text):
            CTkLabel(parent, text=text + ":", text_color="#444", font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 2))

        row_label(scroll, "TITULO")
        f_titulo = CTkEntry(scroll, width=380, height=28)
        f_titulo.pack()

        row_label(scroll, "AUTOR")
        f_autor = CTkEntry(scroll, width=380, height=28)
        f_autor.pack()

        row = CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=5)
        fields = [("Inicio", "fecha_inicio", 110), ("Final", "fecha_final", 110), ("Pags", "paginas", 80)]
        local_entries = {}
        for txt, attr, w in fields:
            c = CTkFrame(row, fg_color="transparent")
            c.pack(side="left", padx=5)
            CTkLabel(c, text=txt + ":", text_color="#444", font=("Arial", 9, "bold")).pack(anchor="w")
            e = CTkEntry(c, width=w, height=26)
            e.pack()
            local_entries[attr] = e

        row2 = CTkFrame(scroll, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        CTkLabel(row2, text="Formato:", text_color="#444", font=("Arial", 10, "bold")).pack(side="left")
        f_formato = ctk.StringVar(value="fisico")
        for val, txt in [("fisico", "Fisico"), ("digital", "Digital"), ("audiolibro", "Audio")]:
            CTkRadioButton(row2, text=txt, variable=f_formato, value=val,
                           text_color="#333", font=("Arial", 9)).pack(side="left", padx=6)

        row_label(scroll, "GENERO")
        f_genero = CTkEntry(scroll, width=380, height=26)
        f_genero.pack()

        rframe = CTkFrame(scroll, fg_color="transparent")
        rframe.pack(pady=8)
        CTkLabel(rframe, text="Calificacion:", text_color="#444", font=("Arial", 12, "bold")).pack(side="left")
        f_stars = StarRating(rframe, rating=0, size=28)
        f_stars.pack(side="left", padx=10)

        row3 = CTkFrame(scroll, fg_color="transparent")
        row3.pack(fill="x", pady=3)
        CTkLabel(row3, text="Fav:", text_color="#444", font=("Arial", 10)).pack(side="left")
        f_fav = CTkEntry(row3, width=140, height=24)
        f_fav.pack(side="left", padx=5)
        CTkLabel(row3, text="Odiado:", text_color="#444", font=("Arial", 10)).pack(side="left", padx=(10, 0))
        f_hate = CTkEntry(row3, width=140, height=24)
        f_hate.pack(side="left", padx=5)

        CTkLabel(scroll, text="Sentimientos:", text_color="#444", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 4))
        sframe = CTkFrame(scroll, fg_color="transparent")
        sframe.pack(fill="x", pady=5)
        feelings = [
            ("Amor", "♥", "amor"), ("Enojo", "😠", "enojo"), ("Tristeza", "💧", "tristeza"),
            ("Plot", "✦", "plot"), ("Reflexion", "🧠", "reflexion"),
            ("Felicidad", "☺", "felicidad"), ("Hot", "🔥", "hot")
        ]
        f_feelings = {}
        for idx, (name, icon, key) in enumerate(feelings):
            c = CTkFrame(sframe, fg_color="transparent")
            c.grid(row=idx // 4, column=idx % 4, padx=6, pady=5)
            CTkLabel(c, text=name, text_color="#555", font=("Arial", 11, "bold")).pack()
            ir = IconRating(c, icon=icon, max_val=5)
            for lbl in ir.labels:
                lbl.configure(font=("Arial", 24))
            ir.pack()
            f_feelings[key] = ir

        row_label(scroll, "FRASES DESTACADAS")
        f_frases = CTkTextbox(scroll, width=380, height=60, corner_radius=6)
        f_frases.pack()

        row_label(scroll, "RESENA")
        f_resena = CTkTextbox(scroll, width=380, height=100, corner_radius=6)
        f_resena.pack()

        def do_save():
            review = {
                "id": Database.generate_id(),
                "titulo": f_titulo.get().strip(),
                "autor": f_autor.get().strip(),
                "fecha_inicio": local_entries["fecha_inicio"].get().strip(),
                "fecha_final": local_entries["fecha_final"].get().strip(),
                "paginas": local_entries["paginas"].get().strip(),
                "formato": f_formato.get(),
                "genero": f_genero.get().strip(),
                "rating": f_stars.rating,
                "personaje_fav": f_fav.get().strip(),
                "personaje_odiado": f_hate.get().strip(),
                "sentimientos": {k: v.value for k, v in f_feelings.items()},
                "frases": f_frases.get("1.0", "end").strip(),
                "resena": f_resena.get("1.0", "end").strip()
            }
            reviews = self.db.get("reviews")
            reviews.append(review)
            self.db.set("reviews", reviews)
            messagebox.showinfo("Exito", "Resena guardada!")
            self.spread_idx = (len(reviews) - 1) // 2
            self.render_spread()

        CTkButton(scroll, text="💾 Guardar Resena", command=do_save,
                  height=32, font=("Arial", 12, "bold")).pack(pady=15)

    def save_review(self):
        pass

    def prev_spread(self):
        if self.spread_idx > 0:
            self.spread_idx -= 1
            self.render_spread()

    def next_spread(self):
        reviews = self.db.get("reviews")
        max_spread = len(reviews) // 2
        if self.spread_idx < max_spread:
            self.spread_idx += 1
            self.render_spread()