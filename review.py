"""Reviews - grid de tarjetas con portada, vista detalle y panel embebido."""
import os
from datetime import datetime

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkTextbox, CTkRadioButton, CTkScrollableFrame
from tkinter import messagebox, filedialog

from PIL import Image

try:
    from customtkinter import CTkImage
except ImportError:
    CTkImage = None

from database import Database, PALETA
from widgets import StarRating, IconRating


# ------------------------------------------------------------------ #
#  WIDGET AUXILIAR: EmojiRating (5 emojis interactivos tipo estrellas)
# ------------------------------------------------------------------ #
class EmojiRating(ctk.CTkFrame):
    def __init__(self, master, emoji="♥", value=0, size=18, color="#ff6b6b", command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.value = value
        self.rating = value
        self.emoji = emoji
        self.color = color
        self.size = size
        self.command = command
        self.labels = []
        for i in range(5):
            lbl = CTkLabel(self, text=emoji, font=("Arial", size), text_color="#2E86C1")
            lbl.bind("<Button-1>", lambda e, idx=i: self.set_value(idx + 1))
            lbl.pack(side="left", padx=1)
            self.labels.append(lbl)
        self.update_ui()

    def set_value(self, v):
        self.value = v
        self.rating = v
        self.update_ui()
        if self.command:
            self.command(v)

    set_rating = set_value

    def update_ui(self):
        for i, lbl in enumerate(self.labels):
            lbl.configure(text_color=self.color if i < self.value else "#2E86C1")


class ReviewFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")
        self._cover_cache = {}
        self._current_review = None

        # --- POOL DE TARJETAS ---
        self._card_pool = []
        self._visible_cards = []
        self._render_job = None

        # ---------- HEADER ----------
        hdr = CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 5), padx=20)
        CTkLabel(hdr, text="Reviews", font=("Helvetica", 28, "bold")).pack(side="left")
        self.btn_toggle_add = CTkButton(hdr, text="+ Nueva Reseña", command=self.show_add_panel)
        self.btn_toggle_add.pack(side="right", padx=5)

        # ---------- GRID DE TARJETAS ----------
        self.scroll = CTkScrollableFrame(self, width=900, height=520, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        # ---------- PANEL DETALLE (LECTURA) ----------
        self.detail_panel = CTkFrame(self, fg_color="#D0EBF5", corner_radius=16, border_width=2, border_color="#2E86C1")
        self.detail_container = CTkFrame(self.detail_panel, fg_color="transparent")
        self.detail_container.pack(expand=True, fill="both", padx=20, pady=10)

        detail_btns = CTkFrame(self.detail_panel, fg_color="transparent")
        detail_btns.pack(pady=(5, 15))
        CTkButton(detail_btns, text="Salir", command=self.close_detail_panel,
                  height=38, font=("Arial", 14), corner_radius=10, fg_color="#1A5276", hover_color="#5DADE2").pack(side="left", padx=8)
        CTkButton(detail_btns, text="Editar", command=self.detail_to_edit,
                  height=38, font=("Arial", 14, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(detail_btns, text="Eliminar", command=self.detail_delete,
                  height=38, font=("Arial", 14), corner_radius=10,
                  fg_color="#E74C3C", hover_color="#C0392B").pack(side="left", padx=8)

        # ---------- PANEL AÑADIR ----------
        self.add_panel = CTkFrame(self, fg_color="#D0EBF5", corner_radius=16, border_width=2, border_color="#2E86C1")
        CTkLabel(self.add_panel, text="NUEVA RESEÑA", font=("Helvetica", 22, "bold")).pack(pady=(15, 10))

        # Scrollable con el formulario
        self.add_scroll = ctk.CTkScrollableFrame(self.add_panel, width=900, height=550, fg_color="transparent")
        self.add_scroll.pack(padx=25, pady=5, fill="both", expand=True)
        self._build_form(self.add_scroll, mode="add")

        # Botones FIJOS abajo (centrados)
        add_btns = CTkFrame(self.add_panel, fg_color="transparent")
        add_btns.pack(pady=(10, 15), fill="x", padx=25)
        CTkButton(add_btns, text="Guardar", command=self.save_review,
                  height=40, font=("Arial", 13, "bold"), corner_radius=10).pack(side="left", expand=True, padx=(0, 8))
        CTkButton(add_btns, text="Cancelar", command=self.close_add_panel,
                  height=40, font=("Arial", 13), corner_radius=10, fg_color="#1A5276", hover_color="#5DADE2").pack(side="left", expand=True, padx=(8, 0))

        # ---------- PANEL EDITAR ----------
        self.edit_panel = CTkFrame(self, fg_color="#D0EBF5", corner_radius=16, border_width=2, border_color="#2E86C1")
        self.edit_review_id = None
        CTkLabel(self.edit_panel, text="EDITAR RESEÑA", font=("Helvetica", 22, "bold")).pack(pady=(15, 10))

        # Scrollable con el formulario (MISMO ORDEN que añadir)
        self.edit_scroll = ctk.CTkScrollableFrame(self.edit_panel, width=900, height=550, fg_color="transparent")
        self.edit_scroll.pack(padx=25, pady=5, fill="both", expand=True)
        self._build_form(self.edit_scroll, mode="edit")

        # Botones FIJOS abajo (centrados)
        edit_btns = CTkFrame(self.edit_panel, fg_color="transparent")
        edit_btns.pack(pady=(10, 15), fill="x", padx=25)
        CTkButton(edit_btns, text="Guardar cambios", command=self.save_edit_review,
                  height=40, font=("Arial", 13, "bold"), corner_radius=10).pack(side="left", expand=True, padx=(0, 8))
        CTkButton(edit_btns, text="Cancelar", command=self.close_edit_panel,
                  height=40, font=("Arial", 13), corner_radius=10, fg_color="#1A5276", hover_color="#5DADE2").pack(side="left", expand=True, padx=(8, 0))

        self.render_reviews()

    # ------------------------------------------------------------------ #
    #  FORMULARIO ESTILO "LECTURA CONCLUIDA"
    # ------------------------------------------------------------------ #
    def _build_form(self, parent, mode="add"):
        prefix = "a_" if mode == "add" else "e_"

        # ===== FILA SUPERIOR: Portada + Estrellas (izq) | Info libro (der) =====
        top_row = CTkFrame(parent, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))

        # --- COLUMNA IZQUIERDA: Portada + Estrellas ---
        left_col = CTkFrame(top_row, fg_color="transparent")
        left_col.pack(side="left", padx=(0, 20))

        # Portada
        cover_box = CTkFrame(left_col, width=160, height=200, corner_radius=10, fg_color="#FFFFFF", border_width=2, border_color="#2E86C1")
        cover_box.pack(pady=(0, 10))
        cover_box.pack_propagate(False)
        setattr(self, f"{prefix}preview_box", cover_box)
        setattr(self, f"{prefix}preview", CTkLabel(cover_box, text="", width=160, height=200))
        getattr(self, f"{prefix}preview").place(relx=0.5, rely=0.5, anchor="center")

        CTkButton(left_col, text="Examinar", width=140, height=32, corner_radius=8,
                  font=("Arial", 11), command=getattr(self, f"browse_{mode}_photo")).pack(pady=(0, 8))

        # Estrellas
        setattr(self, f"{prefix}stars", StarRating(left_col, rating=0, size=28))
        getattr(self, f"{prefix}stars").pack()
        setattr(self, f"_{prefix}foto_path", None)
        setattr(self, f"_{prefix}preview_img", None)

        # --- COLUMNA DERECHA: Info del libro ---
        right_col = CTkFrame(top_row, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        # Título
        CTkLabel(right_col, text="TÍTULO", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
        setattr(self, f"{prefix}titulo", CTkEntry(right_col, width=600, height=36, corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}titulo").pack(fill="x", pady=(0, 10))

        # Autor
        CTkLabel(right_col, text="AUTOR", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
        setattr(self, f"{prefix}autor", CTkEntry(right_col, width=600, height=36, corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}autor").pack(fill="x", pady=(0, 12))

        # Fechas + Páginas + Género (en una fila)
        meta_row = CTkFrame(right_col, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 10))

        # Fecha inicio
        c1 = CTkFrame(meta_row, fg_color="transparent")
        c1.pack(side="left", padx=(0, 10))
        CTkLabel(c1, text="FECHA DE INICIO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        setattr(self, f"{prefix}fecha_inicio", CTkEntry(c1, width=140, height=32, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}fecha_inicio").pack()

        # Fecha final
        c2 = CTkFrame(meta_row, fg_color="transparent")
        c2.pack(side="left", padx=(0, 10))
        CTkLabel(c2, text="FECHA DE FINAL", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        setattr(self, f"{prefix}fecha_final", CTkEntry(c2, width=140, height=32, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}fecha_final").pack()

        # Páginas
        c3 = CTkFrame(meta_row, fg_color="transparent")
        c3.pack(side="left", padx=(0, 10))
        CTkLabel(c3, text="N° DE PÁGINAS", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        setattr(self, f"{prefix}paginas", CTkEntry(c3, width=100, height=32, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}paginas").pack()

        # Género
        c4 = CTkFrame(meta_row, fg_color="transparent")
        c4.pack(side="left", padx=(0, 10))
        CTkLabel(c4, text="GÉNERO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        setattr(self, f"{prefix}genero", CTkEntry(c4, width=140, height=32, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}genero").pack()

        # Formato (físico, digital, audiolibro)
        fmt_frame = CTkFrame(right_col, fg_color="transparent")
        fmt_frame.pack(anchor="w", pady=(0, 5))
        CTkLabel(fmt_frame, text="LO LEÍ EN:", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(side="left", padx=(0, 10))
        setattr(self, f"{prefix}formato", ctk.StringVar(value="fisico"))
        for val, txt in [("fisico", "Físico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(fmt_frame, text=txt, variable=getattr(self, f"{prefix}formato"),
                           value=val, font=("Arial", 11)).pack(side="left", padx=8)

        # ===== PERSONAJES =====
        chars_row = CTkFrame(parent, fg_color="transparent")
        chars_row.pack(fill="x", pady=(0, 15))

        c_fav = CTkFrame(chars_row, fg_color="transparent")
        c_fav.pack(side="left", padx=(0, 20))
        CTkLabel(c_fav, text="PERSONAJE FAVORITO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        setattr(self, f"{prefix}fav", CTkEntry(c_fav, width=280, height=34, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}fav").pack()

        c_hate = CTkFrame(chars_row, fg_color="transparent")
        c_hate.pack(side="left")
        CTkLabel(c_hate, text="PERSONAJE ODIADO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        setattr(self, f"{prefix}hate", CTkEntry(c_hate, width=280, height=34, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}hate").pack()

        # ===== FILA INFERIOR: Sentimientos (izq) | Frases + Reseña (der) =====
        bottom_row = CTkFrame(parent, fg_color="transparent")
        bottom_row.pack(fill="both", expand=True, pady=(0, 10))

        # --- SENTIMIENTOS (columna izquierda) ---
        sent_col = CTkFrame(bottom_row, fg_color="#F5FAFC", corner_radius=14)
        sent_col.pack(side="left", fill="y", padx=(0, 20), pady=5)

        CTkLabel(sent_col, text="SENTIMIENTOS", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 10))

        feelings = [
            ("AMOR", "💗", "amor", "#FF3CCB"),
            ("ENOJO", "💢", "enojo", "#931212"),
            ("TRISTEZA", "💧", "tristeza", "#596DEF"),
            ("PLOT", "🔄️", "plot", "#F3FF07"),
            ("REFLEXIÓN", "💭", "reflexion", "#A716E0"),
            ("FELICIDAD", "🙂", "felicidad", "#1DD62C"),
            ("HOT", "🔥", "hot", "#D90808")
        ]
        setattr(self, f"{prefix}feelings", {})

        for name, icon, key, color in feelings:
            row = CTkFrame(sent_col, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            CTkLabel(row, text=name, font=("Arial", 11, "bold"), text_color=color).pack(side="left", padx=(0, 8))
            er = EmojiRating(row, emoji=icon, value=0, size=16, color=color)
            er.pack(side="left")
            getattr(self, f"{prefix}feelings")[key] = er

        # --- FRASES + RESEÑA (columna derecha) ---
        text_col = CTkFrame(bottom_row, fg_color="transparent")
        text_col.pack(side="left", fill="both", expand=True)

        # Frases destacadas
        CTkLabel(text_col, text="FRASES", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
        setattr(self, f"{prefix}frases", CTkTextbox(text_col, width=600, height=100,
                                                    corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}frases").pack(fill="x", pady=(0, 12))

        # Reseña
        CTkLabel(text_col, text="RESEÑA", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
        setattr(self, f"{prefix}resena", CTkTextbox(text_col, width=600, height=180,
                                                    corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}resena").pack(fill="both", expand=True)

    # ------------------------------------------------------------------ #
    #  PORTADAS
    # ------------------------------------------------------------------ #
    def _load_cover(self, path, size=(140, 190)):
        if not path or not os.path.exists(path):
            return None
        cache_key = (path, size)
        if cache_key in self._cover_cache:
            return self._cover_cache[cache_key]
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            if CTkImage:
                ctk_img = CTkImage(light_image=img, dark_image=img, size=size)
                self._cover_cache[cache_key] = ctk_img
                return ctk_img
        except Exception:
            pass
        return None

    def browse_add_photo(self):
        self._browse_photo("a")

    def browse_edit_photo(self):
        self._browse_photo("e")

    def _browse_photo(self, prefix):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            setattr(self, f"_{prefix}_foto_path", path)
            try:
                img = Image.open(path).resize((140, 190), Image.LANCZOS)
                if CTkImage:
                    preview = CTkImage(light_image=img, dark_image=img, size=(140, 190))
                    setattr(self, f"_{prefix}_preview_img", preview)
                    getattr(self, f"{prefix}_preview").configure(image=preview, text="")
            except Exception:
                setattr(self, f"_{prefix}_preview_img", None)

    # ------------------------------------------------------------------ #
    #  GRID DE TARJETAS (RENDERIZADO OPTIMIZADO)
    # ------------------------------------------------------------------ #
    def render_reviews(self):
        if self._render_job:
            self.after_cancel(self._render_job)
            self._render_job = None

        reviews = self.db.get("reviews")

        # 1. Devolver tarjetas al pool
        for card in self._visible_cards:
            card.grid_remove()
            self._card_pool.append(card)
        self._visible_cards.clear()

        # 2. Limpiar widgets huérfanos
        for w in self.scroll.winfo_children():
            if w not in self._card_pool:
                w.destroy()

        if not reviews:
            lbl = CTkLabel(self.scroll, text="Aún no hay reseñas guardadas.", font=("Arial", 16))
            lbl.pack(pady=50, fill="x")
            lbl.configure(anchor="center")
            return

        # Calcular columnas según ancho configurado (estable)
        scroll_w = int(self.scroll.cget("width"))
        available_w = max(600, scroll_w - 60)
        card_total_w = 200 + 20
        cols = max(1, available_w // card_total_w)

        total = len(reviews)
        chunk = 6

        if hasattr(self.scroll, '_parent_canvas'):
            self.scroll._parent_canvas.yview_moveto(0)

        def draw_batch(start):
            end = min(start + chunk, total)
            for idx in range(start, end):
                row = idx // cols
                col = idx % cols

                if self._card_pool:
                    card = self._card_pool.pop()
                    self._update_review_card(card, reviews[idx])
                else:
                    card = self.create_review_card(self.scroll, reviews[idx])

                card.grid(row=row, column=col, padx=10, pady=15)
                self._bind_card_click(card, reviews[idx])
                self._visible_cards.append(card)

            if end < total:
                self._render_job = self.after(25, lambda: draw_batch(end))
            else:
                max_pool = max(cols * 3, 12)
                while len(self._card_pool) > max_pool:
                    c = self._card_pool.pop()
                    c.destroy()
                self.update_idletasks()

        draw_batch(0)

    def create_review_card(self, parent, review=None):
        """Estructura exacta de la tarjeta original (place) para mantener el mismo ancho/visual."""
        card = CTkFrame(parent, width=200, height=340, corner_radius=12, border_width=2)
        card.grid_propagate(False)
        card.configure(cursor="hand2")

        refs = {}
        card._refs = refs

        # Cover (place como en el original)
        cover = CTkFrame(card, width=140, height=190, corner_radius=8, fg_color="#FFFFFF")
        cover.place(relx=0.5, y=12, anchor="n")
        refs['cover_img'] = CTkLabel(cover, text="")
        refs['cover_img'].place(relx=0.5, rely=0.5, anchor="center")

        # Textos con place (posiciones exactas del original)
        refs['title'] = CTkLabel(card, text="", font=("Arial", 13, "bold"))
        refs['title'].place(relx=0.5, y=214, anchor="n")

        refs['author'] = CTkLabel(card, text="", font=("Arial", 11), text_color="#5DADE2")
        refs['author'].place(relx=0.5, y=238, anchor="n")

        refs['stars'] = StarRating(card, rating=0, size=16, readonly=True)
        refs['stars'].place(relx=0.5, y=262, anchor="n")

        if review:
            self._update_review_card(card, review)
        return card

    def _update_review_card(self, card, review):
        refs = card._refs
        img = self._load_cover(review.get("foto"), size=(140, 190))
        if img:
            refs['cover_img'].configure(image=img, text="")
        else:
            refs['cover_img'].configure(image=None, text="Libro", font=("Arial", 48))
        refs['title'].configure(text=review.get("titulo", "Sin título")[:22])
        refs['author'].configure(text=review.get("autor", "")[:20])
        refs['stars'].set_rating(review.get("rating", 0))

    def _bind_card_click(self, widget, review):
        widget.bind("<Button-1>", lambda e, r=review: self.open_detail_panel(r))
        for child in widget.winfo_children():
            self._bind_card_click(child, review)

    # ------------------------------------------------------------------ #
    #  VISTA DETALLE (LECTURA) - MISMO ORDEN QUE NUEVA RESEÑA
    # ------------------------------------------------------------------ #
    def open_detail_panel(self, review):
        self._current_review = review
        for w in self.detail_container.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self.detail_container, width=900, height=600, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ===== FILA SUPERIOR: Portada (izq) | Info libro (der) =====
        top_row = CTkFrame(scroll, fg_color="transparent")
        top_row.pack(fill="x", pady=(10, 25), padx=10)

        # --- COLUMNA IZQUIERDA: Portada + Estrellas ---
        left_col = CTkFrame(top_row, fg_color="transparent")
        left_col.pack(side="left", padx=(0, 20))

        # Portada
        cover_box = CTkFrame(left_col, width=240, height=320, corner_radius=14, fg_color="#FFFFFF")
        cover_box.pack(pady=(0, 10))
        cover_box.pack_propagate(False)
        img = self._load_cover(review.get("foto"), size=(240, 320))
        if img:
            CTkLabel(cover_box, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            CTkLabel(cover_box, text="Libro", font=("Arial", 90)).place(relx=0.5, rely=0.5, anchor="center")

        # Estrellas
        stars = StarRating(left_col, rating=review.get("rating", 0), size=32, readonly=True)
        stars.pack(pady=(5, 0))

        # --- COLUMNA DERECHA: Info del libro ---
        right_col = CTkFrame(top_row, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, pady=25)

        # Título
        CTkLabel(right_col, text="TÍTULO", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
        CTkLabel(right_col, text=review.get("titulo", "Sin título"), font=("Helvetica", 28, "bold")).pack(anchor="w", pady=(0, 10))

        # Autor
        CTkLabel(right_col, text="AUTOR", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
        CTkLabel(right_col, text=review.get("autor", "Autor desconocido"), font=("Arial", 18), text_color="#aaa").pack(anchor="w", pady=(0, 12))

        # Fechas + Páginas + Género (en una fila)
        meta_row = CTkFrame(right_col, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 10))

        # Fecha inicio
        c1 = CTkFrame(meta_row, fg_color="transparent")
        c1.pack(side="left", padx=(0, 10))
        CTkLabel(c1, text="FECHA DE INICIO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        CTkLabel(c1, text=review.get("fecha_inicio", "-"), font=("Arial", 12)).pack()

        # Fecha final
        c2 = CTkFrame(meta_row, fg_color="transparent")
        c2.pack(side="left", padx=(0, 10))
        CTkLabel(c2, text="FECHA DE FINAL", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        CTkLabel(c2, text=review.get("fecha_final", "-"), font=("Arial", 12)).pack()

        # Páginas
        c3 = CTkFrame(meta_row, fg_color="transparent")
        c3.pack(side="left", padx=(0, 10))
        CTkLabel(c3, text="N° DE PÁGINAS", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        CTkLabel(c3, text=str(review.get("paginas", "?")), font=("Arial", 12)).pack()

        # Género
        c4 = CTkFrame(meta_row, fg_color="transparent")
        c4.pack(side="left", padx=(0, 10))
        CTkLabel(c4, text="GÉNERO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        CTkLabel(c4, text=review.get("genero", "-"), font=("Arial", 12)).pack()

        # Formato
        fmt = review.get("formato", "fisico")
        fmt_text = {"fisico": "Físico", "digital": "Digital", "audiolibro": "Audiolibro"}
        fmt_frame = CTkFrame(right_col, fg_color="transparent")
        fmt_frame.pack(anchor="w", pady=(0, 5))
        CTkLabel(fmt_frame, text="LO LEÍ EN:", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(side="left", padx=(0, 10))
        CTkLabel(fmt_frame, text=fmt_text.get(fmt, fmt.capitalize()), font=("Arial", 12)).pack(side="left")

        # ===== PERSONAJES =====
        chars_row = CTkFrame(scroll, fg_color="transparent")
        chars_row.pack(fill="x", pady=(0, 15), padx=10)

        c_fav = CTkFrame(chars_row, fg_color="transparent")
        c_fav.pack(side="left", padx=(0, 20))
        CTkLabel(c_fav, text="PERSONAJE FAVORITO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        CTkLabel(c_fav, text=review.get("personaje_fav", "-") or "-", font=("Arial", 13, "bold"), text_color="#ff6b6b").pack()

        c_hate = CTkFrame(chars_row, fg_color="transparent")
        c_hate.pack(side="left")
        CTkLabel(c_hate, text="PERSONAJE ODIADO", font=("Arial", 10, "bold"), text_color="#5DADE2").pack(anchor="w")
        CTkLabel(c_hate, text=review.get("personaje_odiado", "-") or "-", font=("Arial", 13, "bold"), text_color="#5DADE2").pack()

        # ===== FILA INFERIOR: Sentimientos (izq) | Frases + Reseña (der) =====
        bottom_row = CTkFrame(scroll, fg_color="transparent")
        bottom_row.pack(fill="both", expand=True, pady=(0, 10), padx=10)

        # --- SENTIMIENTOS (columna izquierda) ---
        sent = review.get("sentimientos", {})
        active_sent = {k: v for k, v in sent.items() if v > 0}

        sent_col = CTkFrame(bottom_row, fg_color="#F5FAFC", corner_radius=14)
        sent_col.pack(side="left", fill="y", padx=(0, 20), pady=5)

        CTkLabel(sent_col, text="SENTIMIENTOS", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 10))

        feelings = [
            ("AMOR", "💗", "amor", "#FF3CCB"),
            ("ENOJO", "💢", "enojo", "#931212"),
            ("TRISTEZA", "💧", "tristeza", "#596DEF"),
            ("PLOT", "🔄️", "plot", "#F3FF07"),
            ("REFLEXIÓN", "💭", "reflexion", "#A716E0"),
            ("FELICIDAD", "🙂", "felicidad", "#1DD62C"),
            ("HOT", "🔥", "hot", "#D90808")
        ]

        for name, icon, key, color in feelings:
            val = active_sent.get(key, 0)
            row = CTkFrame(sent_col, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            CTkLabel(row, text=name, font=("Arial", 11, "bold"), text_color=color).pack(side="left", padx=(0, 8))
            # Mostrar emojis según valor guardado
            icons_frm = CTkFrame(row, fg_color="transparent")
            icons_frm.pack(side="left")
            for i in range(5):
                CTkLabel(icons_frm, text=icon, font=("Arial", 16),
                         text_color=color if i < val else "#2E86C1").pack(side="left", padx=1)

        # --- FRASES + RESEÑA (columna derecha) ---
        text_col = CTkFrame(bottom_row, fg_color="transparent")
        text_col.pack(side="left", fill="both", expand=True)

        # Frases destacadas
        if review.get("frases"):
            CTkLabel(text_col, text="FRASES", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
            frases_box = CTkFrame(text_col, fg_color="#F5FAFC", corner_radius=10)
            frases_box.pack(fill="x", pady=(0, 12))
            CTkLabel(frases_box, text=review["frases"], font=("Arial", 14), text_color="#2C3E50",
                     wraplength=600, justify="left").pack(anchor="w", padx=15, pady=12)

        # Reseña
        if review.get("resena"):
            CTkLabel(text_col, text="RESEÑA", font=("Arial", 11, "bold"), text_color="#5DADE2").pack(anchor="w", pady=(0, 2))
            resena_box = CTkFrame(text_col, fg_color="#F5FAFC", corner_radius=10)
            resena_box.pack(fill="both", expand=True)
            CTkLabel(resena_box, text=review["resena"], font=("Arial", 14), text_color="#2C3E50",
                     wraplength=600, justify="left").pack(anchor="w", padx=15, pady=12)

        self.scroll.pack_forget()
        self.add_panel.pack_forget()
        self.edit_panel.pack_forget()
        self.detail_panel.pack(fill="both", padx=20, pady=10, expand=True)

    def close_detail_panel(self):
        self.detail_panel.pack_forget()
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
        self._current_review = None

    def detail_to_edit(self):
        review = self._current_review
        if review:
            self.close_detail_panel()
            self.open_edit_panel(review)

    def detail_delete(self):
        if self._current_review:
            self.delete_review(self._current_review)
            self.close_detail_panel()

    # ------------------------------------------------------------------ #
    #  PANEL AÑADIR
    # ------------------------------------------------------------------ #
    def show_add_panel(self):
        self.scroll.pack_forget()
        self.detail_panel.pack_forget()
        self.edit_panel.pack_forget()
        self.add_panel.pack(fill="both", padx=20, pady=10, expand=True)

    def close_add_panel(self):
        self.add_panel.pack_forget()
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
        self._clear_form("add")

    def save_review(self):
        titulo = self.a_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Campo requerido", "El título es obligatorio.")
            return
        try:
            paginas = int(self.a_paginas.get().strip()) if self.a_paginas.get().strip() else 0
        except ValueError:
            paginas = 0

        review = {
            "id": Database.generate_id(),
            "titulo": titulo,
            "autor": self.a_autor.get().strip(),
            "fecha_inicio": self.a_fecha_inicio.get().strip(),
            "fecha_final": self.a_fecha_final.get().strip(),
            "paginas": paginas,
            "formato": self.a_formato.get(),
            "genero": self.a_genero.get().strip(),
            "rating": self.a_stars.rating,
            "personaje_fav": self.a_fav.get().strip(),
            "personaje_odiado": self.a_hate.get().strip(),
            "sentimientos": {k: v.value for k, v in self.a_feelings.items()},
            "frases": self.a_frases.get("1.0", "end").strip(),
            "resena": self.a_resena.get("1.0", "end").strip(),
            "foto": getattr(self, "_a_foto_path", None)
        }
        reviews = self.db.get("reviews")
        reviews.append(review)
        self.db.set("reviews", reviews)
        self._cover_cache.clear()
        messagebox.showinfo("Éxito", "Reseña guardada correctamente.")
        self.close_add_panel()
        self.render_reviews()

    # ------------------------------------------------------------------ #
    #  PANEL EDITAR
    # ------------------------------------------------------------------ #
    def open_edit_panel(self, review):
        self.edit_review_id = review.get("id")
        self.e_titulo.delete(0, "end")
        self.e_titulo.insert(0, review.get("titulo", ""))
        self.e_autor.delete(0, "end")
        self.e_autor.insert(0, review.get("autor", ""))
        self.e_fecha_inicio.delete(0, "end")
        self.e_fecha_inicio.insert(0, review.get("fecha_inicio", ""))
        self.e_fecha_final.delete(0, "end")
        self.e_fecha_final.insert(0, review.get("fecha_final", ""))
        self.e_paginas.delete(0, "end")
        self.e_paginas.insert(0, str(review.get("paginas", "")))
        self.e_genero.delete(0, "end")
        self.e_genero.insert(0, review.get("genero", ""))
        self.e_formato.set(review.get("formato", "fisico"))
        self.e_stars.set_rating(review.get("rating", 0))
        self.e_fav.delete(0, "end")
        self.e_fav.insert(0, review.get("personaje_fav", ""))
        self.e_hate.delete(0, "end")
        self.e_hate.insert(0, review.get("personaje_odiado", ""))

        sent = review.get("sentimientos", {})
        for k, ir in self.e_feelings.items():
            ir.set_value(sent.get(k, 0))

        self.e_frases.delete("1.0", "end")
        self.e_frases.insert("1.0", review.get("frases", ""))
        self.e_resena.delete("1.0", "end")
        self.e_resena.insert("1.0", review.get("resena", ""))

        # Portada
        foto = review.get("foto")
        setattr(self, "_e_foto_path", foto)
        setattr(self, "_e_preview_img", None)
        self.e_preview.configure(image=None, text="")
        if foto and os.path.exists(foto):
            try:
                img = Image.open(foto).resize((140, 190), Image.LANCZOS)
                if CTkImage:
                    preview = CTkImage(light_image=img, dark_image=img, size=(140, 190))
                    setattr(self, "_e_preview_img", preview)
                    self.e_preview.configure(image=preview, text="")
            except Exception:
                pass

        self.scroll.pack_forget()
        self.detail_panel.pack_forget()
        self.add_panel.pack_forget()
        self.edit_panel.pack(fill="both", padx=20, pady=10, expand=True)

    def close_edit_panel(self):
        self.edit_panel.pack_forget()
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
        self.render_reviews()

    def save_edit_review(self):
        if not self.edit_review_id:
            return
        try:
            paginas = int(self.e_paginas.get().strip()) if self.e_paginas.get().strip() else 0
        except ValueError:
            paginas = 0

        reviews = self.db.get("reviews")
        for r in reviews:
            if r.get("id") == self.edit_review_id:
                r["titulo"] = self.e_titulo.get().strip()
                r["autor"] = self.e_autor.get().strip()
                r["fecha_inicio"] = self.e_fecha_inicio.get().strip()
                r["fecha_final"] = self.e_fecha_final.get().strip()
                r["paginas"] = paginas
                r["formato"] = self.e_formato.get()
                r["genero"] = self.e_genero.get().strip()
                r["rating"] = self.e_stars.rating
                r["personaje_fav"] = self.e_fav.get().strip()
                r["personaje_odiado"] = self.e_hate.get().strip()
                r["sentimientos"] = {k: v.value for k, v in self.e_feelings.items()}
                r["frases"] = self.e_frases.get("1.0", "end").strip()
                r["resena"] = self.e_resena.get("1.0", "end").strip()
                r["foto"] = getattr(self, "_e_foto_path", None)
                break
        self.db.set("reviews", reviews)
        self._cover_cache.clear()
        messagebox.showinfo("Éxito", "Cambios guardados.")
        self.close_edit_panel()

    def delete_review(self, review):
        if not messagebox.askyesno("Confirmar", f'¿Eliminar la reseña de "{review.get("titulo")}"?'):
            return
        reviews = [r for r in self.db.get("reviews") if r.get("id") != review.get("id")]
        self.db.set("reviews", reviews)
        self._cover_cache.clear()
        self.render_reviews()

    def _clear_form(self, mode):
        prefix = "a_" if mode == "add" else "e_"
        getattr(self, f"{prefix}titulo").delete(0, "end")
        getattr(self, f"{prefix}autor").delete(0, "end")
        getattr(self, f"{prefix}fecha_inicio").delete(0, "end")
        getattr(self, f"{prefix}fecha_final").delete(0, "end")
        getattr(self, f"{prefix}paginas").delete(0, "end")
        getattr(self, f"{prefix}genero").delete(0, "end")
        getattr(self, f"{prefix}formato").set("fisico")
        getattr(self, f"{prefix}stars").set_rating(0)
        getattr(self, f"{prefix}fav").delete(0, "end")
        getattr(self, f"{prefix}hate").delete(0, "end")
        getattr(self, f"{prefix}frases").delete("1.0", "end")
        getattr(self, f"{prefix}resena").delete("1.0", "end")
        for ir in getattr(self, f"{prefix}feelings").values():
            ir.set_value(0)
        setattr(self, f"_{prefix}foto_path", None)
        setattr(self, f"_{prefix}preview_img", None)
        getattr(self, f"{prefix}preview").configure(image=None, text="")

    def refresh(self):
        self.close_add_panel()
        self.close_edit_panel()
        self.close_detail_panel()
        self._cover_cache.clear()
        self.render_reviews()