"""Biblioteca con grid de libros, estados y filtros TBR/Leídos."""
import os
from tkinter import messagebox, filedialog

import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkScrollableFrame, CTkOptionMenu, CTkRadioButton
)
from PIL import Image

try:
    from customtkinter import CTkImage
except ImportError:
    CTkImage = None

from database import Database
from widgets import StarRating


class BibliotecaFrame(CTkFrame):
    ESTADOS = {"no_leido": "No lo he leído", "leyendo": "Lo estoy leyendo", "leido": "Ya lo leí"}
    FILTROS = {"todos": "Todos", "tbr": "📚 TBR", "leidos": "✅ Leídos"}
    ORDEN = {
        "titulo": "🔤 Título A-Z",
        "rating": "⭐ Mejor valorados"
    }

    ESTADO_MAP = {
        "por leer": "no_leido",
        "no leido": "no_leido",
        "no_leido": "no_leido",
        "leyendo": "leyendo",
        "leido": "leido",
        "leído": "leido",
        "ya lo leí": "leido",
    }

    @classmethod
    def normalize_estado(cls, raw):
        return cls.ESTADO_MAP.get(str(raw).lower().strip(), "no_leido")

    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")
        self.filtro_actual = "todos"
        self.orden_actual = "titulo"
        self.add_panel_visible = False
        self._cover_cache = {}
        self._preview_img = None
        self._foto_path = None

        # Header
        hdr = CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 5), padx=20)
        CTkLabel(hdr, text="📖 BIBLIOTECA", font=("Helvetica", 28, "bold")).pack(side="left")

        # Barra de herramientas
        tools = CTkFrame(self, fg_color="transparent")
        tools.pack(fill="x", padx=20, pady=5)

        for key, text in self.FILTROS.items():
            CTkButton(tools, text=text, width=100,
                      command=lambda k=key: self.set_filtro(k)).pack(side="left", padx=5)

        CTkLabel(tools, text="🔍", font=("Arial", 14)).pack(side="left", padx=(20, 2))
        self.search_entry = CTkEntry(tools, width=200, placeholder_text="Buscar título o autor...")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.render_books())
        CTkButton(tools, text="✕", width=30, command=self.clear_search).pack(side="left", padx=2)

        CTkLabel(tools, text="Orden:", font=("Arial", 11)).pack(side="left", padx=(20, 5))
        self.orden_menu = CTkOptionMenu(tools, values=list(self.ORDEN.values()), width=160,
                                        command=self.set_orden)
        self.orden_menu.set(self.ORDEN["titulo"])
        self.orden_menu.pack(side="left", padx=5)

        self.btn_toggle_add = CTkButton(tools, text="+ Añadir Libro", command=self.toggle_add_panel)
        self.btn_toggle_add.pack(side="right", padx=5)

        # --- PANEL EMBEBIDO AÑADIR LIBRO ---
        self.add_panel = CTkFrame(self, fg_color="#1e1e1e", corner_radius=16, border_width=2, border_color="#3a3a3a")

        CTkLabel(self.add_panel, text="✨ NUEVO LIBRO", font=("Helvetica", 22, "bold")).pack(pady=(20, 15))

        self.add_container = CTkFrame(self.add_panel, fg_color="transparent")
        self.add_container.pack(expand=True, fill="both")

        self.add_scroll = ctk.CTkScrollableFrame(self.add_container, width=700, height=420, fg_color="transparent")
        self.add_scroll.pack(padx=30, pady=5, fill="both", expand=True)

        self.entries = {}

        def add_row(label_text, widget):
            row = CTkFrame(self.add_scroll, fg_color="transparent")
            row.pack(fill="x", pady=(6, 2))
            inner = CTkFrame(row, fg_color="transparent")
            inner.pack(expand=True)
            CTkLabel(inner, text=label_text, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
            widget(inner)
            return inner

        add_row("Título *", lambda inner: (
            self.entries.update({"titulo": CTkEntry(inner, width=600, height=32, corner_radius=8)}),
            self.entries["titulo"].pack()
        ))
        add_row("Autor", lambda inner: (
            self.entries.update({"autor": CTkEntry(inner, width=600, height=32, corner_radius=8)}),
            self.entries["autor"].pack()
        ))
        add_row("N° Páginas", lambda inner: (
            self.entries.update({"paginas": CTkEntry(inner, width=600, height=32, corner_radius=8)}),
            self.entries["paginas"].pack()
        ))
        add_row("Género", lambda inner: (
            self.entries.update({"genero": CTkEntry(inner, width=600, height=32, corner_radius=8)}),
            self.entries["genero"].pack()
        ))
        add_row("Ubicación", lambda inner: (
            self.entries.update({"ubicacion": CTkEntry(inner, width=600, height=32, corner_radius=8)}),
            self.entries["ubicacion"].pack()
        ))

        # Portada
        row_foto = CTkFrame(self.add_scroll, fg_color="transparent")
        row_foto.pack(fill="x", pady=(6, 2))
        inner_foto = CTkFrame(row_foto, fg_color="transparent")
        inner_foto.pack(expand=True)
        CTkLabel(inner_foto, text="Portada", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.add_foto_row = CTkFrame(inner_foto, fg_color="transparent")
        self.add_foto_row.pack(anchor="w")
        CTkButton(self.add_foto_row, text="📁 Examinar", width=120, height=32, corner_radius=8,
                  command=self.browse_photo).pack(side="left", padx=(0, 12))
        self.photo_preview = CTkLabel(self.add_foto_row, text="", width=40, height=55)
        self.photo_preview.pack(side="left")

        # Estado
        row_est = CTkFrame(self.add_scroll, fg_color="transparent")
        row_est.pack(fill="x", pady=(6, 2))
        inner_est = CTkFrame(row_est, fg_color="transparent")
        inner_est.pack(expand=True)
        CTkLabel(inner_est, text="Estado", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.estado_var = ctk.StringVar(value="")
        self.add_row_est = CTkFrame(inner_est, fg_color="transparent")
        self.add_row_est.pack(anchor="w")
        for val, txt in [("no_leido", "No leído"), ("leyendo", "Leyendo"), ("leido", "Leído")]:
            CTkRadioButton(self.add_row_est, text=txt, variable=self.estado_var, value=val,
                           command=self.on_estado_change).pack(side="left", padx=10)

        # Extras para "leído"
        self.extras_frame = CTkFrame(self.add_scroll, fg_color="transparent")
        self.extras_frame.pack(fill="x", pady=(6, 0))
        self.extras_frame.pack_forget()

        row_extras = CTkFrame(self.extras_frame, fg_color="transparent")
        row_extras.pack(fill="x")
        inner_extras = CTkFrame(row_extras, fg_color="transparent")
        inner_extras.pack(expand=True)

        CTkLabel(inner_extras, text="Calificación", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.add_stars = StarRating(inner_extras, rating=0, size=26)
        self.add_stars.pack(anchor="w")

        CTkLabel(inner_extras, text="Formato", font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 2))
        self.fmt_var = ctk.StringVar(value="fisico")
        self.add_row_fmt = CTkFrame(inner_extras, fg_color="transparent")
        self.add_row_fmt.pack(anchor="w")
        for val, txt in [("fisico", "Físico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(self.add_row_fmt, text=txt, variable=self.fmt_var, value=val).pack(side="left", padx=10)

        btn_add_row = CTkFrame(self.add_container, fg_color="transparent")
        btn_add_row.pack(pady=(15, 20))
        CTkButton(btn_add_row, text="💾 Guardar Libro", command=self.save_book,
                  height=38, font=("Arial", 14, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(btn_add_row, text="✕ Cancelar", command=self.close_add_panel,
                  height=38, font=("Arial", 14), corner_radius=10, fg_color="#555", hover_color="#666").pack(side="left", padx=8)

        # --- PANEL EMBEBIDO EDITAR LIBRO ---
        self.edit_panel = CTkFrame(self, fg_color="#1e1e1e", corner_radius=16, border_width=2, border_color="#3a3a3a")
        self.edit_book_id = None

        CTkLabel(self.edit_panel, text="✏️ EDITAR LIBRO", font=("Helvetica", 22, "bold")).pack(pady=(20, 15))

        self.edit_container = CTkFrame(self.edit_panel, fg_color="transparent")
        self.edit_container.pack(expand=True, fill="both")

        self.edit_scroll = ctk.CTkScrollableFrame(self.edit_container, width=700, height=420, fg_color="transparent")
        self.edit_scroll.pack(padx=30, pady=5, fill="both", expand=True)

        def edit_row(label_text, widget):
            row = CTkFrame(self.edit_scroll, fg_color="transparent")
            row.pack(fill="x", pady=(6, 2))
            inner = CTkFrame(row, fg_color="transparent")
            inner.pack(expand=True)
            CTkLabel(inner, text=label_text, font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
            widget(inner)
            return inner

        edit_row("Título", lambda inner: (
            setattr(self, 'e_titulo', CTkEntry(inner, width=600, height=32, corner_radius=8)),
            self.e_titulo.pack()
        ))
        edit_row("Autor", lambda inner: (
            setattr(self, 'e_autor', CTkEntry(inner, width=600, height=32, corner_radius=8)),
            self.e_autor.pack()
        ))
        edit_row("Páginas", lambda inner: (
            setattr(self, 'e_pags', CTkEntry(inner, width=600, height=32, corner_radius=8)),
            self.e_pags.pack()
        ))
        edit_row("Género", lambda inner: (
            setattr(self, 'e_genero', CTkEntry(inner, width=600, height=32, corner_radius=8)),
            self.e_genero.pack()
        ))
        edit_row("Ubicación", lambda inner: (
            setattr(self, 'e_ubi', CTkEntry(inner, width=600, height=32, corner_radius=8)),
            self.e_ubi.pack()
        ))

        # Portada
        row_foto = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_foto.pack(fill="x", pady=(6, 2))
        inner_foto = CTkFrame(row_foto, fg_color="transparent")
        inner_foto.pack(expand=True)
        CTkLabel(inner_foto, text="Portada", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.edit_foto_row = CTkFrame(inner_foto, fg_color="transparent")
        self.edit_foto_row.pack(anchor="w")

        self.edit_foto_path = None
        self.edit_preview_img = None

        CTkButton(self.edit_foto_row, text="📁 Examinar", width=120, height=32, corner_radius=8,
                  command=self.browse_edit_photo).pack(side="left", padx=(0, 12))
        self.edit_preview = CTkLabel(self.edit_foto_row, text="", width=40, height=55)
        self.edit_preview.pack(side="left")

        # Estado
        row_est = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_est.pack(fill="x", pady=(6, 2))
        inner_est = CTkFrame(row_est, fg_color="transparent")
        inner_est.pack(expand=True)
        CTkLabel(inner_est, text="Estado", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.e_estado = ctk.StringVar(value="no_leido")
        self.edit_row_est = CTkFrame(inner_est, fg_color="transparent")
        self.edit_row_est.pack(anchor="w")
        for val, txt in [("no_leido", "No leído"), ("leyendo", "Leyendo"), ("leido", "Leído")]:
            CTkRadioButton(self.edit_row_est, text=txt, variable=self.e_estado,
                           value=val, command=self.on_edit_estado_change).pack(side="left", padx=10)

        # Calificación y Formato (siempre visibles, controlados por edit_book)
        row_stars = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_stars.pack(fill="x", pady=(6, 2))
        inner_stars = CTkFrame(row_stars, fg_color="transparent")
        inner_stars.pack(expand=True)
        CTkLabel(inner_stars, text="Calificación", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.e_stars = StarRating(inner_stars, rating=0, size=26)
        self.e_stars.pack(anchor="w")

        row_fmt = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_fmt.pack(fill="x", pady=(6, 2))
        inner_fmt = CTkFrame(row_fmt, fg_color="transparent")
        inner_fmt.pack(expand=True)
        CTkLabel(inner_fmt, text="Formato", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 2))
        self.e_fmt = ctk.StringVar(value="fisico")
        self.edit_row_fmt = CTkFrame(inner_fmt, fg_color="transparent")
        self.edit_row_fmt.pack(anchor="w")
        for val, txt in [("fisico", "Físico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(self.edit_row_fmt, text=txt, variable=self.e_fmt,
                           value=val).pack(side="left", padx=10)

        btn_edit_row = CTkFrame(self.edit_container, fg_color="transparent")
        btn_edit_row.pack(pady=(15, 20))
        CTkButton(btn_edit_row, text="💾 Guardar cambios", command=self.save_edit_book,
                  height=38, font=("Arial", 14, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(btn_edit_row, text="✕ Cancelar", command=self.close_edit_panel,
                  height=38, font=("Arial", 14), corner_radius=10, fg_color="#555", hover_color="#666").pack(side="left", padx=8)

        self.scroll = CTkScrollableFrame(self, width=900, height=500, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render_books()

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.render_books()

    def toggle_add_panel(self):
        if self.add_panel_visible:
            self.close_add_panel()
        else:
            self.scroll.pack_forget()
            self.edit_panel.pack_forget()
            self.add_panel.pack(fill="both", padx=20, pady=10, expand=True)
            self.btn_toggle_add.configure(text="✕ Cerrar panel")
            self.add_panel_visible = True

    def close_add_panel(self):
        self.add_panel.pack_forget()
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
        self.btn_toggle_add.configure(text="+ Añadir Libro")
        self.add_panel_visible = False

    def on_estado_change(self):
        if self.estado_var.get() == "leido":
            self.extras_frame.pack(fill="x", padx=30, pady=5)
        else:
            self.extras_frame.pack_forget()

    def browse_photo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            self._foto_path = path
            try:
                img = Image.open(path).resize((40, 55), Image.LANCZOS)
                if CTkImage:
                    self._preview_img = CTkImage(light_image=img, dark_image=img, size=(40, 55))
                    self.photo_preview.configure(image=self._preview_img, text="")
            except Exception:
                self._preview_img = None

    def save_book(self):
        titulo = self.entries["titulo"].get().strip()
        if not titulo:
            messagebox.showwarning("Campo requerido", "El título es obligatorio.")
            return

        estado = self.estado_var.get()
        if not estado:
            messagebox.showwarning("Campo requerido", "Selecciona un estado para el libro.")
            return

        paginas = self.entries["paginas"].get().strip()
        try:
            paginas = int(paginas) if paginas else 0
        except ValueError:
            paginas = 0

        foto_path = self._foto_path or None

        new_book = {
            "id": Database.generate_id(),
            "titulo": titulo,
            "autor": self.entries["autor"].get().strip(),
            "paginas": paginas,
            "genero": self.entries["genero"].get().strip(),
            "ubicacion": self.entries["ubicacion"].get().strip(),
            "foto": foto_path,
            "estado": estado,
            "rating": self.add_stars.rating if estado == "leido" else 0,
            "formato": self.fmt_var.get() if estado == "leido" else "fisico"
        }
        books = self.db.get("books")
        books.append(new_book)
        self.db.set("books", books)

        for e in self.entries.values():
            e.delete(0, "end")
        self._foto_path = None
        self.estado_var.set("")
        self.extras_frame.pack_forget()
        self.add_stars.set_rating(0)
        self.fmt_var.set("fisico")
        self.photo_preview.configure(text="", image=None)
        self._cover_cache.clear()

        self.toggle_add_panel()
        self.render_books()

    def set_filtro(self, key):
        self.filtro_actual = key
        self.render_books()

    def set_orden(self, valor_texto):
        inv = {v: k for k, v in self.ORDEN.items()}
        self.orden_actual = inv.get(valor_texto, "reciente")
        self.render_books()

    def _filtrar_y_ordenar(self, books):
        if self.filtro_actual == "tbr":
            books = [b for b in books if self.normalize_estado(b.get("estado")) == "no_leido"]
        elif self.filtro_actual == "leidos":
            books = [b for b in books if self.normalize_estado(b.get("estado")) == "leido"]

        q = self.search_entry.get().strip().lower()
        if q:
            books = [b for b in books if q in b.get("titulo", "").lower()
                     or q in b.get("autor", "").lower()
                     or q in b.get("genero", "").lower()]

        if self.orden_actual == "titulo":
            books.sort(key=lambda b: b.get("titulo", "").lower())
        elif self.orden_actual == "rating":
            books.sort(key=lambda b: b.get("rating", 0), reverse=True)

        return books

    def render_books(self):
        # Cancelar renderizado anterior si existe (evita acumulación)
        if hasattr(self, '_render_job') and self._render_job:
            self.after_cancel(self._render_job)
            self._render_job = None

        # Limpiar
        for w in self.scroll.winfo_children():
            w.destroy()

        books = self._filtrar_y_ordenar(self.db.get("books"))

        if not books:
            msg = "No hay libros en esta vista."
            if self.filtro_actual == "tbr":
                msg = "Tu TBR está vacío 📭"
            elif self.filtro_actual == "leidos":
                msg = "Aún no has marcado ningún libro como leído."
            CTkLabel(self.scroll, text=msg, font=("Arial", 16)).pack(pady=50)
            return

        scroll_w = self.scroll.cget("width")
        available_w = max(600, int(scroll_w) - 20)
        card_total_w = 200 + 20
        cols = max(1, available_w // card_total_w)
        total = len(books)
        chunk = 10  # tarjetas por lote

        def draw_batch(start):
            end = min(start + chunk, total)
            for idx in range(start, end):
                row = idx // cols
                col = idx % cols
                card = self.create_book_card(self.scroll, books[idx])
                card.grid(row=row, column=col, padx=10, pady=15)

            if end < total:
                self._render_job = self.after(8, lambda: draw_batch(end))

        draw_batch(0)

    def _load_cover(self, path, size=(140, 200)):
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

    def create_book_card(self, parent, book):
        card = CTkFrame(parent, width=200, height=380, corner_radius=12, border_width=2)
        card.grid_propagate(False)

        cover = CTkFrame(card, width=140, height=160, corner_radius=8, fg_color="#2b2b2b")
        cover.place(relx=0.5, y=10, anchor="n")

        img = self._load_cover(book.get("foto"))
        if img:
            CTkLabel(cover, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            CTkLabel(cover, text="📕", font=("Arial", 48)).place(relx=0.5, rely=0.5, anchor="center")

        # Layout vertical con espaciado generoso para evitar solapamientos
        # Cover termina en y=10+160=170
        y = 188
        CTkLabel(card, text=book.get("titulo", "Sin título")[:22], font=("Arial", 14, "bold")).place(relx=0.5, y=y, anchor="center")
        y += 24
        CTkLabel(card, text=book.get("autor", "")[:20], font=("Arial", 11)).place(relx=0.5, y=y, anchor="center")
        y += 22
        CTkLabel(card, text=f"{book.get('paginas', '?')} pág. | {book.get('genero', '')[:15]}", font=("Arial", 10)).place(relx=0.5, y=y, anchor="center")
        y += 20
        CTkLabel(card, text=f"📍 {book.get('ubicacion', '')[:18]}", font=("Arial", 10)).place(relx=0.5, y=y, anchor="center")
        y += 24

        estado = self.normalize_estado(book.get("estado", "no_leido"))

        if estado != "leido":
            menu = CTkOptionMenu(card, values=list(self.ESTADOS.values()),
                                 command=lambda v, b=book: self.cambiar_estado(b, v),
                                 width=160)
            menu.set(self.ESTADOS[estado])
            menu.place(relx=0.5, y=y, anchor="center")
            y += 38  # altura del OptionMenu + margen
        else:
            CTkLabel(card, text=self.ESTADOS.get(estado, ""), font=("Arial", 10, "bold"),
                     text_color="#888").place(relx=0.5, y=y, anchor="center")
            y += 22
            stars = StarRating(card, rating=book.get("rating", 0), size=16, readonly=True)
            stars.place(relx=0.5, y=y, anchor="center")
            y += 24
            fmt = book.get("formato", "fisico")
            fmt_text = {"fisico": "📖 Físico", "digital": "💻 Digital", "audiolibro": "🎧 Audio"}
            CTkLabel(card, text=fmt_text.get(fmt, ""), font=("Arial", 10)).place(relx=0.5, y=y, anchor="center")
            y += 22

        # Botones siempre al final, fijos en y=355 para que nunca salgan del marco
        btn_row = CTkFrame(card, fg_color="transparent")
        btn_row.place(relx=0.5, y=355, anchor="center")
        CTkButton(btn_row, text="✏️", width=30, height=20, font=("Arial", 9),
                  command=lambda b=book: self.edit_book(b)).pack(side="left", padx=3)
        CTkButton(btn_row, text="🗑", width=30, height=20, fg_color="red", hover_color="darkred",
                  command=lambda b=book: self.delete_book(b)).pack(side="left", padx=3)

        return card

    def cambiar_estado(self, book, valor_texto):
        inv = {v: k for k, v in self.ESTADOS.items()}
        nuevo = inv.get(valor_texto, self.normalize_estado(book.get("estado")))
        books = self.db.get("books")
        for b in books:
            if b.get("id") == book.get("id"):
                b["estado"] = nuevo
                if nuevo == "leido":
                    if "rating" not in b:
                        b["rating"] = 0
                    if "formato" not in b:
                        b["formato"] = "fisico"
                break
        self.db.set("books", books)
        self.render_books()

    def browse_edit_photo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            self.edit_foto_path = path
            try:
                img = Image.open(path).resize((40, 55), Image.LANCZOS)
                if CTkImage:
                    self.edit_preview_img = CTkImage(light_image=img, dark_image=img, size=(40, 55))
                    self.edit_preview.configure(image=self.edit_preview_img, text="")
            except Exception:
                self.edit_preview_img = None

    def on_edit_estado_change(self):
        if self.e_estado.get() == "leido":
            self.e_stars.pack(anchor="w")
            self.edit_row_fmt.pack(anchor="w")
        else:
            self.e_stars.pack_forget()
            self.edit_row_fmt.pack_forget()

    def close_edit_panel(self):
        self.edit_panel.pack_forget()
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
        self.render_books()

    def save_edit_book(self):
        if not self.edit_book_id:
            return
        try:
            paginas = int(self.e_pags.get().strip()) if self.e_pags.get().strip() else 0
        except ValueError:
            paginas = 0

        estado_val = self.e_estado.get()
        books = self.db.get("books")
        for b in books:
            if b.get("id") == self.edit_book_id:
                b["titulo"] = self.e_titulo.get().strip()
                b["autor"] = self.e_autor.get().strip()
                b["paginas"] = paginas
                b["genero"] = self.e_genero.get().strip()
                b["ubicacion"] = self.e_ubi.get().strip()
                b["foto"] = self.edit_foto_path or None
                b["estado"] = estado_val
                b["rating"] = self.e_stars.rating if estado_val == "leido" else 0
                b["formato"] = self.e_fmt.get() if estado_val == "leido" else "fisico"
                break
        self.db.set("books", books)
        self._cover_cache.clear()
        self.close_edit_panel()

    def edit_book(self, book):
        self.edit_book_id = book.get("id")

        # Rellenar campos
        self.e_titulo.delete(0, "end")
        self.e_titulo.insert(0, book.get("titulo", ""))
        self.e_autor.delete(0, "end")
        self.e_autor.insert(0, book.get("autor", ""))
        self.e_pags.delete(0, "end")
        self.e_pags.insert(0, str(book.get("paginas", "")))
        self.e_genero.delete(0, "end")
        self.e_genero.insert(0, book.get("genero", ""))
        self.e_ubi.delete(0, "end")
        self.e_ubi.insert(0, book.get("ubicacion", ""))

        # Foto
        self.edit_foto_path = book.get("foto") or None
        self.edit_preview_img = None
        self.edit_preview.configure(image=None, text="")
        current_foto = book.get("foto")
        if current_foto and os.path.exists(current_foto):
            try:
                img = Image.open(current_foto).resize((40, 55), Image.LANCZOS)
                if CTkImage:
                    self.edit_preview_img = CTkImage(light_image=img, dark_image=img, size=(40, 55))
                    self.edit_preview.configure(image=self.edit_preview_img, text="")
            except Exception:
                pass

        # Estado
        estado = self.normalize_estado(book.get("estado", "no_leido"))
        self.e_estado.set(estado)
        if estado == "leido":
            self.e_stars.pack(anchor="w")
            self.edit_row_fmt.pack(anchor="w")
        else:
            self.e_stars.pack_forget()
            self.edit_row_fmt.pack_forget()

        # Calificación y formato
        self.e_stars.set_rating(book.get("rating", 0))
        self.e_fmt.set(book.get("formato", "fisico"))

        # Mostrar panel
        self.scroll.pack_forget()
        self.add_panel.pack_forget()
        self.btn_toggle_add.configure(text="+ Añadir Libro")
        self.add_panel_visible = False
        self.edit_panel.pack(fill="both", padx=20, pady=10, expand=True)

    def edit_leido(self, book):
        self.edit_book(book)

    def delete_book(self, book):
        if not messagebox.askyesno("Confirmar", f'¿Eliminar "{book.get("titulo")}"?'):
            return
        books = [b for b in self.db.get("books") if b.get("id") != book.get("id")]
        self.db.set("books", books)
        shelf = [s for s in self.db.get("bookshelf") if s.get("book_id") != book.get("id")]
        self.db.set("bookshelf", shelf)
        self._cover_cache.clear()
        self.render_books()

    def refresh(self):
        self.close_add_panel()
        self.close_edit_panel()
        self._cover_cache.clear()
        self.render_books()