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

from database import Database
from widgets import StarRating, IconRating


# ------------------------------------------------------------------ #
#  WIDGET AUXILIAR: EmojiRating (5 emojis interactivos tipo estrellas)
# ------------------------------------------------------------------ #
class EmojiRating(ctk.CTkFrame):
    def __init__(self, master, emoji="♥", value=0, size=18, color="#ff6b6b", command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.value = value
        self.rating = value  # alias para compatibilidad
        self.emoji = emoji
        self.color = color
        self.size = size
        self.command = command
        self.labels = []
        for i in range(5):
            lbl = CTkLabel(self, text=emoji, font=("Arial", size), text_color="#444")
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

    set_rating = set_value  # alias

    def update_ui(self):
        for i, lbl in enumerate(self.labels):
            lbl.configure(text_color=self.color if i < self.value else "#444")


class ReviewFrame(CTkFrame):
    ...
    # (todo lo demás de la clase sigue igual, solo cambia _build_form)
    ...
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")
        self._cover_cache = {}
        self._current_review = None

        # ---------- HEADER ----------
        hdr = CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 5), padx=20)
        CTkLabel(hdr, text="✍️ Reviews", font=("Helvetica", 28, "bold")).pack(side="left")
        self.btn_toggle_add = CTkButton(hdr, text="+ Nueva Reseña", command=self.show_add_panel)
        self.btn_toggle_add.pack(side="right", padx=5)

        # ---------- GRID DE TARJETAS ----------
        self.scroll = CTkScrollableFrame(self, width=900, height=520, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        # ---------- PANEL DETALLE (LECTURA) ----------
        self.detail_panel = CTkFrame(self, fg_color="#1e1e1e", corner_radius=16, border_width=2, border_color="#3a3a3a")
        self.detail_container = CTkFrame(self.detail_panel, fg_color="transparent")
        self.detail_container.pack(expand=True, fill="both", padx=20, pady=10)

        detail_btns = CTkFrame(self.detail_panel, fg_color="transparent")
        detail_btns.pack(pady=(5, 15))
        CTkButton(detail_btns, text="✕ Salir", command=self.close_detail_panel,
                  height=38, font=("Arial", 14), corner_radius=10, fg_color="#555", hover_color="#666").pack(side="left", padx=8)
        CTkButton(detail_btns, text="✏️ Editar", command=self.detail_to_edit,
                  height=38, font=("Arial", 14, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(detail_btns, text="🗑 Eliminar", command=self.detail_delete,
                  height=38, font=("Arial", 14), corner_radius=10,
                  fg_color="red", hover_color="darkred").pack(side="left", padx=8)

        # ---------- PANEL AÑADIR ----------
        self.add_panel = CTkFrame(self, fg_color="#1e1e1e", corner_radius=16, border_width=2, border_color="#3a3a3a")
        CTkLabel(self.add_panel, text="✨ NUEVA RESEÑA", font=("Helvetica", 22, "bold")).pack(pady=(15, 10))
        self.add_scroll = ctk.CTkScrollableFrame(self.add_panel, width=720, height=460, fg_color="transparent")
        self.add_scroll.pack(padx=25, pady=5, fill="both", expand=True)
        self._build_form(self.add_scroll, mode="add")

        add_btns = CTkFrame(self.add_panel, fg_color="transparent")
        add_btns.pack(pady=(5, 15))
        CTkButton(add_btns, text="💾 Guardar", command=self.save_review,
                  height=36, font=("Arial", 13, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(add_btns, text="✕ Cancelar", command=self.close_add_panel,
                  height=36, font=("Arial", 13), corner_radius=10, fg_color="#555", hover_color="#666").pack(side="left", padx=8)

        # ---------- PANEL EDITAR ----------
        self.edit_panel = CTkFrame(self, fg_color="#1e1e1e", corner_radius=16, border_width=2, border_color="#3a3a3a")
        self.edit_review_id = None
        CTkLabel(self.edit_panel, text="✏️ EDITAR RESEÑA", font=("Helvetica", 22, "bold")).pack(pady=(15, 10))
        self.edit_scroll = ctk.CTkScrollableFrame(self.edit_panel, width=720, height=460, fg_color="transparent")
        self.edit_scroll.pack(padx=25, pady=5, fill="both", expand=True)
        self._build_form(self.edit_scroll, mode="edit")

        edit_btns = CTkFrame(self.edit_panel, fg_color="transparent")
        edit_btns.pack(pady=(5, 15))
        CTkButton(edit_btns, text="💾 Guardar cambios", command=self.save_edit_review,
                  height=36, font=("Arial", 13, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(edit_btns, text="✕ Cancelar", command=self.close_edit_panel,
                  height=36, font=("Arial", 13), corner_radius=10, fg_color="#555", hover_color="#666").pack(side="left", padx=8)

        self.render_reviews()

    # ------------------------------------------------------------------ #
    #  FORMULARIO REUTILIZABLE (add / edit)
    # ------------------------------------------------------------------ #
    def _build_form(self, parent, mode="add"):
        prefix = "a_" if mode == "add" else "e_"

        def section(title_text, icon=""):
            sec = CTkFrame(parent, fg_color="#252525", corner_radius=14)
            sec.pack(fill="x", pady=(0, 18), padx=5)
            CTkLabel(sec, text=f"{icon}  {title_text}", font=("Helvetica", 18, "bold")).pack(
                anchor="w", padx=20, pady=(15, 12))
            content = CTkFrame(sec, fg_color="transparent")
            content.pack(fill="x", padx=20, pady=(0, 15))
            return content

        # --- SECCIÓN: Información del libro ---
        info = section("Información del libro", "📚")

        CTkLabel(info, text="Título *", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        setattr(self, f"{prefix}titulo", CTkEntry(info, width=600, height=36, corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}titulo").pack(fill="x", pady=(0, 10))

        CTkLabel(info, text="Autor", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        setattr(self, f"{prefix}autor", CTkEntry(info, width=600, height=36, corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}autor").pack(fill="x", pady=(0, 10))

        row_meta = CTkFrame(info, fg_color="transparent")
        row_meta.pack(fill="x", pady=(0, 10))
        for txt, attr, w in [
            ("Inicio", "fecha_inicio", 140),
            ("Final", "fecha_final", 140),
            ("Páginas", "paginas", 100),
            ("Género", "genero", 160)
        ]:
            c = CTkFrame(row_meta, fg_color="transparent")
            c.pack(side="left", padx=(0, 12))
            CTkLabel(c, text=txt + ":", font=("Arial", 11, "bold")).pack(anchor="w")
            setattr(self, f"{prefix}{attr}", CTkEntry(c, width=w, height=32, corner_radius=8, font=("Arial", 12)))
            getattr(self, f"{prefix}{attr}").pack()

        CTkLabel(info, text="Formato:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 4))
        setattr(self, f"{prefix}formato", ctk.StringVar(value="fisico"))
        fmt_frame = CTkFrame(info, fg_color="transparent")
        fmt_frame.pack(anchor="w", pady=(0, 5))
        for val, txt in [("fisico", "📖 Físico"), ("digital", "💻 Digital"), ("audiolibro", "🎧 Audiolibro")]:
            CTkRadioButton(fmt_frame, text=txt, variable=getattr(self, f"{prefix}formato"),
                           value=val, font=("Arial", 12)).pack(side="left", padx=12)

        # --- SECCIÓN: Calificación ---
        sec_rating = section("Calificación", "⭐")
        setattr(self, f"{prefix}stars", StarRating(sec_rating, rating=0, size=32))
        getattr(self, f"{prefix}stars").pack(anchor="w")

        # --- SECCIÓN: Personajes ---
        sec_chars = section("Personajes", "🎭")
        chars_row = CTkFrame(sec_chars, fg_color="transparent")
        chars_row.pack(fill="x")
        CTkLabel(chars_row, text="Favorito:", font=("Arial", 12, "bold")).pack(side="left")
        setattr(self, f"{prefix}fav", CTkEntry(chars_row, width=200, height=34, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}fav").pack(side="left", padx=(8, 25))
        CTkLabel(chars_row, text="Odiado:", font=("Arial", 12, "bold")).pack(side="left")
        setattr(self, f"{prefix}hate", CTkEntry(chars_row, width=200, height=34, corner_radius=8, font=("Arial", 12)))
        getattr(self, f"{prefix}hate").pack(side="left", padx=8)

        # --- SECCIÓN: Sentimientos ---
        sec_sent = section("Sentimientos", "💭")
        sent_grid = CTkFrame(sec_sent, fg_color="transparent")
        sent_grid.pack(fill="x")

        feelings = [
            ("Amor", "♥", "amor", "#ff6b6b"),
            ("Enojo", "😠", "enojo", "#e74c3c"),
            ("Tristeza", "💧", "tristeza", "#3498db"),
            ("Plot", "✦", "plot", "#f1c40f"),
            ("Reflexión", "🧠", "reflexion", "#9b59b6"),
            ("Felicidad", "☺", "felicidad", "#2ecc71"),
            ("Hot", "🔥", "hot", "#e67e22")
        ]
        setattr(self, f"{prefix}feelings", {})
        for idx, (name, icon, key, color) in enumerate(feelings):
            cell = CTkFrame(sent_grid, fg_color="#1e1e1e", corner_radius=10, width=115, height=80)
            cell.grid(row=idx // 4, column=idx % 4, padx=8, pady=6)
            cell.grid_propagate(False)
            CTkLabel(cell, text=name, font=("Arial", 12, "bold"), text_color=color).place(
                relx=0.5, y=18, anchor="center")
            er = EmojiRating(cell, emoji=icon, value=0, size=18, color=color)
            er.place(relx=0.5, y=52, anchor="center")
            getattr(self, f"{prefix}feelings")[key] = er

        # --- SECCIÓN: Frases destacadas ---
        sec_frases = section("Frases destacadas", "✨")
        setattr(self, f"{prefix}frases", CTkTextbox(sec_frases, width=600, height=80,
                                                    corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}frases").pack(fill="x")

        # --- SECCIÓN: Reseña ---
        sec_res = section("Reseña", "📝")
        setattr(self, f"{prefix}resena", CTkTextbox(sec_res, width=600, height=120,
                                                    corner_radius=10, font=("Arial", 13)))
        getattr(self, f"{prefix}resena").pack(fill="x")

        # --- SECCIÓN: Portada ---
        sec_foto = section("Portada", "🖼️")
        foto_row = CTkFrame(sec_foto, fg_color="transparent")
        foto_row.pack(fill="x")
        CTkButton(foto_row, text="📁 Examinar", width=130, height=36, corner_radius=10,
                  font=("Arial", 12), command=getattr(self, f"browse_{mode}_photo")).pack(
            side="left", padx=(0, 15))
        setattr(self, f"{prefix}preview", CTkLabel(foto_row, text="", width=50, height=70,
                                                  fg_color="#2b2b2b", corner_radius=8))
        getattr(self, f"{prefix}preview").pack(side="left")
        setattr(self, f"_{prefix}foto_path", None)
        setattr(self, f"_{prefix}preview_img", None)

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
                img = Image.open(path).resize((40, 55), Image.LANCZOS)
                if CTkImage:
                    preview = CTkImage(light_image=img, dark_image=img, size=(40, 55))
                    setattr(self, f"_{prefix}_preview_img", preview)
                    getattr(self, f"{prefix}_preview").configure(image=preview, text="")
            except Exception:
                setattr(self, f"_{prefix}_preview_img", None)

    # ------------------------------------------------------------------ #
    #  GRID DE TARJETAS
    # ------------------------------------------------------------------ #
    def render_reviews(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        reviews = self.db.get("reviews")
        if not reviews:
            CTkLabel(self.scroll, text="Aún no hay reseñas guardadas.", font=("Arial", 16)).pack(pady=50)
            return

        scroll_w = self.scroll.cget("width")
        available_w = max(600, int(scroll_w) - 20)
        card_total_w = 200 + 20
        cols = max(1, available_w // card_total_w)

        row, col = 0, 0
        for rev in reviews:
            card = self.create_review_card(self.scroll, rev)
            card.grid(row=row, column=col, padx=10, pady=15)
            self._bind_card_click(card, rev)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def create_review_card(self, parent, review):
        card = CTkFrame(parent, width=200, height=340, corner_radius=12, border_width=2)
        card.grid_propagate(False)
        card.configure(cursor="hand2")

        cover = CTkFrame(card, width=140, height=190, corner_radius=8, fg_color="#2b2b2b")
        cover.place(relx=0.5, y=12, anchor="n")
        img = self._load_cover(review.get("foto"), size=(140, 190))
        if img:
            CTkLabel(cover, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            CTkLabel(cover, text="📕", font=("Arial", 48)).place(relx=0.5, rely=0.5, anchor="center")

        y = 214
        CTkLabel(card, text=review.get("titulo", "Sin título")[:22], font=("Arial", 13, "bold")).place(relx=0.5, y=y, anchor="n")
        y += 24
        CTkLabel(card, text=review.get("autor", "")[:20], font=("Arial", 11), text_color="#888").place(relx=0.5, y=y, anchor="n")
        y += 24
        stars = StarRating(card, rating=review.get("rating", 0), size=16, readonly=True)
        stars.place(relx=0.5, y=y, anchor="n")

        return card

    def _bind_card_click(self, widget, review):
        widget.bind("<Button-1>", lambda e, r=review: self.open_detail_panel(r))
        for child in widget.winfo_children():
            self._bind_card_click(child, review)

    # ------------------------------------------------------------------ #
    #  VISTA DETALLE (LECTURA)
    # ------------------------------------------------------------------ #
    def open_detail_panel(self, review):
        self._current_review = review
        for w in self.detail_container.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self.detail_container, width=900, height=600, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ===== CABECERA: Portada grande + Info principal =====
        header = CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", pady=(10, 25), padx=10)

        # Portada
        cover_box = CTkFrame(header, width=240, height=320, corner_radius=14, fg_color="#2b2b2b")
        cover_box.pack(side="left", padx=(10, 35))
        cover_box.pack_propagate(False)
        img = self._load_cover(review.get("foto"), size=(240, 320))
        if img:
            CTkLabel(cover_box, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            CTkLabel(cover_box, text="📕", font=("Arial", 90)).place(relx=0.5, rely=0.5, anchor="center")

        # Info derecha
        info = CTkFrame(header, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=25)

        CTkLabel(info, text=review.get("titulo", "Sin título"), font=("Helvetica", 34, "bold")).pack(anchor="w")
        CTkLabel(info, text=f"de {review.get('autor', 'Autor desconocido')}", font=("Arial", 18), text_color="#aaa").pack(anchor="w", pady=(4, 18))

        stars = StarRating(info, rating=review.get("rating", 0), size=32, readonly=True)
        stars.pack(anchor="w", pady=(0, 25))

        # Metadatos en grid
        meta_grid = CTkFrame(info, fg_color="transparent")
        meta_grid.pack(anchor="w", pady=5)
        fmt = review.get("formato", "fisico")
        fmt_text = {"fisico": "📖 Físico", "digital": "💻 Digital", "audiolibro": "🎧 Audiolibro"}
        metas = [
            fmt_text.get(fmt, fmt.capitalize()),
            f"📄 {review.get('paginas','?')} páginas",
            f"🎭 {review.get('genero','')}",
            f"📅 {review.get('fecha_inicio','')} → {review.get('fecha_final','')}"
        ]
        for i, txt in enumerate(metas):
            CTkLabel(meta_grid, text=txt, font=("Arial", 15), text_color="#ccc").grid(
                row=i//2, column=i%2, sticky="w", padx=(0, 30), pady=7)

        # Personajes
        if review.get("personaje_fav") or review.get("personaje_odiado"):
            chars = CTkFrame(info, fg_color="transparent")
            chars.pack(anchor="w", pady=(25, 5))
            if review.get("personaje_fav"):
                CTkLabel(chars, text=f"❤️  Favorito: {review['personaje_fav']}",
                         font=("Arial", 15, "bold"), text_color="#ff6b6b").pack(side="left", padx=(0, 35))
            if review.get("personaje_odiado"):
                CTkLabel(chars, text=f"💀  Odiado: {review['personaje_odiado']}",
                         font=("Arial", 15, "bold"), text_color="#888").pack(side="left")

        # ===== SENTIMIENTOS (más compactos, multilinea) =====
        sent = review.get("sentimientos", {})
        active_sent = {k: v for k, v in sent.items() if v > 0}
        if active_sent:
            sent_box = CTkFrame(scroll, fg_color="#252525", corner_radius=14)
            sent_box.pack(fill="x", padx=10, pady=(10, 25))

            CTkLabel(sent_box, text="💭 Sentimientos", font=("Helvetica", 20, "bold")).pack(
                anchor="w", padx=25, pady=(18, 12))

            sent_grid = CTkFrame(sent_box, fg_color="transparent")
            sent_grid.pack(fill="x", padx=20, pady=(0, 18))

            feelings = [
                ("Amor", "♥", "amor", "#ff6b6b"),
                ("Enojo", "😠", "enojo", "#e74c3c"),
                ("Tristeza", "💧", "tristeza", "#3498db"),
                ("Plot", "✦", "plot", "#f1c40f"),
                ("Reflexión", "🧠", "reflexion", "#9b59b6"),
                ("Felicidad", "☺", "felicidad", "#2ecc71"),
                ("Hot", "🔥", "hot", "#e67e22")
            ]

            col_idx, row_idx = 0, 0
            max_cols = 4  # <-- salta a nueva fila cada 4 tarjetas

            for name, icon, key, color in feelings:
                val = active_sent.get(key, 0)
                if val <= 0:
                    continue

                cell = CTkFrame(sent_grid, fg_color="#1e1e1e", corner_radius=10, width=115, height=75)
                cell.grid(row=row_idx, column=col_idx, padx=8, pady=6)
                cell.grid_propagate(False)

                CTkLabel(cell, text=name, font=("Arial", 12, "bold"), text_color=color).place(relx=0.5, y=18, anchor="center")

                icons_frm = CTkFrame(cell, fg_color="transparent")
                icons_frm.place(relx=0.5, y=50, anchor="center")
                for i in range(5):
                    CTkLabel(icons_frm, text=icon, font=("Arial", 16),
                             text_color=color if i < val else "#444").pack(side="left", padx=1)

                col_idx += 1
                if col_idx >= max_cols:
                    col_idx = 0
                    row_idx += 1

        # ===== FRASES DESTACADAS =====
        if review.get("frases"):
            box = CTkFrame(scroll, fg_color="#252525", corner_radius=14)
            box.pack(fill="x", padx=10, pady=(0, 25))
            CTkLabel(box, text="✨ Frases destacadas", font=("Helvetica", 20, "bold"), text_color="#f1c40f").pack(
                anchor="w", padx=25, pady=(18, 10))
            CTkLabel(box, text=review["frases"], font=("Arial", 15), text_color="#eee",
                     wraplength=860, justify="left").pack(anchor="w", padx=25, pady=(0, 20))

        # ===== RESEÑA =====
        if review.get("resena"):
            box = CTkFrame(scroll, fg_color="#252525", corner_radius=14)
            box.pack(fill="x", padx=10, pady=(0, 25))
            CTkLabel(box, text="📝 Reseña", font=("Helvetica", 20, "bold"), text_color="#bbb").pack(
                anchor="w", padx=25, pady=(18, 10))
            CTkLabel(box, text=review["resena"], font=("Arial", 15), text_color="#eee",
                     wraplength=860, justify="left").pack(anchor="w", padx=25, pady=(0, 20))

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
                img = Image.open(foto).resize((40, 55), Image.LANCZOS)
                if CTkImage:
                    preview = CTkImage(light_image=img, dark_image=img, size=(40, 55))
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