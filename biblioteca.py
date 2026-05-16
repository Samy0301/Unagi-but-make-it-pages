"""Biblioteca con grid de libros, estados y filtros TBR/Leidos."""
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

from database import Database, PALETA
from widgets import StarRating


class BibliotecaFrame(CTkFrame):
    ESTADOS = {
        "no_leido": "No lo he leido",
        "leyendo": "Lo estoy leyendo",
        "leido": "Ya lo lei"
    }
    FILTROS = {"todos": "Todos", "tbr": "TBR", "leidos": "Leidos"}
    ORDEN = {"titulo": "Titulo A-Z", "rating": "Mejor valorados"}

    ESTADO_MAP = {
        "por leer": "no_leido",
        "no leido": "no_leido",
        "no_leido": "no_leido",
        "leyendo": "leyendo",
        "leido": "leido",
        "leido": "leido",
        "ya lo lei": "leido",
    }

    COLS = 5
    CARD_WIDTH = 180
    CARD_PADX = 10

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

        # Pool simple
        self._card_pool = []
        self._visible_cards = []

        # Header
        hdr = CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 5), padx=20)
        CTkLabel(hdr, text="BIBLIOTECA", font=("Helvetica", 28, "bold"),
                 text_color=PALETA["text_main"]).pack(side="left")

        # Barra de herramientas
        tools = CTkFrame(self, fg_color="transparent")
        tools.pack(fill="x", padx=20, pady=5)

        for key, text in self.FILTROS.items():
            CTkButton(tools, text=text, width=100,
                      fg_color=PALETA["ocean"],
                      hover_color=PALETA["coral"],
                      text_color=PALETA["text_main"],
                      command=lambda k=key: self.set_filtro(k)).pack(side="left", padx=5)

        CTkLabel(tools, text="Buscar:", font=("Arial", 14),
                 text_color=PALETA["text_secondary"]).pack(side="left", padx=(20, 2))
        self.search_entry = CTkEntry(tools, width=200, placeholder_text="Buscar titulo o autor...",
                                     fg_color=PALETA["bg_input"],
                                     text_color=PALETA["text_main"],
                                     border_color=PALETA["border"])
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.render_books())
        CTkButton(tools, text="X", width=30,
                  fg_color=PALETA["coral"],
                  hover_color=PALETA["coral_light"],
                  text_color=PALETA["bg_main"],
                  command=self.clear_search).pack(side="left", padx=2)

        CTkLabel(tools, text="Orden:", font=("Arial", 11),
                 text_color=PALETA["text_secondary"]).pack(side="left", padx=(20, 5))
        self.orden_menu = CTkOptionMenu(tools, values=list(self.ORDEN.values()), width=160,
                                        fg_color=PALETA["bg_input"],
                                        button_color=PALETA["ocean"],
                                        button_hover_color=PALETA["coral"],
                                        text_color=PALETA["text_main"],
                                        dropdown_fg_color=PALETA["bg_card"],
                                        dropdown_text_color=PALETA["text_main"],
                                        dropdown_hover_color=PALETA["coral"],
                                        command=self.set_orden)
        self.orden_menu.set(self.ORDEN["titulo"])
        self.orden_menu.pack(side="left", padx=5)

        self.btn_toggle_add = CTkButton(tools, text="+ Anadir Libro",
                                        fg_color=PALETA["coral"],
                                        hover_color=PALETA["coral_light"],
                                        text_color=PALETA["bg_main"],
                                        command=self.toggle_add_panel)
        self.btn_toggle_add.pack(side="right", padx=5)

        # --- PANEL EMBEBIDO ANADIR LIBRO ---
        self.add_panel = CTkFrame(self, fg_color=PALETA["bg_card"], corner_radius=16,
                                  border_width=2, border_color=PALETA["border_accent"])

        CTkLabel(self.add_panel, text="NUEVO LIBRO", font=("Helvetica", 22, "bold"),
                 text_color=PALETA["text_main"]).pack(pady=(20, 15))

        self.add_container = CTkFrame(self.add_panel, fg_color="transparent")
        self.add_container.pack(expand=True, fill="both")

        self.add_scroll = ctk.CTkScrollableFrame(self.add_container, width=700, height=420,
                                               fg_color="transparent")
        self.add_scroll.pack(padx=30, pady=5, fill="both", expand=True)

        self.entries = {}

        def add_row(label_text, widget_factory):
            row = CTkFrame(self.add_scroll, fg_color="transparent")
            row.pack(fill="x", pady=(6, 2))
            inner = CTkFrame(row, fg_color="transparent")
            inner.pack(expand=True)
            CTkLabel(inner, text=label_text, font=("Arial", 12, "bold"),
                     text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
            w = widget_factory(inner)
            w.pack()
            return w

        self.entries["titulo"] = add_row("Titulo *", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.entries["autor"] = add_row("Autor", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.entries["paginas"] = add_row("N Paginas", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.entries["genero"] = add_row("Genero", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.entries["ubicacion"] = add_row("Ubicacion", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))

        # Portada
        row_foto = CTkFrame(self.add_scroll, fg_color="transparent")
        row_foto.pack(fill="x", pady=(6, 2))
        inner_foto = CTkFrame(row_foto, fg_color="transparent")
        inner_foto.pack(expand=True)
        CTkLabel(inner_foto, text="Portada", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.add_foto_row = CTkFrame(inner_foto, fg_color="transparent")
        self.add_foto_row.pack(anchor="w")
        CTkButton(self.add_foto_row, text="Examinar", width=120, height=32, corner_radius=8,
                  fg_color=PALETA["coral"],
                  hover_color=PALETA["coral_light"],
                  text_color=PALETA["bg_main"],
                  command=self.browse_photo).pack(side="left", padx=(0, 12))
        self.photo_preview = CTkLabel(self.add_foto_row, text="", width=40, height=55,
                                      fg_color=PALETA["bg_input"])
        self.photo_preview.pack(side="left")

        # Estado
        row_est = CTkFrame(self.add_scroll, fg_color="transparent")
        row_est.pack(fill="x", pady=(6, 2))
        inner_est = CTkFrame(row_est, fg_color="transparent")
        inner_est.pack(expand=True)
        CTkLabel(inner_est, text="Estado", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.estado_var = ctk.StringVar(value="")
        self.add_row_est = CTkFrame(inner_est, fg_color="transparent")
        self.add_row_est.pack(anchor="w")
        for val, txt in [("no_leido", "No leido"), ("leyendo", "Leyendo"), ("leido", "Leido")]:
            CTkRadioButton(self.add_row_est, text=txt, variable=self.estado_var, value=val,
                           fg_color=PALETA["coral"],
                           border_color=PALETA["border_accent"],
                           text_color=PALETA["text_secondary"],
                           command=self.on_estado_change).pack(side="left", padx=10)

        # Extras para "leido"
        self.extras_frame = CTkFrame(self.add_scroll, fg_color="transparent")
        self.extras_frame.pack(fill="x", padx=30, pady=(6, 0))
        self.extras_frame.pack_forget()

        row_extras = CTkFrame(self.extras_frame, fg_color="transparent")
        row_extras.pack(fill="x")
        inner_extras = CTkFrame(row_extras, fg_color="transparent")
        inner_extras.pack(expand=True)

        CTkLabel(inner_extras, text="Calificacion", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.add_stars = StarRating(inner_extras, rating=0, size=26)
        self.add_stars.pack(anchor="w")

        CTkLabel(inner_extras, text="Formato", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(8, 2))
        self.fmt_var = ctk.StringVar(value="fisico")
        self.add_row_fmt = CTkFrame(inner_extras, fg_color="transparent")
        self.add_row_fmt.pack(anchor="w")
        for val, txt in [("fisico", "Fisico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(self.add_row_fmt, text=txt, variable=self.fmt_var, value=val,
                           fg_color=PALETA["coral"],
                           border_color=PALETA["border_accent"],
                           text_color=PALETA["text_secondary"]).pack(side="left", padx=10)

        btn_add_row = CTkFrame(self.add_container, fg_color="transparent")
        btn_add_row.pack(pady=(15, 20))
        CTkButton(btn_add_row, text="Guardar Libro", command=self.save_book,
                  height=38, font=("Arial", 14, "bold"), corner_radius=10,
                  fg_color=PALETA["coral"],
                  hover_color=PALETA["coral_light"],
                  text_color=PALETA["bg_main"]).pack(side="left", padx=8)
        CTkButton(btn_add_row, text="Cancelar", command=self.close_add_panel,
                  height=38, font=("Arial", 14), corner_radius=10,
                  fg_color=PALETA["ocean"],
                  hover_color=PALETA["coral"],
                  text_color=PALETA["text_main"]).pack(side="left", padx=8)

        # --- PANEL EMBEBIDO EDITAR LIBRO ---
        self.edit_panel = CTkFrame(self, fg_color=PALETA["bg_card"], corner_radius=16,
                                   border_width=2, border_color=PALETA["border_accent"])
        self.edit_book_id = None

        CTkLabel(self.edit_panel, text="EDITAR LIBRO", font=("Helvetica", 22, "bold"),
                 text_color=PALETA["text_main"]).pack(pady=(20, 15))

        self.edit_container = CTkFrame(self.edit_panel, fg_color="transparent")
        self.edit_container.pack(expand=True, fill="both")

        self.edit_scroll = ctk.CTkScrollableFrame(self.edit_container, width=700, height=420,
                                                fg_color="transparent")
        self.edit_scroll.pack(padx=30, pady=5, fill="both", expand=True)

        def edit_row(label_text, widget_factory):
            row = CTkFrame(self.edit_scroll, fg_color="transparent")
            row.pack(fill="x", pady=(6, 2))
            inner = CTkFrame(row, fg_color="transparent")
            inner.pack(expand=True)
            CTkLabel(inner, text=label_text, font=("Arial", 12, "bold"),
                     text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
            w = widget_factory(inner)
            w.pack()
            return w

        self.e_titulo = edit_row("Titulo", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.e_autor = edit_row("Autor", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.e_pags = edit_row("Paginas", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.e_genero = edit_row("Genero", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))
        self.e_ubi = edit_row("Ubicacion", 
            lambda p: CTkEntry(p, width=600, height=32, corner_radius=8,
                              fg_color=PALETA["bg_input"],
                              text_color=PALETA["text_main"],
                              border_color=PALETA["border"]))

        # Portada
        row_foto = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_foto.pack(fill="x", pady=(6, 2))
        inner_foto = CTkFrame(row_foto, fg_color="transparent")
        inner_foto.pack(expand=True)
        CTkLabel(inner_foto, text="Portada", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.edit_foto_row = CTkFrame(inner_foto, fg_color="transparent")
        self.edit_foto_row.pack(anchor="w")

        self.edit_foto_path = None
        self.edit_preview_img = None

        CTkButton(self.edit_foto_row, text="Examinar", width=120, height=32, corner_radius=8,
                  fg_color=PALETA["coral"],
                  hover_color=PALETA["coral_light"],
                  text_color=PALETA["bg_main"],
                  command=self.browse_edit_photo).pack(side="left", padx=(0, 12))
        self.edit_preview = CTkLabel(self.edit_foto_row, text="", width=40, height=55,
                                     fg_color=PALETA["bg_input"])
        self.edit_preview.pack(side="left")

        # Estado
        row_est = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_est.pack(fill="x", pady=(6, 2))
        inner_est = CTkFrame(row_est, fg_color="transparent")
        inner_est.pack(expand=True)
        CTkLabel(inner_est, text="Estado", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.e_estado = ctk.StringVar(value="no_leido")
        self.edit_row_est = CTkFrame(inner_est, fg_color="transparent")
        self.edit_row_est.pack(anchor="w")
        for val, txt in [("no_leido", "No leido"), ("leyendo", "Leyendo"), ("leido", "Leido")]:
            CTkRadioButton(self.edit_row_est, text=txt, variable=self.e_estado,
                           value=val, command=self.on_edit_estado_change,
                           fg_color=PALETA["coral"],
                           border_color=PALETA["border_accent"],
                           text_color=PALETA["text_secondary"]).pack(side="left", padx=10)

        # Calificacion y Formato
        row_stars = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_stars.pack(fill="x", pady=(6, 2))
        inner_stars = CTkFrame(row_stars, fg_color="transparent")
        inner_stars.pack(expand=True)
        CTkLabel(inner_stars, text="Calificacion", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.e_stars = StarRating(inner_stars, rating=0, size=26)
        self.e_stars.pack(anchor="w")

        row_fmt = CTkFrame(self.edit_scroll, fg_color="transparent")
        row_fmt.pack(fill="x", pady=(6, 2))
        inner_fmt = CTkFrame(row_fmt, fg_color="transparent")
        inner_fmt.pack(expand=True)
        CTkLabel(inner_fmt, text="Formato", font=("Arial", 12, "bold"),
                 text_color=PALETA["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.e_fmt = ctk.StringVar(value="fisico")
        self.edit_row_fmt = CTkFrame(inner_fmt, fg_color="transparent")
        self.edit_row_fmt.pack(anchor="w")
        for val, txt in [("fisico", "Fisico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(self.edit_row_fmt, text=txt, variable=self.e_fmt,
                           value=val,
                           fg_color=PALETA["coral"],
                           border_color=PALETA["border_accent"],
                           text_color=PALETA["text_secondary"]).pack(side="left", padx=10)

        btn_edit_row = CTkFrame(self.edit_container, fg_color="transparent")
        btn_edit_row.pack(pady=(15, 20))
        CTkButton(btn_edit_row, text="Guardar cambios", command=self.save_edit_book,
                  height=38, font=("Arial", 14, "bold"), corner_radius=10,
                  fg_color=PALETA["coral"],
                  hover_color=PALETA["coral_light"],
                  text_color=PALETA["bg_main"]).pack(side="left", padx=8)
        CTkButton(btn_edit_row, text="Cancelar", command=self.close_edit_panel,
                  height=38, font=("Arial", 14), corner_radius=10,
                  fg_color=PALETA["ocean"],
                  hover_color=PALETA["coral"],
                  text_color=PALETA["text_main"]).pack(side="left", padx=8)

        # --- SCROLL DE TARJETAS ---
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
            self.btn_toggle_add.configure(text="Cerrar panel",
                                          fg_color=PALETA["coral_dark"],
                                          hover_color=PALETA["coral"])
            self.add_panel_visible = True

    def close_add_panel(self):
        self.add_panel.pack_forget()
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
        self.btn_toggle_add.configure(text="+ Anadir Libro",
                                      fg_color=PALETA["coral"],
                                      hover_color=PALETA["coral_light"])
        self.add_panel_visible = False

    def on_estado_change(self):
        if self.estado_var.get() == "leido":
            self.extras_frame.pack(fill="x", padx=30, pady=5)
        else:
            self.extras_frame.pack_forget()

    def browse_photo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
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
            messagebox.showwarning("Campo requerido", "El titulo es obligatorio.")
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

        self.toggle_add_panel()
        self.render_books()

    def set_filtro(self, key):
        self.filtro_actual = key
        self.render_books()

    def set_orden(self, valor_texto):
        inv = {v: k for k, v in self.ORDEN.items()}
        self.orden_actual = inv.get(valor_texto, "titulo")
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
        books = self._filtrar_y_ordenar(self.db.get("books"))

        for card in self._visible_cards:
            card.grid_remove()
        self._visible_cards.clear()

        for w in list(self.scroll.winfo_children()):
            if getattr(w, "_is_empty_msg", False):
                w.destroy()

        if not books:
            msg = "No hay libros en esta vista."
            if self.filtro_actual == "tbr":
                msg = "Tu TBR esta vacio"
            elif self.filtro_actual == "leidos":
                msg = "Aun no has marcado ningun libro como leido."
            lbl = CTkLabel(self.scroll, text=msg, font=("Arial", 16),
                          text_color=PALETA["text_muted"])
            lbl._is_empty_msg = True
            lbl.pack(pady=50, fill="x")
            lbl.configure(anchor="center")
            return

        cols = self.COLS
        total = len(books)

        canvas = getattr(self.scroll, "_parent_canvas", None)
        if canvas:
            canvas.yview_moveto(0)

        for idx in range(total):
            row = idx // cols
            col = idx % cols

            if self._card_pool:
                card = self._card_pool.pop()
            else:
                card = self.create_book_card(self.scroll)

            self._update_book_card(card, books[idx])
            card.grid(row=row, column=col, padx=self.CARD_PADX, pady=15)
            self._visible_cards.append(card)

        max_pool = cols * 3
        while len(self._card_pool) > max_pool:
            c = self._card_pool.pop()
            c.destroy()

        self.update_idletasks()

    def _load_cover(self, path, size=(120, 170)):
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

    def create_book_card(self, parent):
        card = CTkFrame(parent, width=self.CARD_WIDTH, height=360, corner_radius=12,
                        border_width=2, fg_color=PALETA["bg_card"],
                        border_color=PALETA["border"])
        card.grid_propagate(False)

        refs = {}
        card._refs = refs
        card._book_id = None

        # Cover
        cover = CTkFrame(card, width=120, height=150, corner_radius=8,
                         fg_color=PALETA["bg_input"])
        cover.pack(pady=(10, 6))
        cover.pack_propagate(False)
        refs['cover_img'] = CTkLabel(cover, text="")
        refs['cover_img'].place(relx=0.5, rely=0.5, anchor="center")

        # Textos
        refs['title'] = CTkLabel(card, text="", font=("Arial", 13, "bold"),
                                 text_color=PALETA["text_main"], wraplength=160)
        refs['title'].pack(pady=(0, 2))
        refs['author'] = CTkLabel(card, text="", font=("Arial", 10),
                                  text_color=PALETA["text_secondary"], wraplength=160)
        refs['author'].pack(pady=(0, 2))
        refs['meta'] = CTkLabel(card, text="", font=("Arial", 9),
                                text_color=PALETA["text_muted"], wraplength=160)
        refs['meta'].pack(pady=(0, 2))
        refs['location'] = CTkLabel(card, text="", font=("Arial", 9),
                                    text_color=PALETA["text_muted"], wraplength=160)
        refs['location'].pack(pady=(0, 2))

        # Estado frame
        refs['estado_frame'] = CTkFrame(card, fg_color="transparent", height=55)
        refs['estado_frame'].pack(pady=(0, 4))
        refs['estado_frame'].pack_propagate(False)

        # Pre-crear widgets de estado
        refs['estado_menu'] = CTkOptionMenu(refs['estado_frame'], values=list(self.ESTADOS.values()),
                                            width=140,
                                            fg_color=PALETA["bg_input"],
                                            button_color=PALETA["ocean"],
                                            button_hover_color=PALETA["coral"],
                                            text_color=PALETA["text_main"],
                                            dropdown_fg_color=PALETA["bg_card"],
                                            dropdown_text_color=PALETA["text_main"],
                                            dropdown_hover_color=PALETA["coral"])

        refs['estado_done'] = CTkFrame(refs['estado_frame'], fg_color="transparent")
        refs['estado_done_label'] = CTkLabel(refs['estado_done'], text="",
                                              font=("Arial", 9, "bold"),
                                              text_color=PALETA["coral"])
        refs['estado_done_stars'] = StarRating(refs['estado_done'], rating=0, size=14, readonly=True)
        refs['estado_done_fmt'] = CTkLabel(refs['estado_done'], text="", font=("Arial", 9),
                                           text_color=PALETA["text_secondary"])

        # Botones
        btn_row = CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(0, 8))
        refs['btn_edit'] = CTkButton(btn_row, text="Editar", width=28, height=18, font=("Arial", 8),
                                     fg_color=PALETA["ocean"],
                                     hover_color=PALETA["coral"],
                                     text_color=PALETA["text_main"])
        refs['btn_edit'].pack(side="left", padx=2)
        refs['btn_del'] = CTkButton(btn_row, text="Eliminar", width=28, height=18,
                                    fg_color=PALETA["error"],
                                    hover_color=PALETA["coral"],
                                    text_color=PALETA["text_main"])
        refs['btn_del'].pack(side="left", padx=2)

        return card

    def _update_book_card(self, card, book):
        refs = card._refs
        estado = self.normalize_estado(book.get("estado", "no_leido"))
        card._book_id = book.get("id")

        # Portada
        img = self._load_cover(book.get("foto"))
        if img:
            refs['cover_img'].configure(image=img, text="")
        else:
            refs['cover_img'].configure(image=None, text="Libro",
                                        font=("Arial", 40),
                                        text_color=PALETA["text_muted"])

        # Textos
        refs['title'].configure(text=book.get("titulo", "Sin titulo"))
        refs['author'].configure(text=book.get("autor", ""))
        refs['meta'].configure(text=f"{book.get('paginas', '?')} pag. | {book.get('genero', '')}")
        refs['location'].configure(text=f"Loc: {book.get('ubicacion', '')}")

        # Estado
        if estado != "leido":
            refs['estado_done'].place_forget()
            refs['estado_menu'].place(relx=0.5, rely=0.5, anchor="center")
            refs['estado_menu'].set(self.ESTADOS[estado])
            refs['estado_menu'].configure(
                command=lambda v, b=book: self.cambiar_estado(b, v)
            )
        else:
            refs['estado_menu'].place_forget()
            refs['estado_done'].place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
            refs['estado_done_label'].configure(text=self.ESTADOS.get(estado, ""))
            refs['estado_done_label'].place(relx=0.5, y=8, anchor="center")
            refs['estado_done_stars'].set_rating(book.get("rating", 0))
            refs['estado_done_stars'].place(relx=0.5, y=24, anchor="center")
            fmt = book.get("formato", "fisico")
            fmt_text = {"fisico": "Fisico", "digital": "Digital", "audiolibro": "Audio"}
            refs['estado_done_fmt'].configure(text=fmt_text.get(fmt, ""))
            refs['estado_done_fmt'].place(relx=0.5, y=42, anchor="center")

        # Botones
        refs['btn_edit'].configure(command=lambda b=book: self.edit_book(b))
        refs['btn_del'].configure(command=lambda b=book: self.delete_book(b))

    def cambiar_estado(self, book, valor_texto):
        inv = {v: k for k, v in self.ESTADOS.items()}
        nuevo = inv.get(valor_texto, self.normalize_estado(book.get("estado")))
        books = self.db.get("books")
        for b in books:
            if b.get("id") == book.get("id"):
                b["estado"] = nuevo
                if nuevo == "leido":
                    b.setdefault("rating", 0)
                    b.setdefault("formato", "fisico")
                break
        self.db.set("books", books)
        self.render_books()

    def browse_edit_photo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
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

        estado = self.normalize_estado(book.get("estado", "no_leido"))
        self.e_estado.set(estado)
        if estado == "leido":
            self.e_stars.pack(anchor="w")
            self.edit_row_fmt.pack(anchor="w")
        else:
            self.e_stars.pack_forget()
            self.edit_row_fmt.pack_forget()

        self.e_stars.set_rating(book.get("rating", 0))
        self.e_fmt.set(book.get("formato", "fisico"))

        self.scroll.pack_forget()
        self.add_panel.pack_forget()
        self.btn_toggle_add.configure(text="+ Anadir Libro",
                                      fg_color=PALETA["coral"],
                                      hover_color=PALETA["coral_light"])
        self.add_panel_visible = False
        self.edit_panel.pack(fill="both", padx=20, pady=10, expand=True)

    def delete_book(self, book):
        if not messagebox.askyesno("Confirmar", f'Eliminar "{book.get("titulo")}"?'):
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