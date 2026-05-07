"""Estantería visual con lomos personalizables."""
from tkinter import Canvas, colorchooser, messagebox

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu, CTkEntry, CTkScrollableFrame

from database import Database


SHELF_Y = [120, 260, 400, 540]
LOMO_H = 110
COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6",
          "#1abc9c", "#e67e22", "#34495e", "#d35400", "#8e44ad"]


class BookshelfFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="🪴 The Bookshelf", font=("Helvetica", 28, "bold")).pack(pady=(15, 5))

        # Panel superior de controles
        ctrl = CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=5)

        # Libro a colocar
        CTkLabel(ctrl, text="Libro:").pack(side="left", padx=5)
        self.book_var = ctk.StringVar()
        self.book_menu = CTkOptionMenu(ctrl, variable=self.book_var, width=200, values=self._book_titles())
        self.book_menu.pack(side="left", padx=5)

        # Color
        CTkLabel(ctrl, text="Color:").pack(side="left", padx=(15, 5))
        self.color_var = ctk.StringVar(value=COLORS[0])
        self.color_preview = CTkFrame(ctrl, width=25, height=25, fg_color=COLORS[0], corner_radius=4)
        self.color_preview.pack(side="left", padx=5)
        self.color_preview.bind("<Button-1>", self.pick_color)

        # Paleta rápida
        for c in COLORS[:5]:
            btn = CTkFrame(ctrl, width=20, height=20, fg_color=c, corner_radius=3)
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, col=c: self.set_color(col))

        CTkButton(ctrl, text="↻ Refrescar libros", command=self.refresh_books, width=120).pack(side="left", padx=15)
        CTkButton(ctrl, text="🗑 Limpiar estantería", command=self.clear_shelf, fg_color="red", hover_color="darkred", width=140).pack(side="left", padx=5)

        self.status_label = CTkLabel(self, text="Haz click en la estantería para colocar el lomo seleccionado.", font=("Arial", 11))
        self.status_label.pack(pady=2)

        # Canvas
        self.canvas = Canvas(self, width=950, height=620, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_shelf()

    def _book_titles(self):
        books = self.db.get("books")
        if not books:
            return ["Sin libros"]
        return [b.get("titulo", "Sin título") for b in books]

    def refresh_books(self):
        titles = self._book_titles()
        self.book_menu.configure(values=titles)
        if titles:
            self.book_var.set(titles[0])

    def set_color(self, c):
        self.color_var.set(c)
        self.color_preview.configure(fg_color=c)

    def pick_color(self, event=None):
        c = colorchooser.askcolor(color=self.color_var.get(), title="Elige color del lomo")[1]
        if c:
            self.set_color(c)

    def clear_shelf(self):
        if messagebox.askyesno("Confirmar", "¿Eliminar todos los lomos de la estantería?"):
            self.db.set("bookshelf", [])
            self.draw_shelf()

    def draw_shelf(self):
        self.canvas.delete("all")

        # Estantes
        for y in SHELF_Y:
            self.canvas.create_rectangle(40, y, 910, y + 8, fill="#5c3a21", outline="")
            self.canvas.create_rectangle(40, y + 8, 910, y + 10, fill="#3e2716", outline="")

        # Lomos guardados
        for item in self.db.get("bookshelf"):
            self._draw_spine(item)

        # Plantas decorativas
        for px, py in [(55, 105), (880, 385), (120, 525)]:
            self.canvas.create_oval(px - 12, py - 25, px + 12, py, fill="#2ecc71", outline="")
            self.canvas.create_oval(px - 8, py - 38, px + 8, py - 12, fill="#27ae60", outline="")

    def _draw_spine(self, item):
        x = item["x"]
        y_base = item["y"]
        color = item.get("color", "#3498db")
        title = item.get("title", "")
        width = item.get("width", 60)

        # Ajustar a estante más cercano
        shelf_y = min(SHELF_Y, key=lambda s: abs(s - y_base))
        y_top = shelf_y - LOMO_H

        # Sombra
        self.canvas.create_rectangle(x + 3, y_top + 3, x + width + 3, shelf_y + 3,
                                     fill="#000000", outline="", stipple="gray50")
        # Lomo
        self.canvas.create_rectangle(x, y_top, x + width, shelf_y,
                                     fill=color, outline="#111", width=2)
        # Texto rotado 90°
        self.canvas.create_text(x + width / 2, (y_top + shelf_y) / 2,
                                text=title, fill="white", font=("Arial", 9),
                                angle=90, anchor="center")
        # Brillo superior
        self.canvas.create_line(x + 4, y_top + 4, x + width - 4, y_top + 4,
                                fill="#ffffff", width=1, stipple="gray50")

        # Tag para identificar
        tag = f"spine_{item.get('id', '')}"
        self.canvas.addtag_withtag(tag, "all")

    def on_canvas_click(self, event):
        title = self.book_var.get()
        if title == "Sin libros":
            return

        # Buscar libro en DB para obtener título exacto y ancho
        books = self.db.get("books")
        book = next((b for b in books if b.get("titulo") == title), None)
        if not book:
            return

        # Calcular ancho proporcional al título (aprox 7px por carácter + padding)
        width = max(40, min(160, len(book["titulo"]) * 7 + 14))

        # Ajustar Y al estante más cercano
        shelf_y = min(SHELF_Y, key=lambda s: abs(s - event.y))

        # Ajustar X para que no se salga
        x = max(45, min(event.x, 910 - width))

        new_item = {
            "id": Database.generate_id(),
            "book_id": book.get("id"),
            "title": book["titulo"],
            "x": x,
            "y": shelf_y,
            "color": self.color_var.get(),
            "width": width
        }

        shelf = self.db.get("bookshelf")
        shelf.append(new_item)
        self.db.set("bookshelf", shelf)
        self.draw_shelf()
