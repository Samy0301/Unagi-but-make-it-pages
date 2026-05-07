"""Challenges - panel reservado para futuras funcionalidades."""
from customtkinter import CTkFrame, CTkLabel

from database import Database


class ChallengesFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(
            self, text="🏆 Challenges",
            font=("Helvetica", 28, "bold")
        ).pack(pady=(40, 20))

        CTkLabel(
            self, text="Panel reservado para futuras funcionalidades.",
            font=("Arial", 14), text_color="gray"
        ).pack(pady=10)

        CTkLabel(
            self, text="Próximamente: desafíos de lectura, metas anuales, bingo literario y más.",
            font=("Arial", 12), text_color="#666"
        ).pack(pady=5)
