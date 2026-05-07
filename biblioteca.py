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
        self.add_panel_visible = False

        # Header
        hdr = CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(15, 5), padx=20)
        CTkLabel(hdr, text="📖 BIBLIOTECA", font=("Helvetica", 28, "bold")).pack(side="left")

        # Filtros
        filtros = CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=20, pady=5)
        for key, text in self.FILTROS.items():
            CTkButton(filtros, text=text, width=100,
                      command=lambda k=key: self.set_filtro(k)).pack(side="left", padx=5)

        self.btn_toggle_add = CTkButton(filtros, text="+ Añadir Libro", command=self.toggle_add_panel)
        self.btn_toggle_add.pack(side="right", padx=5)

        # --- PANEL EMBEBIDO AÑADIR LIBRO ---
        self.add_panel = CTkFrame(self, fg_color="#252525", corner_radius=12, border_width=2)

        CTkLabel(self.add_panel, text="NUEVO LIBRO", font=("Helvetica", 18, "bold")).pack(pady=(15, 10))

        # Grid de campos
        grid = CTkFrame(self.add_panel, fg_color="transparent")
        grid.pack(padx=20, pady=5)

        fields = [
            ("Título *", "titulo"), ("Autor", "autor"),
            ("N° Páginas", "paginas"), ("Género", "genero"),
            ("Ubicación", "ubicacion")
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 2)
            CTkLabel(grid, text=label + ":", font=("Arial", 11, "bold")).grid(row=r*2, column=c, padx=10, pady=(8, 2), sticky="w")
            e = CTkEntry(grid, width=300)
            e.grid(row=r*2+1, column=c, padx=10, pady=(0, 5))
            self.entries[key] = e

        # Foto
        row_foto = len(fields) // 2 * 2 + 1
        CTkLabel(grid, text="Foto de portada:", font=("Arial", 11, "bold")).grid(row=row_foto, column=0, padx=10, pady=(10, 2), sticky="w")
        foto_row = CTkFrame(grid, fg_color="transparent")
        foto_row.grid(row=row_foto+1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.entry_foto = CTkEntry(foto_row, width=400, placeholder_text="Ruta de la imagen...")
        self.entry_foto.pack(side="left", padx=5)
        CTkButton(foto_row, text="📁 Examinar", width=100, command=self.browse_photo).pack(side="left", padx=5)
        self.photo_preview = CTkLabel(foto_row, text="", width=40, height=40)
        self.photo_preview.pack(side="left", padx=10)

        # Estado
        estado_frame = CTkFrame(self.add_panel, fg_color="transparent")
        estado_frame.pack(fill="x", padx=30, pady=(10, 5))
        CTkLabel(estado_frame, text="Estado:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.estado_var = ctk.StringVar(value="")
        self.estado_radios = []
        for val, txt in [("no_leido", "No leído"), ("leyendo", "Leyendo"), ("leido", "Leído")]:
            rb = CTkRadioButton(estado_frame, text=txt, variable=self.estado_var, value=val,
                                command=self.on_estado_change)
            rb.pack(side="left", padx=12)
            self.estado_radios.append(rb)

        # Extras para "leído"
        self.extras_frame = CTkFrame(self.add_panel, fg_color="transparent")
        self.extras_frame.pack(fill="x", padx=30, pady=5)
        self.extras_frame.pack_forget()

        CTkLabel(self.extras_frame, text="Calificación:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.add_stars = StarRating(self.extras_frame, rating=0, size=26)
        self.add_stars.pack(side="left", padx=10)

        CTkLabel(self.extras_frame, text="Formato:", font=("Arial", 12, "bold")).pack(side="left", padx=(20, 5))
        self.fmt_var = ctk.StringVar(value="fisico")
        for val, txt in [("fisico", "Físico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(self.extras_frame, text=txt, variable=self.fmt_var, value=val).pack(side="left", padx=8)

        # Botón guardar
        CTkButton(self.add_panel, text="💾 Guardar Libro", command=self.save_book, height=38,
                  font=("Arial", 14, "bold")).pack(pady=20)

        # Grid scrollable
        self.scroll = CTkScrollableFrame(self, width=900, height=500, fg_color="transparent")
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render_books()

    def toggle_add_panel(self):
        if self.add_panel_visible:
            self.add_panel.pack_forget()
            self.btn_toggle_add.configure(text="+ Añadir Libro")
            self.add_panel_visible = False
        else:
            self.scroll.pack_forget()
            self.add_panel.pack(fill="x", padx=20, pady=10)
            self.scroll.pack(padx=20, pady=10, fill="both", expand=True)
            self.btn_toggle_add.configure(text="✕ Cerrar panel")
            self.add_panel_visible = True

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
            self.entry_foto.delete(0, "end")
            self.entry_foto.insert(0, path)
            try:
                img = Image.open(path).resize((40, 55), Image.LANCZOS)
                if CTkImage:
                    self.photo_preview.configure(image=CTkImage(light_image=img, dark_image=img, size=(40, 55)), text="")
            except Exception:
                pass

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

        foto_path = self.entry_foto.get().strip() or None

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
        self.entry_foto.delete(0, "end")
        self.estado_var.set("")
        self.extras_frame.pack_forget()
        self.add_stars.set_rating(0)
        self.fmt_var.set("fisico")
        self.photo_preview.configure(image="", text="")

        self.toggle_add_panel()
        self.render_books()

    def set_filtro(self, key):
        self.filtro_actual = key
        self.render_books()

    def render_books(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        books = self.db.get("books")
        if self.filtro_actual == "tbr":
            books = [b for b in books if self.normalize_estado(b.get("estado")) == "no_leido"]
        elif self.filtro_actual == "leidos":
            books = [b for b in books if self.normalize_estado(b.get("estado")) == "leido"]

        if not books:
            msg = "No hay libros en esta vista."
            if self.filtro_actual == "tbr":
                msg = "Tu TBR está vacío 📭"
            elif self.filtro_actual == "leidos":
                msg = "Aún no has marcado ningún libro como leído."
            CTkLabel(self.scroll, text=msg, font=("Arial", 16)).pack(pady=50)
            return

        row, col = 0, 0
        for book in books:
            card = self.create_book_card(self.scroll, book)
            card.grid(row=row, column=col, padx=15, pady=15)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def _load_cover(self, path, size=(140, 200)):
        if not path or not os.path.exists(path):
            return None
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            if CTkImage:
                return CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            pass
        return None

    def create_book_card(self, parent, book):
        card = CTkFrame(parent, width=200, height=380, corner_radius=12, border_width=2)
        card.grid_propagate(False)

        cover = CTkFrame(card, width=140, height=200, corner_radius=8, fg_color="#2b2b2b")
        cover.place(relx=0.5, y=15, anchor="n")

        img = self._load_cover(book.get("foto"))
        if img:
            CTkLabel(cover, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
        else:
            CTkLabel(cover, text="📕", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")

        y_off = 230
        CTkLabel(card, text=book.get("titulo", "Sin título")[:22], font=("Arial", 12, "bold")).place(relx=0.5, y=y_off, anchor="center")
        CTkLabel(card, text=book.get("autor", "")[:20], font=("Arial", 10)).place(relx=0.5, y=y_off+22, anchor="center")
        CTkLabel(card, text=f"{book.get('paginas', '?')} pág. | {book.get('genero', '')[:15]}", font=("Arial", 9)).place(relx=0.5, y=y_off+42, anchor="center")
        CTkLabel(card, text=f"📍 {book.get('ubicacion', '')[:18]}", font=("Arial", 9)).place(relx=0.5, y=y_off+58, anchor="center")

        estado = self.normalize_estado(book.get("estado", "no_leido"))
        menu = CTkOptionMenu(card, values=list(self.ESTADOS.values()),
                             command=lambda v, b=book: self.cambiar_estado(b, v),
                             width=160)
        menu.set(self.ESTADOS[estado])
        menu.place(relx=0.5, y=y_off+85, anchor="center")

        if estado == "leido":
            stars = StarRating(card, rating=book.get("rating", 0), size=14)
            stars.place(relx=0.5, y=y_off+115, anchor="center")
            fmt = book.get("formato", "fisico")
            fmt_text = {"fisico": "📖 Físico", "digital": "💻 Digital", "audiolibro": "🎧 Audio"}
            CTkLabel(card, text=fmt_text.get(fmt, ""), font=("Arial", 9)).place(relx=0.5, y=y_off+138, anchor="center")
            CTkButton(card, text="✏️ Editar", width=60, height=20, font=("Arial", 9),
                      command=lambda b=book: self.edit_leido(b)).place(relx=0.5, y=y_off+160, anchor="center")

        CTkButton(card, text="🗑", width=30, height=20, fg_color="red", hover_color="darkred",
                  command=lambda b=book: self.delete_book(b)).place(relx=0.85, y=15, anchor="n")

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

    def edit_leido(self, book):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Editar libro leído")
        dlg.geometry("350x250")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        CTkLabel(dlg, text="Puntuación:").pack(pady=(15, 5))
        stars = StarRating(dlg, rating=book.get("rating", 0))
        stars.pack()

        CTkLabel(dlg, text="Formato:").pack(pady=(15, 5))
        fmt_var = ctk.StringVar(value=book.get("formato", "fisico"))
        row = CTkFrame(dlg, fg_color="transparent")
        row.pack()
        for val, txt in [("fisico", "Físico"), ("digital", "Digital"), ("audiolibro", "Audiolibro")]:
            CTkRadioButton(row, text=txt, variable=fmt_var, value=val).pack(side="left", padx=8)

        def guardar():
            books = self.db.get("books")
            for b in books:
                if b.get("id") == book.get("id"):
                    b["rating"] = stars.rating
                    b["formato"] = fmt_var.get()
                    break
            self.db.set("books", books)
            dlg.destroy()
            self.render_books()

        CTkButton(dlg, text="Guardar", command=guardar).pack(pady=20)

    def delete_book(self, book):
        if not messagebox.askyesno("Confirmar", f'¿Eliminar "{book.get("titulo")}"?'):
            return
        books = [b for b in self.db.get("books") if b.get("id") != book.get("id")]
        self.db.set("books", books)
        shelf = [s for s in self.db.get("bookshelf") if s.get("book_id") != book.get("id")]
        self.db.set("bookshelf", shelf)
        self.render_books()