"""
📚 BOOK JOURNAL v2 - CustomTkinter
Biblioteca | Tracker | Bookshelf | Review | Challenges
"""
import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkSwitch

from database import Database
from frames.biblioteca import BibliotecaFrame
from frames.tracker import TrackerFrame
from frames.bookshelf import BookshelfFrame
from frames.review import ReviewFrame
from frames.challenges import ChallengesFrame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class BookJournalApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("📚 Book Journal v2")
        self.geometry("1250x850")
        self.minsize(1100, 750)

        self.db = Database()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(8, weight=1)

        CTkLabel(self.sidebar, text="📚 Book\nJournal", font=("Helvetica", 24, "bold")).grid(
            row=0, column=0, pady=(30, 20), padx=20)

        self.nav_buttons = []
        nav_items = [
            ("Biblioteca", "📖", BibliotecaFrame),
            ("Tracker", "📅", TrackerFrame),
            ("Bookshelf", "🪴", BookshelfFrame),
            ("Review", "✍️", ReviewFrame),
            ("Challenges", "🏆", ChallengesFrame)
        ]

        self.current_frame = None
        for idx, (name, icon, FrameClass) in enumerate(nav_items, 1):
            btn = CTkButton(
                self.sidebar, text=f"{icon} {name}", font=("Arial", 14),
                anchor="w", height=42, width=180,
                command=lambda f=FrameClass, n=name: self.show_frame(f, n)
            )
            btn.grid(row=idx, column=0, pady=8, padx=15)
            self.nav_buttons.append((btn, name))

        # Theme
        self.theme_switch = CTkSwitch(
            self.sidebar, text="Modo Oscuro", command=self.toggle_theme
        )
        self.theme_switch.grid(row=9, column=0, pady=20, padx=15, sticky="s")
        self.theme_switch.select()

        # Content
        self.content = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.show_frame(BibliotecaFrame, "Biblioteca")

    def show_frame(self, FrameClass, name):
        for btn, btn_name in self.nav_buttons:
            if btn_name == name:
                btn.configure(fg_color=["#3a7ebf", "#1f538d"], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=["black", "white"])

        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = FrameClass(self.content, self.db, corner_radius=15)
        self.current_frame.grid(row=0, column=0, sticky="nswe")

    def toggle_theme(self):
        mode = "Dark" if self.theme_switch.get() else "Light"
        ctk.set_appearance_mode(mode)


if __name__ == "__main__":
    app = BookJournalApp()
    app.mainloop()
