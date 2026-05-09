"""Estantería visual con lomos personalizables - estilo minimalista."""
from tkinter import Canvas, colorchooser, messagebox

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu

from database import Database


LOMO_H_MIN = 70
LOMO_H_MAX = 130
COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6",
          "#1abc9c", "#e67e22", "#34495e", "#d35400", "#8e44ad",
          "#c0392b", "#2980b9", "#27ae60", "#f39c12", "#8e44ad"]

# Configuración por defecto de estantes
DEFAULT_SHELVES = [140, 300, 460]
SHELF_SPACING = 160  # espacio entre estantes


class BookshelfFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="🪴 The Bookshelf", font=("Helvetica", 28, "bold")).pack(pady=(15, 5))

        # Controles superiores
        ctrl = CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=5)

        CTkLabel(ctrl, text="Libro:").pack(side="left", padx=5)
        self.book_var = ctk.StringVar()
        self.book_menu = CTkOptionMenu(ctrl, variable=self.book_var, width=200, values=self._book_titles())
        self.book_menu.pack(side="left", padx=5)

        CTkLabel(ctrl, text="Color:").pack(side="left", padx=(15, 5))
        self.color_var = ctk.StringVar(value=COLORS[0])
        self.color_preview = CTkFrame(ctrl, width=25, height=25, fg_color=COLORS[0], corner_radius=4)
        self.color_preview.pack(side="left", padx=5)
        self.color_preview.bind("<Button-1>", self.pick_color)

        for c in COLORS[:5]:
            btn = CTkFrame(ctrl, width=20, height=20, fg_color=c, corner_radius=3)
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, col=c: self.set_color(col))

        CTkButton(ctrl, text="↻ Refrescar", command=self.refresh_books, width=100).pack(side="left", padx=10)
        CTkButton(ctrl, text="🗑 Limpiar", command=self.clear_shelf, fg_color="red", hover_color="darkred", width=100).pack(side="left", padx=5)

        # Controles de estantes
        shelf_ctrl = CTkFrame(self, fg_color="transparent")
        shelf_ctrl.pack(fill="x", padx=20, pady=(0, 5))
        CTkButton(shelf_ctrl, text="➕ Añadir estante", command=self.add_shelf,
                  width=130, corner_radius=8).pack(side="left", padx=5)
        CTkButton(shelf_ctrl, text="➖ Quitar estante", command=self.remove_shelf,
                  width=130, corner_radius=8, fg_color="#555", hover_color="#666").pack(side="left", padx=5)
        self.shelf_count_label = CTkLabel(shelf_ctrl, text=f"Estantes: {len(self.get_shelves())}", font=("Arial", 11))
        self.shelf_count_label.pack(side="left", padx=15)

        self.status_label = CTkLabel(self, text="Click en la estantería para colocar el lomo. Click derecho en un lomo para eliminarlo.", font=("Arial", 11))
        self.status_label.pack(pady=2)

        # Canvas scrollable para estantes
        self.canvas_frame = CTkFrame(self, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = Canvas(self.canvas_frame, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

        # Scrollbar vertical
        self.vscroll = ctk.CTkScrollbar(self.canvas_frame, command=self.canvas.yview)
        self.vscroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        # --- SCROLL CON RUEDA / TOUCHPAD ---
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)      # Windows / macOS
        self.canvas.bind("<Button-4>", self._on_mousewheel)        # Linux scroll arriba
        self.canvas.bind("<Button-5>", self._on_mousewheel)        # Linux scroll abajo

        # Grid invisible para control de solapamiento
        self.shelf_grid = {}

        # Centrado automático al cambiar tamaño
        self._last_canvas_width = 0
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.draw_shelf()

    def _on_mousewheel(self, event):
        """Maneja scroll con rueda del ratón y touchpad."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(3, "units")

    def _on_canvas_configure(self, event=None):
        """Redibuja la estantería cuando el canvas cambia de tamaño para mantenerla centrada."""
        width = self.canvas.winfo_width()
        # Evitar redibujos innecesarios si el ancho no cambió significativamente
        if abs(width - self._last_canvas_width) > 2:
            self._last_canvas_width = width
            self.draw_shelf()

    def get_shelves(self):
        """Obtiene la lista de posiciones Y de los estantes."""
        config = self.db.get("shelf_config")
        if isinstance(config, dict) and "shelves" in config:
            return config["shelves"]
        return list(DEFAULT_SHELVES)

    def save_shelves(self, shelves):
        """Guarda la configuración de estantes."""
        self.db.set("shelf_config", {"shelves": shelves})

    def add_shelf(self):
        """Añade un nuevo estante debajo del último."""
        shelves = self.get_shelves()
        if len(shelves) >= 10:
            messagebox.showinfo("Límite", "Máximo 10 estantes.")
            return
        new_y = shelves[-1] + SHELF_SPACING if shelves else 140
        shelves.append(new_y)
        self.save_shelves(shelves)
        self.shelf_count_label.configure(text=f"Estantes: {len(shelves)}")
        self.draw_shelf()

    def remove_shelf(self):
        """Elimina el último estante (si está vacío)."""
        shelves = self.get_shelves()
        if len(shelves) <= 1:
            messagebox.showinfo("Mínimo", "Debe haber al menos 1 estante.")
            return
        last_y = shelves[-1]
        # Verificar si hay libros en el último estante
        shelf_items = [item for item in self.db.get("bookshelf") if item.get("y") == last_y]
        if shelf_items:
            messagebox.showinfo("Ocupado", "El último estante tiene libros. Muévelos primero.")
            return
        shelves.pop()
        self.save_shelves(shelves)
        self.shelf_count_label.configure(text=f"Estantes: {len(shelves)}")
        self.draw_shelf()

    def _book_titles(self):
        books = self.db.get("books")
        if not books:
            return ["Sin libros"]
        shelf_book_ids = {item.get("book_id") for item in self.db.get("bookshelf")}
        available = [b for b in books if b.get("id") not in shelf_book_ids]
        if not available:
            return ["Todos los libros están en la estantería"]
        return [b.get("titulo", "Sin título") for b in available]

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
            self.shelf_grid = {}
            self.refresh_books()
            self.draw_shelf()

    def _rebuild_grid(self):
        """Reconstruye el grid a partir de los datos guardados."""
        self.shelf_grid = {}
        for item in self.db.get("bookshelf"):
            shelf_y = item.get("y")
            x = item.get("x")
            if shelf_y not in self.shelf_grid:
                self.shelf_grid[shelf_y] = {}
            self.shelf_grid[shelf_y][x] = item

    def draw_shelf(self):
        self.canvas.delete("all")
        self._rebuild_grid()
        shelves = self.get_shelves()

        # Obtener ancho real del canvas (ahora siempre correcto gracias a <Configure>)
        canvas_w = max(950, self.canvas.winfo_width())

        # Dimensiones del mueble de estantería
        shelf_inner_w = 800   # ancho interior donde van los libros
        frame_thickness = 18  # grosor del marco de madera
        top_margin = 30       # espacio arriba del primer estante
        bottom_margin = 40    # espacio debajo del último estante

        # Calcular altura total del mueble
        if shelves:
            inner_height = shelves[-1] - shelves[0] + bottom_margin + top_margin
            furniture_h = inner_height + frame_thickness * 2
            furniture_top = shelves[0] - top_margin - frame_thickness
            furniture_bottom = furniture_top + furniture_h
        else:
            furniture_h = 500
            furniture_top = 50
            furniture_bottom = furniture_top + furniture_h

        total_height = furniture_bottom + 50
        self.canvas.configure(scrollregion=(0, 0, canvas_w, total_height))

        # Centro del mueble
        furniture_x = (canvas_w - (shelf_inner_w + frame_thickness * 2)) / 2
        left_frame = furniture_x
        right_frame = furniture_x + shelf_inner_w + frame_thickness * 2
        left_inner = furniture_x + frame_thickness
        right_inner = right_frame - frame_thickness

        # ─── MARCO DEL MUEBLE (efecto 3D de madera) ───
        # Sombra del mueble
        self.canvas.create_rectangle(
            furniture_x + 6, furniture_top + 6,
            right_frame + 6, furniture_bottom + 6,
            fill="#8B7355", outline="", stipple="gray25"
        )

        # Marco exterior (madera oscura)
        self.canvas.create_rectangle(
            furniture_x, furniture_top,
            right_frame, furniture_bottom,
            fill="#6B4423", outline="#4A2F1A", width=2
        )

        # Borde claro superior (efecto 3D)
        self.canvas.create_line(
            furniture_x + 2, furniture_top + 2,
            right_frame - 2, furniture_top + 2,
            fill="#A0785A", width=2
        )
        self.canvas.create_line(
            furniture_x + 2, furniture_top + 2,
            furniture_x + 2, furniture_bottom - 2,
            fill="#A0785A", width=2
        )

        # Borde oscuro inferior (efecto 3D)
        self.canvas.create_line(
            furniture_x + 2, furniture_bottom - 2,
            right_frame - 2, furniture_bottom - 2,
            fill="#4A2F1A", width=2
        )
        self.canvas.create_line(
            right_frame - 2, furniture_top + 2,
            right_frame - 2, furniture_bottom - 2,
            fill="#4A2F1A", width=2
        )

        # ─── ESTANTES (tablones de madera) ───
        for y in shelves:
            # Tablón del estante
            self.canvas.create_rectangle(
                left_inner - 2, y - 4,
                right_inner + 2, y + 4,
                fill="#8B6914", outline="#5C3A21", width=1
            )
            # Borde claro arriba del tablón
            self.canvas.create_line(
                left_inner - 2, y - 3,
                right_inner + 2, y - 3,
                fill="#C4A882", width=1
            )
            # Borde oscuro abajo del tablón
            self.canvas.create_line(
                left_inner - 2, y + 3,
                right_inner + 2, y + 3,
                fill="#5C3A21", width=1
            )

        # Dibujar lomos
        for item in self.db.get("bookshelf"):
            self._draw_spine(item, left_inner, right_inner)

    def _draw_spine(self, item, left_x=30, right_x=920):
        x = item["x"]
        y_base = item["y"]
        color = item.get("color", "#3498db")
        title = item.get("title", "")
        width = item.get("width", 18)
        height = item.get("height", 100)

        shelf_y = min(self.get_shelves(), key=lambda s: abs(s - y_base))
        y_top = shelf_y - height

        # Sombra sutil a la derecha
        self.canvas.create_rectangle(x + 2, y_top + 2, x + width + 2, shelf_y + 2,
                                     fill="#cccccc", outline="", stipple="gray50")

        # Lomo principal
        self.canvas.create_rectangle(x, y_top, x + width, shelf_y,
                                     fill=color, outline="#333", width=1)

        # Borde superior claro
        self.canvas.create_line(x + 1, y_top + 1, x + width - 1, y_top + 1,
                                fill="#ffffff", width=1, stipple="gray50")

        # Texto vertical rotado 90°
        self.canvas.create_text(x + width / 2, (y_top + shelf_y) / 2,
                                text=title, fill="white", font=("Arial", 8),
                                angle=90, anchor="center")

    def _find_slot(self, shelf_y, x_click, width):
        """Verifica si hay espacio en la posición deseada sin solapamiento."""
        grid = self.shelf_grid.get(shelf_y, {})
        self.canvas.update_idletasks()
        canvas_w = max(950, self.canvas.winfo_width())
        shelf_inner_w = 800
        frame_thickness = 18
        left_margin = (canvas_w - (shelf_inner_w + frame_thickness * 2)) / 2 + frame_thickness + 5
        right_margin = left_margin + shelf_inner_w - 5
        x = max(left_margin, min(x_click - width // 2, right_margin - width))

        occupied = sorted(grid.keys())
        for ox in occupied:
            item = grid[ox]
            ow = item.get("width", 40)
            if not (x + width <= ox or x >= ox + ow):
                return None
        return x

    def on_canvas_click(self, event):
        title = self.book_var.get()
        if title in ("Sin libros", "Todos los libros están en la estantería"):
            return

        books = self.db.get("books")
        book = next((b for b in books if b.get("titulo") == title), None)
        if not book:
            return

        shelf = self.db.get("bookshelf")
        if any(item.get("book_id") == book.get("id") for item in shelf):
            messagebox.showinfo("Libro ya colocado", f'"{title}" ya está en la estantería.')
            return

        paginas = book.get("paginas", 200)
        height_by_pages = max(LOMO_H_MIN, min(LOMO_H_MAX, paginas // 3 + 60))
        tlen = len(book["titulo"])
        height_by_title = tlen * 6 + 14
        height = max(height_by_pages, height_by_title)

        width = 18

        shelves = self.get_shelves()
        if len(shelves) < 2:
            messagebox.showinfo("Sin espacio", "Necesitas al menos 2 estantes para colocar libros.")
            return

        # Solo permitir colocar desde el segundo estante en adelante
        valid_shelves = shelves[1:]
        shelf_y = min(valid_shelves, key=lambda s: abs(s - event.y))

        x = self._find_slot(shelf_y, event.x, width)
        if x is None:
            messagebox.showinfo("Espacio ocupado", "Ya hay un libro en esa posición.")
            return

        new_item = {
            "id": Database.generate_id(),
            "book_id": book.get("id"),
            "title": book["titulo"],
            "x": x,
            "y": shelf_y,
            "color": self.color_var.get(),
            "width": width,
            "height": height,
            "tilt": 0
        }

        shelf.append(new_item)
        self.db.set("bookshelf", shelf)
        self.refresh_books()
        self.draw_shelf()

    def on_canvas_right_click(self, event):
        shelves = self.get_shelves()
        if len(shelves) < 2:
            return

        # Solo permitir interactuar desde el segundo estante en adelante
        valid_shelves = shelves[1:]
        shelf_y = min(valid_shelves, key=lambda s: abs(s - event.y))
        if abs(shelf_y - event.y) > 130:
            return

        grid = self.shelf_grid.get(shelf_y, {})
        if not grid:
            return

        closest_item = None
        closest_dist = float("inf")

        for x, item in grid.items():
            width = item.get("width", 40)
            center_x = x + width / 2
            dist = abs(center_x - event.x)
            if dist < closest_dist and dist < width / 2 + 5:
                closest_dist = dist
                closest_item = item

        if closest_item:
            book_title = closest_item.get("title", "este libro")
            if messagebox.askyesno("Eliminar lomo", f'¿Eliminar "{book_title}" de la estantería?'):
                shelf = [item for item in self.db.get("bookshelf")
                         if item.get("id") != closest_item.get("id")]
                self.db.set("bookshelf", shelf)
                self.refresh_books()
                self.draw_shelf()