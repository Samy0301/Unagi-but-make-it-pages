"""
📚 BOOK JOURNAL v2 - CustomTkinter
Biblioteca | Tracker | Bookshelf | Review | Challenges
"""
import customtkinter as ctk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton

from database import Database, PALETA
from biblioteca import BibliotecaFrame
from tracker import TrackerFrame
from bookshelf import BookshelfFrame
from review import ReviewFrame
from challenges import ChallengesFrame

ctk.set_appearance_mode("Light")
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

        # Sidebar with ocean depth gradient
        self.sidebar = CTkFrame(self, width=220, corner_radius=0, fg_color=PALETA["bg_header"],
                                border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Subtle top glow effect
        self.sidebar_glow = CTkFrame(self.sidebar, height=3, fg_color=PALETA["seafoam"],
                                     corner_radius=0)
        self.sidebar_glow.place(x=0, y=0, relwidth=1)

        CTkLabel(self.sidebar, text="Book\nJournal", font=("Helvetica", 24, "bold")).grid(
            row=0, column=0, pady=(30, 20), padx=20)

        self.nav_buttons = []
        nav_items = [
            ("Biblioteca", "📖", BibliotecaFrame),
            ("Tracker", "", TrackerFrame),
            ("Bookshelf", "", BookshelfFrame),
            ("Review", "", ReviewFrame),
            ("Challenges", "", ChallengesFrame)
        ]

        self.frames = {}
        self.current_frame = None
        self.current_name = None

        for idx, (name, icon, FrameClass) in enumerate(nav_items, 1):
            btn = CTkButton(
                self.sidebar, text=f"{icon} {name}", font=("Arial", 14),
                anchor="w", height=42, width=180,
                fg_color="transparent",
                hover_color=PALETA["sky"],
                text_color=PALETA["ocean"],
                command=lambda f=FrameClass, n=name: self.show_frame(f, n)
            )
            btn.grid(row=idx, column=0, pady=8, padx=15)
            self.nav_buttons.append((btn, name))

        # Content
        self.content = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.show_frame(BibliotecaFrame, "Biblioteca")

    def show_frame(self, FrameClass, name):
        # Actualizar botones del sidebar
        for btn, btn_name in self.nav_buttons:
            if btn_name == name:
                btn.configure(fg_color=PALETA["sand"], text_color=PALETA["text_main"])
            else:
                btn.configure(fg_color="transparent", text_color=PALETA["text_main"])

        # Ocultar frame actual
        if self.current_frame:
            self.current_frame.grid_remove()

        # Crear solo la primera vez
        if name not in self.frames:
            self.frames[name] = FrameClass(self.content, self.db, corner_radius=15)
            self.frames[name].grid(row=0, column=0, sticky="nswe")

        # Mostrar frame cacheado
        frame = self.frames[name]
        frame.grid()

        # Refrescar datos SOLO si la base de datos cambió desde la última vez
        if hasattr(frame, "refresh"):
            current_v = self.db.get_version()
            last_v = getattr(frame, '_last_db_version', -1)
            if current_v != last_v:
                frame.refresh()
                frame._last_db_version = current_v

        self.current_frame = frame
        self.current_name = name


if __name__ == "__main__":
    app = BookJournalApp()
    app.mainloop()