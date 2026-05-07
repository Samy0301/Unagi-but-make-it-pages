"""Visualización de estantería decorativa."""
from tkinter import Canvas

import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkButton

from database import Database


class BookshelfFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(
            self, text="🪴 The Bookshelf", font=("Helvetica", 28, "bold")
        ).pack(pady=(20, 10))

        self.canvas = Canvas(
            self, width=900, height=600, bg="#1a1a1a", highlightthickness=0
        )
        self.canvas.pack(pady=10)

        CTkButton(
            self, text="🎨 Redibujar Estantería", command=self.draw_shelf
        ).pack(pady=10)
        self.draw_shelf()

    def draw_shelf(self):
        self.canvas.delete("all")
        books = self.db.get("books")

        shelf_y = [100, 220, 340, 460, 580]

        for y in shelf_y:
            self.canvas.create_rectangle(
                50, y, 850, y + 10, fill="#5c3a21", outline=""
            )

        shelf_idx = 0
        x_pos = 70
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c"]

        for i, book in enumerate(books[:25]):
            if x_pos > 800:
                shelf_idx += 1
                x_pos = 70
            if shelf_idx >= 5:
                break

            y_base = shelf_y[shelf_idx]
            h = 60 + (hash(book["titulo"]) % 40)
            w = 30 + (hash(book.get("autor", "")) % 20)
            color = colors[i % 6]

            self.canvas.create_rectangle(
                x_pos, y_base - h, x_pos + w, y_base,
                fill=color, outline="#222", width=1
            )
            self.canvas.create_text(
                x_pos + w / 2, y_base - h / 2,
                text=book["titulo"][:8], fill="white",
                font=("Arial", 8), angle=90 if i % 7 == 0 else 0
            )

            x_pos += w + 5

        # Plantas decorativas
        for px, py in [(60, 85), (820, 325), (100, 445)]:
            self.canvas.create_oval(
                px - 15, py - 30, px + 15, py, fill="#2ecc71", outline=""
            )
            self.canvas.create_oval(
                px - 10, py - 45, px + 10, py - 15, fill="#27ae60", outline=""
            )
