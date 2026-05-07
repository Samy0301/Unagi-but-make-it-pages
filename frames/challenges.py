"""Gestión de desafíos de lectura."""
import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkScrollableFrame, CTkProgressBar
)

from database import Database


class ChallengesFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        CTkLabel(
            self, text="🏆 Reading Challenges", font=("Helvetica", 28, "bold")
        ).pack(pady=(20, 10))

        top = CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=10)
        self.entry_challenge = CTkEntry(
            top, width=300, placeholder_text="Nombre del desafío..."
        )
        self.entry_challenge.pack(side="left", padx=5)
        self.entry_goal = CTkEntry(
            top, width=100, placeholder_text="Meta (número)"
        )
        self.entry_goal.pack(side="left", padx=5)
        CTkButton(top, text="+ Crear Challenge", command=self.add_challenge).pack(
            side="left", padx=10
        )

        self.scroll = CTkScrollableFrame(
            self, width=900, height=550, fg_color="transparent"
        )
        self.scroll.pack(padx=20, pady=10, fill="both", expand=True)

        self.render()

    def render(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        challenges = self.db.get("challenges")
        if not challenges:
            CTkLabel(
                self.scroll,
                text="Sin desafíos activos. ¡Crea uno! 🚀",
                font=("Arial", 16)
            ).pack(pady=50)
            return

        for ch in challenges:
            card = CTkFrame(self.scroll, corner_radius=15, border_width=2)
            card.pack(fill="x", pady=10, padx=5)

            CTkLabel(
                card, text=ch["nombre"], font=("Arial", 16, "bold")
            ).pack(anchor="w", padx=20, pady=(15, 5))

            progress = CTkProgressBar(
                card, width=800, height=20, corner_radius=10
            )
            progress.pack(padx=20, pady=5)
            prog_val = min(ch.get("actual", 0) / ch.get("meta", 1), 1)
            progress.set(prog_val)

            CTkLabel(
                card,
                text=f"{ch.get('actual', 0)} / {ch['meta']} completado",
                font=("Arial", 12)
            ).pack(anchor="w", padx=20, pady=(0, 10))

            ctrl = CTkFrame(card, fg_color="transparent")
            ctrl.pack(anchor="w", padx=20, pady=(0, 15))
            CTkButton(
                ctrl, text="+1", width=60,
                command=lambda c=ch: self.update_challenge(c, 1)
            ).pack(side="left", padx=5)
            CTkButton(
                ctrl, text="+5", width=60,
                command=lambda c=ch: self.update_challenge(c, 5)
            ).pack(side="left", padx=5)
            CTkButton(
                ctrl, text="🗑 Eliminar", width=100,
                fg_color="red", hover_color="darkred",
                command=lambda c=ch: self.delete_challenge(c)
            ).pack(side="left", padx=20)

    def add_challenge(self):
        name = self.entry_challenge.get().strip()
        goal = self.entry_goal.get().strip()
        if name and goal.isdigit():
            challenges = self.db.get("challenges")
            challenges.append({
                "id": Database.generate_id(),
                "nombre": name,
                "meta": int(goal),
                "actual": 0
            })
            self.db.set("challenges", challenges)
            self.entry_challenge.delete(0, "end")
            self.entry_goal.delete(0, "end")
            self.render()

    def update_challenge(self, ch, delta):
        challenges = self.db.get("challenges")
        for c in challenges:
            if c.get("id") == ch.get("id"):
                c["actual"] = min(c.get("actual", 0) + delta, c["meta"])
                break
        self.db.set("challenges", challenges)
        self.render()

    def delete_challenge(self, ch):
        challenges = self.db.get("challenges")
        challenges = [c for c in challenges if c.get("id") != ch.get("id")]
        self.db.set("challenges", challenges)
        self.render()
