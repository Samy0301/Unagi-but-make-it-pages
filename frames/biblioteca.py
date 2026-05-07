"""Vista de Biblioteca con grid de libros."""
import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkScrollableFrame
)
from tkinter import messagebox

from database import Database
from widgets import StarRating


class BibliotecaFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        header = CTkLabel(self, text="📖 BIBLIOTECA", font=("Helvetica", 28, "bold"))
        header.pack(pady=(20, 10))

        btn_add = CTkButton(self, text="+ Agregar Libro", command=self.add_book_dialog)
        btn_add.pack(pady=10)

        self.scroll = CTkScrollableFrame(
            self, width=900, height=600, fg_color="transparent"
        )
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render_books()

    def render_books(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        books = self.db.get("books")
        if not books:
            CTkLabel(
                self.scroll, text="No hay libros aún. ¡Agrega uno!", font=("Arial", 16)
            ).pack(pady=50)
            return

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

        cover = CTkFrame(card, width=140, height=200, corner_radius=8, fg_color="#2b2b2b")
        cover.place(relx=0.5, y=20, anchor="n")
        CTkLabel(cover, text="📕", font=("Arial", 60)).place(
            relx=0.5, rely=0.5, anchor="center"
        )

        CTkLabel(
            card, text=book.get("titulo", "Sin título")[:20], font=("Arial", 12, "bold")
        ).place(relx=0.5, y=235, anchor="center")

        CTkLabel(
            card, text=book.get("autor", "")[:18], font=("Arial", 10)
        ).place(relx=0.5, y=260, anchor="center")

        stars = StarRating(card, rating=book.get("rating", 0), size=16)
        stars.place(relx=0.5, y=295, anchor="center")

        return card

    def add_book_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Libro")
        dialog.geometry("400x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        CTkLabel(dialog, text="Título:").pack(pady=(20, 5))
        entry_titulo = CTkEntry(dialog, width=300)
        entry_titulo.pack()

        CTkLabel(dialog, text="Autor:").pack(pady=(15, 5))
        entry_autor = CTkEntry(dialog, width=300)
        entry_autor.pack()

        CTkLabel(dialog, text="Género:").pack(pady=(15, 5))
        entry_genre = CTkEntry(dialog, width=300)
        entry_genre.pack()

        CTkLabel(dialog, text="Calificación:").pack(pady=(15, 5))
        star = StarRating(dialog, rating=0)
        star.pack()

        def save():
            titulo = entry_titulo.get().strip()
            if not titulo:
                messagebox.showwarning("Campo requerido", "El título es obligatorio.")
                return
            new_book = {
                "id": Database.generate_id(),
                "titulo": titulo,
                "autor": entry_autor.get().strip(),
                "genero": entry_genre.get().strip(),
                "rating": star.rating,
                "estado": "Por leer"
            }
            books = self.db.get("books")
            books.append(new_book)
            self.db.set("books", books)
            dialog.destroy()
            self.render_books()

        CTkButton(dialog, text="Guardar", command=save).pack(pady=30)
