from tkinter import Canvas, colorchooser, messagebox

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkOptionMenu

from database import Database, PALETA


LOMO_H_MIN = 70
LOMO_H_MAX = 130
COLORS = [
    "#0849BA",  
    "#BE100D",  
    "#E2DE04", 
    "#13A01A",  
    "#FB8C00",  
    "#7A079A",  
    "#0A89C4",  
    "#AB04C8", 
    "#F60BCB"
]

DEFAULT_SHELVES = [140, 300, 460]
SHELF_SPACING = 160


class BookshelfFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(self, text="The Bookshelf", font=("Helvetica", 28, "bold"),
                text_color=PALETA["text_main"]).pack(pady=(15, 5))

        ctrl = CTkFrame(self, fg_color="transparent")
        ctrl.pack(fill="x", padx=20, pady=5)

        CTkLabel(ctrl, text="Libro:", text_color=PALETA["text_secondary"]).pack(side="left", padx=5)
        self.book_var = ctk.StringVar()
        self.book_menu = CTkOptionMenu(ctrl, variable=self.book_var, width=200,
                                    values=self._book_titles(),
                                    fg_color=PALETA["bg_input"],
                                    button_color=PALETA["ocean"],
                                    button_hover_color=PALETA["coral"],
                                    text_color=PALETA["text_main"],
                                    dropdown_fg_color=PALETA["bg_card"],
                                    dropdown_text_color=PALETA["text_main"],
                                    dropdown_hover_color=PALETA["coral"])
        self.book_menu.pack(side="left", padx=5)

        CTkLabel(ctrl, text="Color:", text_color=PALETA["text_secondary"]).pack(side="left", padx=(15, 5))
        self.color_var = ctk.StringVar(value=COLORS[0])
        self.color_preview = CTkFrame(ctrl, width=25, height=25,
                                    fg_color=COLORS[0], corner_radius=4,
                                    border_width=2, border_color=PALETA["border"])
        self.color_preview.pack(side="left", padx=5)
        self.color_preview.bind("<Button-1>", self.pick_color)

        for c in COLORS[:5]:
            btn = CTkFrame(ctrl, width=20, height=20, fg_color=c, corner_radius=3,
                        border_width=1, border_color=PALETA["border"])
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, col=c: self.set_color(col))

        for c in COLORS[5:]:
            btn = CTkFrame(ctrl, width=20, height=20, fg_color=c, corner_radius=3,
                        border_width=1, border_color=PALETA["border"])
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, col=c: self.set_color(col))

        CTkButton(ctrl, text="Refrescar", command=self.refresh_books, width=100,
                fg_color=PALETA["ocean"],
                hover_color=PALETA["coral"],
                text_color=PALETA["text_main"]).pack(side="left", padx=10)
        CTkButton(ctrl, text="Limpiar", command=self.clear_shelf,
                fg_color=PALETA["error"],
                hover_color=PALETA["coral"],
                text_color=PALETA["text_main"], width=100).pack(side="left", padx=5)

        shelf_ctrl = CTkFrame(self, fg_color="transparent")
        shelf_ctrl.pack(fill="x", padx=20, pady=(0, 5))
        CTkButton(shelf_ctrl, text="Anadir estante", command=self.add_shelf,
                width=130, corner_radius=8,
                fg_color=PALETA["coral"],
                hover_color=PALETA["coral_light"],
                text_color=PALETA["bg_main"]).pack(side="left", padx=5)
        CTkButton(shelf_ctrl, text="Quitar estante", command=self.remove_shelf,
                width=130, corner_radius=8,
                fg_color=PALETA["ocean"],
                hover_color=PALETA["coral"],
                text_color=PALETA["text_main"]).pack(side="left", padx=5)
        self.shelf_count_label = CTkLabel(shelf_ctrl,
                                        text=f"Estantes: {len(self.get_shelves())}",
                                        font=("Arial", 11),
                                        text_color=PALETA["text_secondary"])
        self.shelf_count_label.pack(side="left", padx=15)

        self.status_label = CTkLabel(self,
            text="Click en la estanteria para colocar el lomo. Click derecho en un lomo para eliminarlo.",
            font=("Arial", 11), text_color=PALETA["text_muted"])
        self.status_label.pack(pady=2)

        self.canvas_frame = CTkFrame(self, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = Canvas(self.canvas_frame, bg=PALETA["bg_panel"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

        self.vscroll = ctk.CTkScrollbar(self.canvas_frame, command=self.canvas.yview)
        self.vscroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        self._shelf_grid = {}
        self._canvas_items = {}

        self._last_canvas_width = 0
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.draw_shelf()

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(3, "units")

    def _on_canvas_configure(self, event=None):
        width = self.canvas.winfo_width()
        if abs(width - self._last_canvas_width) > 2:
            self._last_canvas_width = width
            self.draw_shelf()

    def get_shelves(self):
        config = self.db.get("shelf_config")
        if isinstance(config, dict) and "shelves" in config:
            return config["shelves"]
        return list(DEFAULT_SHELVES)

    def save_shelves(self, shelves):
        self.db.set("shelf_config", {"shelves": shelves})

    def add_shelf(self):
        shelves = self.get_shelves()
        if len(shelves) >= 10:
            messagebox.showinfo("Limite", "Maximo 10 estantes.")
            return
        new_y = shelves[-1] + SHELF_SPACING if shelves else 140
        shelves.append(new_y)
        self.save_shelves(shelves)
        self.shelf_count_label.configure(text=f"Estantes: {len(shelves)}")
        self.draw_shelf()

    def remove_shelf(self):
        shelves = self.get_shelves()
        if len(shelves) <= 1:
            messagebox.showinfo("Minimo", "Debe haber al menos 1 estante.")
            return
        last_y = shelves[-1]
        shelf_items = [item for item in self.db.get("bookshelf") if item.get("y") == last_y]
        if shelf_items:
            messagebox.showinfo("Ocupado", "El ultimo estante tiene libros. Muevelos primero.")
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
            return ["Todos los libros estan en la estanteria"]
        return [b.get("titulo", "Sin titulo") for b in available]

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
        if messagebox.askyesno("Confirmar", "Eliminar todos los lomos de la estanteria?"):
            self.db.set("bookshelf", [])
            self._shelf_grid = {}
            self._canvas_items = {}
            self.refresh_books()
            self.draw_shelf()

    def _rebuild_grid(self):
        self._shelf_grid = {}
        for item in self.db.get("bookshelf"):
            shelf_y = item.get("y")
            x = item.get("x")
            if shelf_y not in self._shelf_grid:
                self._shelf_grid[shelf_y] = set()
            self._shelf_grid[shelf_y].add(x)

    def draw_shelf(self):
        self.canvas.delete("all")
        self._canvas_items = {}
        self._rebuild_grid()
        shelves = self.get_shelves()

        canvas_w = max(950, self.canvas.winfo_width())
        shelf_inner_w = 800
        frame_thickness = 18
        top_margin = 30
        bottom_margin = 40

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

        furniture_x = (canvas_w - (shelf_inner_w + frame_thickness * 2)) / 2
        left_frame = furniture_x
        right_frame = furniture_x + shelf_inner_w + frame_thickness * 2
        left_inner = furniture_x + frame_thickness
        right_inner = right_frame - frame_thickness

        self.canvas.create_rectangle(
            furniture_x + 6, furniture_top + 6,
            right_frame + 6, furniture_bottom + 6,
            fill=PALETA["shadow"], outline="", stipple="gray25"
        )

        self.canvas.create_rectangle(
            furniture_x, furniture_top,
            right_frame, furniture_bottom,
            fill=PALETA["bg_card"], outline=PALETA["border_accent"], width=2
        )

        self.canvas.create_line(
            furniture_x + 2, furniture_top + 2,
            right_frame - 2, furniture_top + 2,
            fill=PALETA["wave"], width=2
        )
        self.canvas.create_line(
            furniture_x + 2, furniture_top + 2,
            furniture_x + 2, furniture_bottom - 2,
            fill=PALETA["wave"], width=2
        )

        self.canvas.create_line(
            furniture_x + 2, furniture_bottom - 2,
            right_frame - 2, furniture_bottom - 2,
            fill=PALETA["bg_header"], width=2
        )
        self.canvas.create_line(
            right_frame - 2, furniture_top + 2,
            right_frame - 2, furniture_bottom - 2,
            fill=PALETA["bg_header"], width=2
        )

        for y in shelves:
            self.canvas.create_rectangle(
                left_inner - 2, y - 4,
                right_inner + 2, y + 4,
                fill=PALETA["bg_header"], outline=PALETA["border_accent"], width=1
            )
            self.canvas.create_line(
                left_inner - 2, y - 3,
                right_inner + 2, y - 3,
                fill=PALETA["wave"], width=1
            )
            self.canvas.create_line(
                left_inner - 2, y + 3,
                right_inner + 2, y + 3,
                fill=PALETA["ocean"], width=1
            )

        for item in self.db.get("bookshelf"):
            self._draw_spine(item, left_inner, right_inner)

    def _draw_spine(self, item, left_x, right_x):
        x = item["x"]
        y_base = item["y"]
        color = item.get("color", "#48D1CC")
        title = item.get("title", "")
        width = item.get("width", 18)
        height = item.get("height", 100)

        shelf_y = min(self.get_shelves(), key=lambda s: abs(s - y_base))
        y_top = shelf_y - height

        ids = []

        ids.append(self.canvas.create_rectangle(
            x + 2, y_top + 2, x + width + 2, shelf_y + 2,
            fill=PALETA["shadow"], outline="", stipple="gray50"
        ))

        ids.append(self.canvas.create_rectangle(
            x, y_top, x + width, shelf_y,
            fill=color, outline=PALETA["border_accent"], width=1
        ))

        ids.append(self.canvas.create_line(
            x + 1, y_top + 1, x + width - 1, y_top + 1,
            fill=PALETA["text_main"], width=1, stipple="gray50"
        ))

        ids.append(self.canvas.create_text(
            x + width / 2, (y_top + shelf_y) / 2,
            text=title, fill=PALETA["text_main"], font=("Arial", 8),
            angle=90, anchor="center"
        ))

        for iid in ids:
            self._canvas_items[iid] = item

    def _find_slot(self, shelf_y, x_click, width):
        grid = self._shelf_grid.get(shelf_y, set())
        canvas_w = max(950, self.canvas.winfo_width())
        shelf_inner_w = 800
        frame_thickness = 18
        left_margin = (canvas_w - (shelf_inner_w + frame_thickness * 2)) / 2 + frame_thickness + 5
        right_margin = left_margin + shelf_inner_w - 5
        x = max(left_margin, min(x_click - width // 2, right_margin - width))

        for ox in grid:
            ow = 18
            if not (x + width <= ox or x >= ox + ow):
                return None
        return x

    def on_canvas_click(self, event):
        title = self.book_var.get()
        if title in ("Sin libros", "Todos los libros estan en la estanteria"):
            return

        books = self.db.get("books")
        book = next((b for b in books if b.get("titulo") == title), None)
        if not book:
            return

        shelf = self.db.get("bookshelf")
        if any(item.get("book_id") == book.get("id") for item in shelf):
            messagebox.showinfo("Libro ya colocado", f'"{title}" ya esta en la estanteria.')
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

        valid_shelves = shelves[1:]
        click_y = self.canvas.canvasy(event.y)
        shelf_y = min(valid_shelves, key=lambda s: abs(s - click_y))

        click_x = self.canvas.canvasx(event.x)
        x = self._find_slot(shelf_y, click_x, width)
        if x is None:
            messagebox.showinfo("Espacio ocupado", "Ya hay un libro en esa posicion.")
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
        self._rebuild_grid()
        self._draw_spine(new_item,
                        (max(950, self.canvas.winfo_width()) - (800 + 36)) / 2 + 18 + 5,
                        (max(950, self.canvas.winfo_width()) - (800 + 36)) / 2 + 800 + 18 - 5)

    def on_canvas_right_click(self, event):
        shelves = self.get_shelves()
        if len(shelves) < 2:
            return

        valid_shelves = shelves[1:]
        click_y = self.canvas.canvasy(event.y)
        shelf_y = min(valid_shelves, key=lambda s: abs(s - click_y))
        if abs(shelf_y - click_y) > 130:
            return

        click_x = self.canvas.canvasx(event.x)
        closest_item = None
        closest_dist = float("inf")

        for iid, item in self._canvas_items.items():
            x = item.get("x", 0)
            w = item.get("width", 40)
            center_x = x + w / 2
            dist = abs(center_x - click_x)
            if dist < closest_dist and dist < w / 2 + 5:
                closest_dist = dist
                closest_item = item

        if closest_item:
            book_title = closest_item.get("title", "este libro")
            if messagebox.askyesno("Eliminar lomo", f'Eliminar "{book_title}" de la estanteria?'):
                shelf = [item for item in self.db.get("bookshelf")
                        if item.get("id") != closest_item.get("id")]
                self.db.set("bookshelf", shelf)
                self.refresh_books()
                self.draw_shelf()

    def refresh(self):
        self.refresh_books()
        self.draw_shelf()