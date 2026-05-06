"""
📚 BOOK JOURNAL APP - Base Proyecto CustomTkinter
Incluye: Biblioteca, Reviews, Reading Tracker, TBR, Challenges, Bookshelf Visual
Autor: Base generada por IA | Extensible y modular
"""

import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkProgressBar, CTkRadioButton, CTkLabel, CTkButton, CTkEntry, CTkTextbox, CTkScrollableFrame, CTkSegmentedButton, CTkSwitch, CTkSlider, CTkOptionMenu, CTkImage
from PIL import Image, ImageDraw, ImageFont
import json
import os
from datetime import datetime, date
import calendar
from tkinter import Canvas, messagebox

# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================
ctk.set_appearance_mode("Dark")  # "Dark" o "Light"
ctk.set_default_color_theme("blue")

DATA_FILE = "book_journal_data.json"

# ============================================================
# BASE DE DATOS LOCAL (JSON)
# ============================================================
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
            "books": [],           # Biblioteca general
            "reviews": [],         # Reseñas detalladas
            "tracker": {},         # { "2026-05": { "1": 15, "2": 30 } }
            "tbr": [],             # To Be Read
            "challenges": []       # Desafíos de lectura
        }
        for key, val in defaults.items():
            if key not in self.data:
                self.data[key] = val
        self.save()

    def get(self, key):
        return self.data.get(key, [])

    def set(self, key, value):
        self.data[key] = value
        self.save()

# ============================================================
# UTILIDADES DE UI
# ============================================================
class StarRating(ctk.CTkFrame):
    """Widget de 5 estrellas interactivo."""
    def __init__(self, master, rating=0, command=None, size=20, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.rating = rating
        self.command = command
        self.size = size
        self.stars = []
        for i in range(5):
            lbl = CTkLabel(self, text="☆", font=("Arial", size), text_color="gold")
            lbl.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx+1))
            lbl.pack(side="left", padx=2)
            self.stars.append(lbl)
        self.update_stars()

    def set_rating(self, value):
        self.rating = value
        self.update_stars()
        if self.command:
            self.command(value)

    def update_stars(self):
        for i, lbl in enumerate(self.stars):
            lbl.configure(text="★" if i < self.rating else "☆")

class IconRating(ctk.CTkFrame):
    """Rating con iconos personalizados (❤️ 😠 😢 etc)."""
    def __init__(self, master, icon="♥", max_val=5, value=0, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.value = value
        self.icon = icon
        self.labels = []
        for i in range(max_val):
            lbl = CTkLabel(self, text=icon, font=("Arial", 18), text_color="gray")
            lbl.bind("<Button-1>", lambda e, idx=i: self.set_value(idx+1))
            lbl.pack(side="left", padx=3)
            self.labels.append(lbl)
        self.update_ui()

    def set_value(self, v):
        self.value = v
        self.update_ui()

    def update_ui(self):
        for i, lbl in enumerate(self.labels):
            lbl.configure(text_color="#ff6b6b" if i < self.value else "gray")

# ============================================================
# 1. BIBLIOTECA (Grid de libros como foto 1)
# ============================================================
class BibliotecaFrame(CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        header = CTkLabel(self, text="📖 BIBLIOTECA", font=("Helvetica", 28, "bold"))
        header.pack(pady=(20,10))

        # Botón agregar
        btn_add = CTkButton(self, text="+ Agregar Libro", command=self.add_book_dialog)
        btn_add.pack(pady=10)

        # Grid scrollable
        self.scroll = CTkScrollableFrame(self, width=900, height=600, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render_books()

    def render_books(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        books = self.db.get("books")
        if not books:
            CTkLabel(self.scroll, text="No hay libros aún. ¡Agrega uno!", font=("Arial", 16)).pack(pady=50)
            return

        # Grid 4 columnas como la foto
        row, col = 0, 0
        for book in books:
            card = self.create_book_card(self.scroll, book)
            card.grid(row=row, column=col, padx=15, pady=15)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def create_book_card(self, parent, book):
        card = CTkFrame(parent, width=180, height=320, corner_radius=12, border_width=2)
        card.grid_propagate(False)

        # Portada placeholder
        cover = CTkFrame(card, width=140, height=200, corner_radius=8, fg_color="#2b2b2b")
        cover.place(relx=0.5, y=20, anchor="n")

        CTkLabel(cover, text="📕", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")

        # Título
        CTkLabel(card, text=book.get("titulo","Sin título")[:20], font=("Arial", 12, "bold")).place(relx=0.5, y=235, anchor="center")
        # Autor
        CTkLabel(card, text=book.get("autor","")[:18], font=("Arial", 10)).place(relx=0.5, y=260, anchor="center")
        # Rating
        stars = StarRating(card, rating=book.get("rating",0), size=16)
        stars.place(relx=0.5, y=295, anchor="center")

        return card

    def add_book_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Libro")
        dialog.geometry("400x500")

        CTkLabel(dialog, text="Título:").pack(pady=(20,5))
        entry_titulo = CTkEntry(dialog, width=300)
        entry_titulo.pack()

        CTkLabel(dialog, text="Autor:").pack(pady=(15,5))
        entry_autor = CTkEntry(dialog, width=300)
        entry_autor.pack()

        CTkLabel(dialog, text="Género:").pack(pady=(15,5))
        entry_genre = CTkEntry(dialog, width=300)
        entry_genre.pack()

        CTkLabel(dialog, text="Calificación:").pack(pady=(15,5))
        star = StarRating(dialog, rating=0)
        star.pack()

        def save():
            new_book = {
                "id": datetime.now().isoformat(),
                "titulo": entry_titulo.get(),
                "autor": entry_autor.get(),
                "genero": entry_genre.get(),
                "rating": star.rating,
                "estado": "Por leer"  # o Leyendo, Leído
            }
            books = self.db.get("books")
            books.append(new_book)
            self.db.set("books", books)
            dialog.destroy()
            self.render_books()

        CTkButton(dialog, text="Guardar", command=save).pack(pady=30)

# ============================================================
# 2. LECTURA CONCLUIDA / REVIEW (Formulario como foto 2)
# ============================================================
class ReviewFrame(CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="✍️ Lectura Concluida", font=("Helvetica", 28, "bold")).pack(pady=(20,10))

        self.scroll = CTkScrollableFrame(self, width=950, height=620, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.build_form()

    def build_form(self):
        f = self.scroll

        # Row 0: Título y Autor
        r0 = CTkFrame(f, fg_color="transparent")
        r0.pack(fill="x", pady=10)

        CTkLabel(r0, text="TÍTULO:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        self.entry_titulo = CTkEntry(r0, width=600, height=35)
        self.entry_titulo.pack(anchor="w", padx=20, pady=5)

        CTkLabel(r0, text="AUTOR:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        self.entry_autor = CTkEntry(r0, width=600, height=35)
        self.entry_autor.pack(anchor="w", padx=20, pady=5)

        # Row 1: Fechas y páginas
        r1 = CTkFrame(f, fg_color="transparent")
        r1.pack(fill="x", pady=10)

        for text, attr in [("Fecha Inicio", "fecha_inicio"), ("Fecha Final", "fecha_final"), ("N° Páginas", "paginas")]:
            col = CTkFrame(r1, fg_color="transparent")
            col.pack(side="left", padx=20)
            CTkLabel(col, text=text+":", font=("Arial", 11, "bold")).pack(anchor="w")
            entry = CTkEntry(col, width=150)
            entry.pack()
            setattr(self, f"entry_{attr}", entry)

        # Formato
        r2 = CTkFrame(f, fg_color="transparent")
        r2.pack(fill="x", pady=10, padx=20)
        CTkLabel(r2, text="Formato:", font=("Arial", 12, "bold")).pack(side="left")
        self.formato_var = ctk.StringVar(value="Físico")
        for val in ["Físico", "Digital", "Audiolibro"]:
            CTkRadioButton(r2, text=val, variable=self.formato_var, value=val).pack(side="left", padx=10)

        CTkLabel(r2, text="Género:", font=("Arial", 12, "bold")).pack(side="left", padx=(30,0))
        self.entry_genero = CTkEntry(r2, width=200)
        self.entry_genero.pack(side="left", padx=10)

        # Rating general
        r3 = CTkFrame(f, fg_color="transparent")
        r3.pack(fill="x", pady=15, padx=20)
        CTkLabel(r3, text="Calificación General:", font=("Arial", 14, "bold")).pack(side="left")
        self.stars_general = StarRating(r3, rating=0, size=28)
        self.stars_general.pack(side="left", padx=20)

        # Personajes
        r4 = CTkFrame(f, fg_color="transparent")
        r4.pack(fill="x", pady=10, padx=20)
        CTkLabel(r4, text="Personaje Favorito:").pack(side="left")
        self.entry_fav = CTkEntry(r4, width=200)
        self.entry_fav.pack(side="left", padx=10)
        CTkLabel(r4, text="Personaje Odiado:").pack(side="left", padx=(20,0))
        self.entry_hate = CTkEntry(r4, width=200)
        self.entry_hate.pack(side="left", padx=10)

        # Sentimientos (como la foto 2)
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
        CTkLabel(r6, text="FRASES DESTACADAS:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.text_frases = CTkTextbox(f, width=800, height=100, corner_radius=10)
        self.text_frases.pack(padx=20, pady=5)

        # Reseña
        r7 = CTkFrame(f, fg_color="transparent")
        r7.pack(fill="x", pady=10, padx=20)
        CTkLabel(r7, text="RESEÑA:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.text_resena = CTkTextbox(f, width=800, height=150, corner_radius=10)
        self.text_resena.pack(padx=20, pady=5)

        # Guardar
        CTkButton(f, text="💾 Guardar Reseña", command=self.save_review, height=40, font=("Arial", 14, "bold")).pack(pady=20)

    def save_review(self):
        review = {
            "id": datetime.now().isoformat(),
            "titulo": self.entry_titulo.get(),
            "autor": self.entry_autor.get(),
            "fecha_inicio": self.entry_fecha_inicio.get(),
            "fecha_final": self.entry_fecha_final.get(),
            "paginas": self.entry_paginas.get(),
            "formato": self.formato_var.get(),
            "genero": self.entry_genero.get(),
            "rating": self.stars_general.rating,
            "personaje_fav": self.entry_fav.get(),
            "personaje_odiado": self.entry_hate.get(),
            "sentimientos": {k: v.value for k,v in self.feelings.items()},
            "frases": self.text_frases.get("1.0", "end").strip(),
            "resena": self.text_resena.get("1.0", "end").strip()
        }
        reviews = self.db.get("reviews")
        reviews.append(review)
        self.db.set("reviews", reviews)
        messagebox.showinfo("Éxito", "¡Reseña guardada correctamente!")

# ============================================================
# 3. READING TRACKER (Circular como foto 4)
# ============================================================
class TrackerFrame(CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="📅 Reading Tracker", font=("Helvetica", 28, "bold")).pack(pady=(20,10))

        # Selector mes/año
        ctrl = CTkFrame(self, fg_color="transparent")
        ctrl.pack(pady=10)

        self.month_var = ctk.StringVar(value=str(date.today().month))
        self.year_var = ctk.StringVar(value=str(date.today().year))

        CTkOptionMenu(ctrl, values=[str(i) for i in range(1,13)], variable=self.month_var, width=80).pack(side="left", padx=5)
        CTkOptionMenu(ctrl, values=[str(i) for i in range(2024,2031)], variable=self.year_var, width=100).pack(side="left", padx=5)
        CTkButton(ctrl, text="Cargar", command=self.render_tracker, width=80).pack(side="left", padx=10)

        # Canvas para tracker circular
        self.canvas = Canvas(self, width=600, height=600, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Leyenda
        legend = CTkFrame(self, fg_color="transparent")
        legend.pack(pady=10)
        colors = [("#3a3a3a","0-10"), ("#5c5c5c","11-20"), ("#7e7e7e","21-40"), 
                  ("#a0a0a0","41-70"), ("#c2c2c2","70+"), ("#1f1f1f","Nada")]
        for col, label in colors:
            box = CTkFrame(legend, width=20, height=20, fg_color=col, corner_radius=4)
            box.pack(side="left", padx=5)
            CTkLabel(legend, text=label, font=("Arial", 10)).pack(side="left", padx=(0,15))

        self.day_entries = {}  # Para edición
        self.render_tracker()

    def render_tracker(self):
        self.canvas.delete("all")
        self.day_entries.clear()

        cx, cy = 300, 300
        r_outer, r_inner = 250, 180

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        days_in_month = calendar.monthrange(year, month)[1]

        tracker_data = self.db.get("tracker").get(f"{year}-{month:02d}", {})

        # Dibujar segmentos circulares
        for day in range(1, days_in_month + 1):
            angle_start = (day - 1) * (360 / days_in_month) - 90
            angle_end = day * (360 / days_in_month) - 90

            pages = tracker_data.get(str(day), 0)
            color = self._color_for_pages(pages)

            # Dibujar arco
            self._draw_arc(cx, cy, r_outer, r_inner, angle_start, angle_end, color)

            # Número del día
            mid_angle = (angle_start + angle_end) / 2
            rad = (r_outer + r_inner) / 2
            x = cx + rad * 0.85 * (3.14159/180 * mid_angle).__class__(__import__('math').cos(mid_angle*3.14159/180))
            y = cy + rad * 0.85 * __import__('math').sin(mid_angle*3.14159/180)
            x = cx + rad * 0.85 * __import__('math').cos(mid_angle*3.14159/180)
            y = cy + rad * 0.85 * __import__('math').sin(mid_angle*3.14159/180)

            self.canvas.create_text(x, y, text=str(day), fill="white", font=("Arial", 10, "bold"))

            # Click para editar
            tag = f"day_{day}"
            self.canvas.addtag_withtag(tag, "all")

        # Centro decorativo (libros/flor simplificado)
        self.canvas.create_oval(cx-80, cy-80, cx+80, cy+80, fill="#2b2b2b", outline="#444", width=2)
        self.canvas.create_text(cx, cy, text="📚\n🌸", font=("Arial", 40))

        # Bind click
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Panel de entrada rápida
        if not hasattr(self, "input_frame"):
            self.input_frame = CTkFrame(self, fg_color="transparent")
            self.input_frame.pack(pady=10)
            CTkLabel(self.input_frame, text="Día:").pack(side="left", padx=5)
            self.entry_day = CTkEntry(self.input_frame, width=50)
            self.entry_day.pack(side="left", padx=5)
            CTkLabel(self.input_frame, text="Páginas:").pack(side="left", padx=5)
            self.entry_pages = CTkEntry(self.input_frame, width=80)
            self.entry_pages.pack(side="left", padx=5)
            CTkButton(self.input_frame, text="Registrar", command=self.log_day).pack(side="left", padx=10)

    def _color_for_pages(self, pages):
        if pages == 0 or pages == "None": return "#1f1f1f"
        p = int(pages)
        if p <= 10: return "#3a3a3a"
        if p <= 20: return "#5c5c5c"
        if p <= 40: return "#7e7e7e"
        if p <= 70: return "#a0a0a0"
        return "#c2c2c2"

    def _draw_arc(self, cx, cy, r_out, r_in, a1, a2, color):
        import math
        points = []
        steps = 20
        for i in range(steps+1):
            a = math.radians(a1 + (a2-a1)*i/steps)
            points.append(cx + r_out * math.cos(a))
            points.append(cy + r_out * math.sin(a))
        for i in range(steps+1):
            a = math.radians(a2 - (a2-a1)*i/steps)
            points.append(cx + r_in * math.cos(a))
            points.append(cy + r_in * math.sin(a))
        self.canvas.create_polygon(points, fill=color, outline="")

    def on_canvas_click(self, event):
        # Simplificación: se usa el panel inferior para registrar
        pass

    def log_day(self):
        day = self.entry_day.get()
        pages = self.entry_pages.get()
        if not day.isdigit():
            return
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        key = f"{year}-{month:02d}"
        tracker = self.db.get("tracker")
        if key not in tracker:
            tracker[key] = {}
        tracker[key][day] = pages
        self.db.set("tracker", tracker)
        self.render_tracker()

# ============================================================
# 4. TBR (To Be Read)
# ============================================================
class TBRFrame(CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="🎯 TBR - To Be Read", font=("Helvetica", 28, "bold")).pack(pady=(20,10))

        top = CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        self.entry_tbr = CTkEntry(top, width=400, placeholder_text="Título del libro...")
        self.entry_tbr.pack(side="left", padx=5)
        CTkButton(top, text="+ Añadir a TBR", command=self.add_tbr).pack(side="left", padx=5)

        self.scroll = CTkScrollableFrame(self, width=900, height=550, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render()

    def render(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        tbr_list = self.db.get("tbr")
        if not tbr_list:
            CTkLabel(self.scroll, text="Tu TBR está vacío 📭", font=("Arial", 16)).pack(pady=50)
            return

        for item in tbr_list:
            row = CTkFrame(self.scroll, corner_radius=10, border_width=1)
            row.pack(fill="x", pady=5, padx=5)
            CTkLabel(row, text=item["titulo"], font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)
            CTkLabel(row, text=item.get("fecha_add",""), font=("Arial", 10)).pack(side="left", padx=10)
            CTkButton(row, text="✓ Leído", width=80, command=lambda i=item: self.mark_read(i)).pack(side="right", padx=10)
            CTkButton(row, text="🗑", width=40, fg_color="red", hover_color="darkred", 
                     command=lambda i=item: self.delete_tbr(i)).pack(side="right", padx=5)

    def add_tbr(self):
        text = self.entry_tbr.get().strip()
        if text:
            tbr = self.db.get("tbr")
            tbr.append({"titulo": text, "fecha_add": datetime.now().strftime("%Y-%m-%d")})
            self.db.set("tbr", tbr)
            self.entry_tbr.delete(0, "end")
            self.render()

    def delete_tbr(self, item):
        tbr = self.db.get("tbr")
        tbr = [x for x in tbr if x["titulo"] != item["titulo"] or x["fecha_add"] != item["fecha_add"]]
        self.db.set("tbr", tbr)
        self.render()

    def mark_read(self, item):
        # Mover a biblioteca
        books = self.db.get("books")
        books.append({
            "id": datetime.now().isoformat(),
            "titulo": item["titulo"],
            "autor": "",
            "rating": 0,
            "estado": "Leído"
        })
        self.db.set("books", books)
        self.delete_tbr(item)
        messagebox.showinfo("¡Excelente!", "Libro movido a tu Biblioteca 📖")

# ============================================================
# 5. BOOKSHELF VISUAL (Como foto 3)
# ============================================================
class BookshelfFrame(CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="🪴 The Bookshelf", font=("Helvetica", 28, "bold")).pack(pady=(20,10))

        self.canvas = Canvas(self, width=900, height=600, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=10)

        CTkButton(self, text="🎨 Redibujar Estantería", command=self.draw_shelf).pack(pady=10)
        self.draw_shelf()

    def draw_shelf(self):
        self.canvas.delete("all")
        books = self.db.get("books")

        # Dibujar 5 estantes
        shelf_y = [100, 220, 340, 460, 580]
        colors = ["#8B4513", "#A0522D", "#CD853F", "#D2691E", "#8B4513"]

        for y in shelf_y:
            self.canvas.create_rectangle(50, y, 850, y+10, fill="#5c3a21", outline="")

        # Distribuir libros en estantes
        shelf_idx = 0
        x_pos = 70
        for i, book in enumerate(books[:25]):  # max 25 visuales
            if x_pos > 800:
                shelf_idx += 1
                x_pos = 70
            if shelf_idx >= 5:
                break

            y_base = shelf_y[shelf_idx]
            h = 60 + (hash(book["titulo"]) % 40)  # altura variada
            w = 30 + (hash(book["autor"]) % 20)   # ancho variado
            color = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c"][i % 6]

            # Dibujar libro inclinado o recto
            self.canvas.create_rectangle(x_pos, y_base-h, x_pos+w, y_base, fill=color, outline="#222", width=1)
            self.canvas.create_text(x_pos+w/2, y_base-h/2, text=book["titulo"][:8], fill="white", 
                                   font=("Arial", 8), angle=90 if i%7==0 else 0)

            x_pos += w + 5

        # Plantas decorativas (círculos verdes)
        for px, py in [(60, 85), (820, 325), (100, 445)]:
            self.canvas.create_oval(px-15, py-30, px+15, py, fill="#2ecc71", outline="")
            self.canvas.create_oval(px-10, py-45, px+10, py-15, fill="#27ae60", outline="")

# ============================================================
# 6. CHALLENGES
# ============================================================
class ChallengesFrame(CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="🏆 Reading Challenges", font=("Helvetica", 28, "bold")).pack(pady=(20,10))

        top = CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        self.entry_challenge = CTkEntry(top, width=300, placeholder_text="Nombre del desafío...")
        self.entry_challenge.pack(side="left", padx=5)
        self.entry_goal = CTkEntry(top, width=100, placeholder_text="Meta (número)")
        self.entry_goal.pack(side="left", padx=5)
        CTkButton(top, text="+ Crear Challenge", command=self.add_challenge).pack(side="left", padx=10)

        self.scroll = CTkScrollableFrame(self, width=900, height=550, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render()

    def render(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        challenges = self.db.get("challenges")
        if not challenges:
            CTkLabel(self.scroll, text="Sin desafíos activos. ¡Crea uno! 🚀", font=("Arial", 16)).pack(pady=50)
            return

        for ch in challenges:
            card = CTkFrame(self.scroll, corner_radius=15, border_width=2)
            card.pack(fill="x", pady=10, padx=5)

            title = CTkLabel(card, text=ch["nombre"], font=("Arial", 16, "bold"))
            title.pack(anchor="w", padx=20, pady=(15,5))

            progress = CTkProgressBar(card, width=800, height=20, corner_radius=10)
            progress.pack(padx=20, pady=5)
            prog_val = min(ch.get("actual",0) / ch.get("meta",1), 1)
            progress.set(prog_val)

            info = CTkLabel(card, text=f"{ch.get('actual',0)} / {ch['meta']} completado", font=("Arial", 12))
            info.pack(anchor="w", padx=20, pady=(0,10))

            ctrl = CTkFrame(card, fg_color="transparent")
            ctrl.pack(anchor="w", padx=20, pady=(0,15))
            CTkButton(ctrl, text="+1", width=60, command=lambda c=ch: self.update_challenge(c, 1)).pack(side="left", padx=5)
            CTkButton(ctrl, text="+5", width=60, command=lambda c=ch: self.update_challenge(c, 5)).pack(side="left", padx=5)
            CTkButton(ctrl, text="🗑 Eliminar", width=100, fg_color="red", hover_color="darkred",
                     command=lambda c=ch: self.delete_challenge(c)).pack(side="left", padx=20)

    def add_challenge(self):
        name = self.entry_challenge.get().strip()
        goal = self.entry_goal.get().strip()
        if name and goal.isdigit():
            challenges = self.db.get("challenges")
            challenges.append({"nombre": name, "meta": int(goal), "actual": 0})
            self.db.set("challenges", challenges)
            self.entry_challenge.delete(0, "end")
            self.entry_goal.delete(0, "end")
            self.render()

    def update_challenge(self, ch, delta):
        challenges = self.db.get("challenges")
        for c in challenges:
            if c["nombre"] == ch["nombre"] and c["meta"] == ch["meta"]:
                c["actual"] = min(c.get("actual",0) + delta, c["meta"])
                break
        self.db.set("challenges", challenges)
        self.render()

    def delete_challenge(self, ch):
        challenges = self.db.get("challenges")
        challenges = [c for c in challenges if not (c["nombre"]==ch["nombre"] and c["meta"]==ch["meta"])]
        self.db.set("challenges", challenges)
        self.render()

# ============================================================
# APP PRINCIPAL CON NAVEGACIÓN
# ============================================================
class BookJournalApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("📚 Book Journal Pro - CustomTkinter")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        self.db = Database()

        # Layout: Sidebar + Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(8, weight=1)

        CTkLabel(self.sidebar, text="📚 Book\nJournal", font=("Helvetica", 24, "bold")).grid(row=0, column=0, pady=(30,20), padx=20)

        self.nav_buttons = []
        nav_items = [
            ("Biblioteca", "📖", BibliotecaFrame),
            ("Review", "✍️", ReviewFrame),
            ("Tracker", "📅", TrackerFrame),
            ("TBR", "🎯", TBRFrame),
            ("Bookshelf", "🪴", BookshelfFrame),
            ("Challenges", "🏆", ChallengesFrame)
        ]

        self.frames = {}
        self.current_frame = None

        for idx, (name, icon, FrameClass) in enumerate(nav_items, 1):
            btn = CTkButton(self.sidebar, text=f"{icon} {name}", font=("Arial", 14),
                           anchor="w", height=40, width=180,
                           command=lambda f=FrameClass, n=name: self.show_frame(f, n))
            btn.grid(row=idx, column=0, pady=8, padx=15)
            self.nav_buttons.append((btn, name))

        # Theme switch
        self.theme_switch = CTkSwitch(self.sidebar, text="Modo Oscuro", command=self.toggle_theme)
        self.theme_switch.grid(row=9, column=0, pady=20, padx=15, sticky="s")
        self.theme_switch.select()

        # CONTENT AREA
        self.content = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Mostrar primera vista
        self.show_frame(BibliotecaFrame, "Biblioteca")

    def show_frame(self, FrameClass, name):
        # Resetear estilos de botones
        for btn, btn_name in self.nav_buttons:
            if btn_name == name:
                btn.configure(fg_color=["#3a7ebf", "#1f538d"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=["black", "white"])

        # Destruir frame anterior
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = FrameClass(self.content, self.db, corner_radius=15)
        self.current_frame.grid(row=0, column=0, sticky="nswe")

    def toggle_theme(self):
        mode = "Dark" if self.theme_switch.get() else "Light"
        ctk.set_appearance_mode(mode)

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    app = BookJournalApp()
    app.mainloop()