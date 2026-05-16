"""Challenges - Retos literarios con estética de carpetas."""
import os
import tkinter
from tkinter import filedialog, messagebox

import customtkinter as ctk
from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkEntry,
    CTkScrollableFrame
)
from PIL import Image

try:
    from customtkinter import CTkImage
except ImportError:
    CTkImage = None

from database import Database


# ═══════════════════════════════════════════════════════════════════
#  DATOS DE RETOS
# ═══════════════════════════════════════════════════════════════════
RETO_LECTOR_DATA = {
    1:  {"mes": "ENERO",      "color": "#AED6F1"},
    2:  {"mes": "FEBRERO",    "color": "#F5B7B1"},
    3:  {"mes": "MARZO",      "color": "#F9E79F"},
    4:  {"mes": "ABRIL",      "color": "#F5B7B1"},
    5:  {"mes": "MAYO",       "color": "#D4EFDF"},
    6:  {"mes": "JUNIO",      "color": "#AED6F1"},
    7:  {"mes": "JULIO",      "color": "#FADBD8"},
    8:  {"mes": "AGOSTO",     "color": "#FCF3CF"},
    9:  {"mes": "SEPTIEMBRE", "color": "#E8DAEF"},
    10: {"mes": "OCTUBRE",    "color": "#D5F5E3"},
    11: {"mes": "NOVIEMBRE",  "color": "#D6EAF8"},
    12: {"mes": "DICIEMBRE",  "color": "#FADBD8"},
}

COLLECT_COLORS_DATA = [
    {"key": "red",        "name": "Red",        "color": "#FF8A65", "bg": "#FDEDEC"},
    {"key": "orange",     "name": "Orange",     "color": "#E67E22", "bg": "#FEF5E7"},
    {"key": "yellow",     "name": "Yellow",     "color": "#F1C40F", "bg": "#FCF3CF"},
    {"key": "green",      "name": "Green",      "color": "#4DD0E1", "bg": "#EAFAF1"},
    {"key": "light_blue", "name": "Light Blue", "color": "#5DADE2", "bg": "#EBF5FB"},
    {"key": "blue",       "name": "Blue",       "color": "#2980B9", "bg": "#D6EAF8"},
    {"key": "purple",     "name": "Purple",     "color": "#8E44AD", "bg": "#F4ECF7"},
    {"key": "pink",       "name": "Pink",       "color": "#FF69B4", "bg": "#FDEBF7"},
    {"key": "brown",      "name": "Brown",      "color": "#8B4513", "bg": "#F6ECE1"},
    {"key": "black",      "name": "Black",      "color": "#0B3A5C", "bg": "#EAECEE"},
    {"key": "grey",       "name": "Grey",       "color": "#7F8C8D", "bg": "#F2F4F4"},
    {"key": "#E0F7FA",      "name": "White",      "color": "#BDC3C7", "bg": "#FBFCFC"},
]



# ═══════════════════════════════════════════════════════════════════
#  GENRE TRACKER DATA
# ═══════════════════════════════════════════════════════════════════
GENRE_TRACKER_DATA = [
    {"key": "thriller", "name": "Thriller", "color": "#FF7043"},
    {"key": "ciencia_ficcion", "name": "Ciencia\nFicción", "color": "#00CED1"},
    {"key": "fantasia", "name": "Fantasía", "color": "#8E44AD"},
    {"key": "terror", "name": "Terror", "color": "#0B3A5C"},
    {"key": "romantico", "name": "Romántico", "color": "#FF69B4"},
    {"key": "aventura", "name": "Aventura", "color": "#4DD0E1"},
    {"key": "distopia", "name": "Distopía", "color": "#7D3C98"},
    {"key": "historica", "name": "Histórica", "color": "#D2691E"},
    {"key": "biografia", "name": "Biografía", "color": "#2980B9"},
    {"key": "divulgacion", "name": "Divulgación\nCientífica", "color": "#F1C40F"},
]


# ═══════════════════════════════════════════════════════════════════
#  30 DAY READING CHALLENGE DATA
# ═══════════════════════════════════════════════════════════════════
READING_30_DATA = list(range(1, 31))   # 1 … 30
READING_30_COLS = 5


# ═══════════════════════════════════════════════════════════════════
#  ALPHABET READING CHALLENGE DATA
# ═══════════════════════════════════════════════════════════════════
ALPHABET_LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


# ═══════════════════════════════════════════════════════════════════
#  BOOKISH BINGO CHALLENGE CHALLENGE DATA
# ═══════════════════════════════════════════════════════════════════
BINGO_DATA = [
    "Título de una sola palabra",
    "Enemies to lovers",
    "Adaptado a película/serie",
    "Protagonista con mascota",
    "Menos de 200 páginas",
    "Viaje en el tiempo",
    "Segunda oportunidad",
    "Basado en hechos reales",
    "Protagonista forma parte de una banda",
    "Primera parte de saga",
    "Más de 500 páginas",
    "Publicado este año",
    "Presencia de criaturas fantásticas",
    "Found family",
    "Only one bed",
    "Ambientado en invierno",
    "De tu año de nacimiento",
    "Slow burn",
    "Autor debut",
    "Empieza con tu inicial",
    "Magia en el mundo real",
    "Número en el título",
    "Pueblo secreto/misterioso",
    "Blow-your-mind\nplot twist",
    "Libro que hable de libros",
]


# ═══════════════════════════════════════════════════════════════════
#  YEARLY READING CHALLENGE DATA (31 retos + 5 bonus)
# ═══════════════════════════════════════════════════════════════════
YEARLY_DATA = [
    "Libro favorito de un miembro del club de lectura",
    "El título contiene un número",
    "Un libro con magia",
    "Un libro con vampiros",
    "El protagonista es un atleta",
    "Un libro fuera de tu zona de confort",
    "Una flor en la portada",
    "No lo descubriste en BookTok",
    "Un libro con un levantamiento o rebelión",
    "Portada de tu color favorito",
    "Juzga un libro por su portada",
    "Autor nuevo para ti",
    "Múltiples puntos de vista",
    "Un libro viral en BookTok",
    "El título tiene 5+ palabras",
    "Un arma en la portada",
    "Publicado este año",
    "Un libro sobre una biblioteca",
    "Un libro en la lista de prohibidos",
    "Publicado antes del año actual",
    "Un libro que te regalaron",
    "Un libro que te haga llorar",
    "Un libro sin personaje en la portada",
    "Publicado en el mes de tu nacimiento",
    "Humo en la portada",
    "Un libro que tiene dragones",
    "Novela gráfica",
    "Una duología",
    "Llevaba 3+ años en tu TBR",
    "Una reimaginación",
    "600+ páginas",
]
# ═══════════════════════════════════════════════════════════════════
#  WIDGET AUXILIAR: Tarjeta-Carpeta visual
# ═══════════════════════════════════════════════════════════════════
class FolderCard(CTkFrame):
    def __init__(self, parent, title, subtitle="", icon="📁", color="#F4D03F",
                 command=None, width=240, height=200, **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height, **kwargs)
        self.pack_propagate(False)
        self.command = command

        self.tab = CTkFrame(self, width=100, height=22, fg_color=color, corner_radius=6)
        self.tab.place(x=18, y=2)
        self.tab.pack_propagate(False)

        self.body = CTkFrame(self, width=width, height=height-20, fg_color=color, corner_radius=12)
        self.body.place(x=0, y=20)
        self.body.pack_propagate(False)

        CTkLabel(self.body, text=icon, font=("Arial", 52)).pack(pady=(18, 4))
        CTkLabel(self.body, text=title, font=("Arial", 15, "bold"), text_color="#2c3e50").pack()
        if subtitle:
            CTkLabel(self.body, text=subtitle, font=("Arial", 10), text_color="#0D3B5C").pack(pady=(2, 0))

        for widget in (self, self.tab, self.body):
            widget.bind("<Button-1>", lambda e: self._invoke())
        for child in self.body.winfo_children():
            child.bind("<Button-1>", lambda e: self._invoke())
            child.configure(cursor="hand2")
        self.configure(cursor="hand2")

    def _invoke(self):
        if self.command:
            self.command()


# ═══════════════════════════════════════════════════════════════════
#  FRAME PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
class ChallengesFrame(CTkFrame):
    def __init__(self, master, db: Database, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.configure(fg_color="transparent")

        self._cover_cache = {}
        self._form_foto_path = None
        self._form_preview_img = None
        self._current_challenge_type = None
        self._current_challenge_key = None
        self._alpha_editing = None   # letra actualmente en modo edición

        # ── Panel carpetas ──
        self.folders_panel = CTkScrollableFrame(self, fg_color="transparent")

        # ── Reto Lector ──
        self.reto_panel = CTkFrame(self, fg_color="transparent")
        h1 = CTkFrame(self.reto_panel, fg_color="transparent")
        h1.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h1, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h1, text="📅 Reto Lector 2026", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)
        self.reto_scroll = CTkScrollableFrame(self.reto_panel, fg_color="transparent")
        self.reto_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # ── Collect Colors ──
        self.collect_panel = CTkFrame(self, fg_color="transparent")
        h2 = CTkFrame(self.collect_panel, fg_color="transparent")
        h2.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h2, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h2, text="🌈 Collect the Colors", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)
        self.collect_scroll = CTkScrollableFrame(self.collect_panel, fg_color="transparent")
        self.collect_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # ── Bracket ──
        self.bracket_panel = CTkFrame(self, fg_color="transparent")
        h3 = CTkFrame(self.bracket_panel, fg_color="transparent")
        h3.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h3, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h3, text="🏆 Genre Tracker", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)

        # Scroll VERTICAL para el bracket (estructura vertical)
        self.bracket_scroll = CTkScrollableFrame(self.bracket_panel, width=900, height=650,
                                                  fg_color="transparent")
        self.bracket_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.bracket_canvas = self.bracket_scroll._parent_canvas
        self.bracket_canvas.configure(bg="#0B1B2B", highlightthickness=0)

        # ── 30 Day Challenge ──
        self.day30_panel = CTkFrame(self, fg_color="transparent")
        h4 = CTkFrame(self.day30_panel, fg_color="transparent")
        h4.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h4, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h4, text="🔥 30 Day Reading Challenge", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)

        self.day30_scroll = CTkScrollableFrame(self.day30_panel, width=900, height=650,
                                                  fg_color="transparent")
        self.day30_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Alphabet Challenge ──
        self.alpha_panel = CTkFrame(self, fg_color="transparent")
        h5 = CTkFrame(self.alpha_panel, fg_color="transparent")
        h5.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h5, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h5, text="🔤 Alphabet Reading Challenge", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)

        self.alpha_scroll = CTkScrollableFrame(self.alpha_panel, width=900, height=650,
                                                fg_color="transparent")
        self.alpha_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Bookish Bingo ──
        self.bingo_panel = CTkFrame(self, fg_color="transparent")
        h6 = CTkFrame(self.bingo_panel, fg_color="transparent")
        h6.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h6, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h6, text="🎀 Bookish Bingo", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)

        self.bingo_scroll = CTkScrollableFrame(self.bingo_panel, width=900, height=650,
                                                fg_color="transparent")
        self.bingo_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Yearly Challenge ──
        self.yearly_panel = CTkFrame(self, fg_color="transparent")
        h7 = CTkFrame(self.yearly_panel, fg_color="transparent")
        h7.pack(fill="x", padx=20, pady=(15, 5))
        CTkButton(h7, text="← Volver", width=90, command=self.show_folders).pack(side="left")
        CTkLabel(h7, text="YEARLY", font=("Helvetica", 28, "bold"), text_color="#81D4FA").pack(side="left", padx=(15, 4))
        CTkLabel(h7, text="READING", font=("Helvetica", 28, "bold"), text_color="#4A90A4").pack(side="left", padx=(0, 4))
        CTkLabel(h7, text="CHALLENGE", font=("Helvetica", 28, "bold"), text_color="#81D4FA").pack(side="left")

        self.yearly_scroll = CTkScrollableFrame(self.yearly_panel, width=900, height=650,
                                                 fg_color="transparent")
        self.yearly_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Formulario (reutilizable) ──
        self.form_panel = CTkFrame(self, fg_color="#0B1B2B", corner_radius=16,
                                   border_width=2, border_color="#1E5F8E")
        CTkLabel(self.form_panel, text="📝 Completar Reto", font=("Helvetica", 22, "bold")).pack(pady=(18, 12))
        self.form_scroll = CTkScrollableFrame(self.form_panel, width=800, height=500, fg_color="transparent")
        self.form_scroll.pack(padx=25, pady=5, fill="both", expand=True)

        self.cover_box = CTkFrame(self.form_scroll, width=160, height=200, corner_radius=10,
                             fg_color="#162F4A", border_width=2, border_color="#1E5F8E")
        self.cover_box.pack(pady=(0, 10))
        self.cover_box.pack_propagate(False)
        CTkButton(self.form_scroll, text="📁 Examinar portada", width=160, height=34,
                  command=self.browse_form_photo).pack(pady=(0, 15))

        def form_row(label, attr_name, width=600):
            CTkLabel(self.form_scroll, text=label, font=("Arial", 11, "bold"), text_color="#4A90A4").pack(anchor="w", pady=(0, 2))
            entry = CTkEntry(self.form_scroll, width=width, height=34, corner_radius=8, font=("Arial", 13))
            entry.pack(anchor="w", pady=(0, 12))
            setattr(self, attr_name, entry)
        form_row("Título del libro *", "form_titulo")
        form_row("Autor", "form_autor")
        self.form_context_label = CTkLabel(self.form_scroll, text="", font=("Arial", 12),
                                          text_color="#aaa", wraplength=700)
        self.form_context_label.pack(pady=(5, 15))

        btn_row = CTkFrame(self.form_panel, fg_color="transparent")
        btn_row.pack(pady=(10, 18))
        CTkButton(btn_row, text="💾 Guardar", command=self.save_form,
                  height=38, font=("Arial", 13, "bold"), corner_radius=10).pack(side="left", padx=8)
        CTkButton(btn_row, text="✕ Cancelar", command=self.close_form,
                  height=38, font=("Arial", 13), corner_radius=10,
                  fg_color="#0D3B5C", hover_color="#4A90A4").pack(side="left", padx=8)

        self.build_folders()
        self.show_folders()

    # ═══════════════════════════════════════════════════════════════
    #  DB
    # ═══════════════════════════════════════════════════════════════
    def _ensure_challenges(self):
        raw = self.db.get("challenges")
        if not isinstance(raw, dict):
            data = {"reto_lector": {}, "collect_colors": {}, "bracket": {}}
            self.db.set("challenges", data)
            return data
        for k in ("reto_lector", "collect_colors", "bracket"):
            raw.setdefault(k, {})
        self.db.set("challenges", raw)
        return raw

    def _get_saved(self, challenge_type, key):
        ch = self._ensure_challenges()
        return ch.get(challenge_type, {}).get(str(key), None)

    def _set_saved(self, challenge_type, key, data_dict):
        ch = self._ensure_challenges()
        ch[challenge_type][str(key)] = data_dict
        self.db.set("challenges", ch)

    # ═══════════════════════════════════════════════════════════════
    #  PORTADAS
    # ═══════════════════════════════════════════════════════════════
    def _load_cover(self, path, size=(120, 160)):
        if not path or not os.path.exists(path):
            return None
        cache_key = (path, size)
        if cache_key in self._cover_cache:
            return self._cover_cache[cache_key]
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            if CTkImage:
                ctk_img = CTkImage(light_image=img, dark_image=img, size=size)
                self._cover_cache[cache_key] = ctk_img
                return ctk_img
        except Exception:
            pass
        return None

    def browse_form_photo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            self._form_foto_path = path
            self._build_preview(path)

    # ═══════════════════════════════════════════════════════════════
    #  CARPETAS
    # ═══════════════════════════════════════════════════════════════
    def build_folders(self):
        for w in self.folders_panel.winfo_children():
            w.destroy()
        container = CTkFrame(self.folders_panel, fg_color="transparent")
        container.pack(expand=True, fill="both", pady=30)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(4, weight=1)

        f1 = FolderCard(container, title="Reto Lector 2026",
                        subtitle="12 meses · 12 libros",
                        icon="📅", color="#F9E79F",
                        command=self.show_reto_lector)
        f1.grid(row=0, column=1, padx=15, pady=20)

        f2 = FolderCard(container, title="Collect the Colors",
                        subtitle="12 colores · 12 portadas",
                        icon="🌈", color="#D6EAF8",
                        command=self.show_collect_colors)
        f2.grid(row=0, column=2, padx=15, pady=20)

        f3 = FolderCard(container, title="Genre Tracker",
                        subtitle="10 géneros · 20 libros cada uno",
                        icon="🏆", color="#FADBD8",
                        command=self.show_bracket)
        f3.grid(row=0, column=3, padx=15, pady=20)

        f4 = FolderCard(container, title="30 Day Challenge",
                        subtitle="30 días · Lectura consecutiva",
                        icon="🔥", color="#F5B7B1",
                        command=self.show_day30)
        f4.grid(row=1, column=1, padx=15, pady=20)

        f5 = FolderCard(container, title="Alphabet Challenge",
                        subtitle="A-Z · Un libro por cada letra",
                        icon="🔤", color="#D4EFDF",
                        command=self.show_alpha)
        f5.grid(row=1, column=2, padx=15, pady=20)

        f6 = FolderCard(container, title="Bookish Bingo",
                        subtitle="25 casillas · 5×5",
                        icon="🎀", color="#FADBD8",
                        command=self.show_bingo)
        f6.grid(row=1, column=3, padx=15, pady=20)

        f7 = FolderCard(container, title="Yearly Challenge",
                        subtitle="31 retos · Portadas",
                        icon="📅", color="#D4EFDF",
                        command=self.show_yearly)
        f7.grid(row=2, column=1, columnspan=2, padx=15, pady=20)

    def show_folders(self):
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.day30_panel.pack_forget()
        self.alpha_panel.pack_forget()
        self.bingo_panel.pack_forget()
        self.yearly_panel.pack_forget()
        self.form_panel.pack_forget()
        self._alpha_editing = None
        self.folders_panel.pack(fill="both", expand=True, padx=10, pady=10)

    # ═══════════════════════════════════════════════════════════════
    #  RETO LECTOR
    # ═══════════════════════════════════════════════════════════════
    def show_reto_lector(self):
        self.folders_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_reto_lector()
        self.reto_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_reto_lector(self):
        for w in self.reto_scroll.winfo_children():
            w.destroy()
        cols = 4
        for c in range(cols):
            self.reto_scroll.grid_columnconfigure(c, weight=1)
        for idx, (mes_num, info) in enumerate(RETO_LECTOR_DATA.items()):
            row = idx // cols
            col = idx % cols
            card = self._build_mes_card(self.reto_scroll, mes_num, info)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _build_mes_card(self, parent, mes_num, info):
        saved = self._get_saved("reto_lector", mes_num)
        color = info["color"]
        card = CTkFrame(parent, width=280, height=340, corner_radius=14,
                        border_width=2, border_color=color, fg_color="#112240")
        card.grid_propagate(False)
        hdr = CTkFrame(card, fg_color=color, corner_radius=14, height=38)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)
        CTkLabel(hdr, text=info["mes"], font=("Helvetica", 14, "bold"),
                 text_color="#2c3e50").place(relx=0.5, rely=0.5, anchor="center")
        CTkLabel(card, text="📖 Libro favorito del mes", font=("Arial", 11, "bold"), text_color="#81D4FA").pack(pady=(10, 8), padx=10)
        content = CTkFrame(card, fg_color="transparent", height=210)
        content.pack(fill="x", padx=10, pady=(0, 8))
        content.pack_propagate(False)
        if saved:
            img = self._load_cover(saved.get("foto"), size=(110, 150))
            if img:
                CTkLabel(content, image=img, text="").pack(pady=(8, 4))
            else:
                CTkLabel(content, text="📕", font=("Arial", 48)).pack(pady=(20, 4))
            CTkLabel(content, text=saved.get("titulo", ""), font=("Arial", 12, "bold"),
                     wraplength=250).pack(pady=(4, 0))
            CTkLabel(content, text=saved.get("autor", ""), font=("Arial", 10),
                     text_color="#4A90A4", wraplength=250).pack()
        else:
            CTkLabel(content, text="Sin libro favorito", font=("Arial", 12),
                     text_color="#4A90A4").place(relx=0.5, rely=0.4, anchor="center")
            CTkButton(content, text="➕ Añadir favorito", width=140, height=30,
                      command=lambda m=mes_num: self.open_form("reto_lector", m)).place(relx=0.5, rely=0.7, anchor="center")
        if saved:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e, m=mes_num: self.open_form("reto_lector", m))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, m=mes_num: self.open_form("reto_lector", m))
        return card

    # ═══════════════════════════════════════════════════════════════
    #  COLLECT COLORS
    # ═══════════════════════════════════════════════════════════════
    def show_collect_colors(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_collect_colors()
        self.collect_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_collect_colors(self):
        for w in self.collect_scroll.winfo_children():
            w.destroy()
        cols = 5
        for c in range(cols):
            self.collect_scroll.grid_columnconfigure(c, weight=1)
        for idx, cdata in enumerate(COLLECT_COLORS_DATA):
            row = idx // cols
            col = idx % cols
            card = self._build_color_card(self.collect_scroll, cdata)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _build_color_card(self, parent, cdata):
        saved = self._get_saved("collect_colors", cdata["key"])
        color = cdata["color"]
        card = CTkFrame(parent, width=200, height=280, corner_radius=14,
                        border_width=2, border_color=color, fg_color="#112240")
        card.grid_propagate(False)
        hdr = CTkFrame(card, fg_color=color, corner_radius=14, height=32)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)
        CTkLabel(hdr, text=cdata["name"], font=("Helvetica", 13, "bold"),
                 text_color="#E0F7FA" if cdata["key"] in ("black", "blue", "purple", "brown") else "#2c3e50"
                 ).place(relx=0.5, rely=0.5, anchor="center")
        slot = CTkFrame(card, width=120, height=160, corner_radius=10,
                        border_width=4, border_color=color, fg_color="#0B1B2B")
        slot.pack(pady=(15, 8))
        slot.pack_propagate(False)
        if saved:
            img = self._load_cover(saved.get("foto"), size=(110, 150))
            if img:
                CTkLabel(slot, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
            else:
                CTkLabel(slot, text="📕", font=("Arial", 40)).place(relx=0.5, rely=0.5, anchor="center")
            CTkLabel(card, text=saved.get("titulo", ""), font=("Arial", 11, "bold"),
                     wraplength=180).pack(pady=(2, 0))
            CTkLabel(card, text=saved.get("autor", ""), font=("Arial", 10),
                     text_color="#4A90A4", wraplength=180).pack()
        else:
            CTkLabel(slot, text="📕", font=("Arial", 40), text_color="#1E5F8E").place(relx=0.5, rely=0.5, anchor="center")
            CTkButton(card, text="➕ Añadir", width=120, height=28,
                      command=lambda k=cdata["key"]: self.open_form("collect_colors", k)).pack(pady=(8, 0))
        if saved:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e, k=cdata["key"]: self.open_form("collect_colors", k))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, k=cdata["key"]: self.open_form("collect_colors", k))
        return card


    # ═══════════════════════════════════════════════════════════════
    #  GENRE TRACKER
    # ═══════════════════════════════════════════════════════════════
    def _get_genre_tracker(self):
        ch = self._ensure_challenges()
        return ch.get("genre_tracker", {})

    def _set_genre_tracker(self, data):
        ch = self._ensure_challenges()
        ch["genre_tracker"] = data
        self.db.set("challenges", ch)

    def show_bracket(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_bracket()
        self.bracket_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_bracket(self):
        for w in self.bracket_scroll.winfo_children():
            w.destroy()

        container = CTkFrame(self.bracket_scroll, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        CTkLabel(container, text="🎨 Genre Tracker", font=("Helvetica", 26, "bold")).pack(pady=(0, 5))
        CTkLabel(container, text="Haz clic para marcar un libro leído · Clic derecho en un cuadro pintado para despintar",
                 font=("Arial", 12), text_color="#4A90A4").pack(pady=(0, 20))

        saved = self._get_genre_tracker()

        main = CTkFrame(container, fg_color="transparent")
        main.pack(expand=True, fill="both")

        # Números laterales
        nums = CTkFrame(main, fg_color="transparent", width=35)
        nums.pack(side="left", fill="y", padx=(0, 10))
        for i in range(20):
            slot = CTkFrame(nums, width=35, height=24)
            slot.pack_propagate(False)
            slot.pack(pady=1)
            if i in (0, 5, 10, 15):
                num = 20 - i
                CTkLabel(slot, text=str(num), font=("Arial", 10, "bold"), text_color="#4A90A4").place(relx=0.5, rely=0.5, anchor="center")

        # Grid de géneros
        grid_frame = CTkFrame(main, fg_color="transparent")
        grid_frame.pack(side="left", fill="both", expand=True)

        for col_idx in range(len(GENRE_TRACKER_DATA)):
            grid_frame.grid_columnconfigure(col_idx, weight=1)

        for col_idx, gdata in enumerate(GENRE_TRACKER_DATA):
            col = self._build_genre_column(grid_frame, gdata, saved.get(gdata["key"], []))
            col.grid(row=0, column=col_idx, padx=4, pady=5, sticky="n")

    def _build_genre_column(self, parent, gdata, filled_indices):
        col = CTkFrame(parent, fg_color="transparent", width=70)
        col.grid_propagate(False)

        for i in range(20):
            is_filled = i in filled_indices
            sq = self._create_square(col, gdata["key"], i, gdata["color"], is_filled)
            sq.pack(pady=1)

        lbl = CTkLabel(col, text=gdata["name"], font=("Arial", 12, "bold"),
                       text_color=gdata["color"], wraplength=65, justify="center")
        lbl.pack(pady=(8, 0))

        return col

    def _create_square(self, parent, genre_key, index, color, is_filled):
        size = 24
        fg = color if is_filled else "#0B1B2B"
        border = color

        sq = CTkFrame(parent, width=size, height=size, corner_radius=2,
                      fg_color=fg, border_width=2, border_color=border)
        sq.pack_propagate(False)

        sq._genre_key = genre_key
        sq._index = index
        sq._color = color
        sq._filled = is_filled

        sq.bind("<Button-1>", lambda e, s=sq: self._on_square_click(s))
        sq.bind("<Button-3>", lambda e, s=sq: self._on_square_right_click(s, e))
        return sq

    def _on_square_click(self, sq):
        if sq._filled:
            return
        sq._filled = True
        sq.configure(fg_color=sq._color)

        saved = self._get_genre_tracker()
        if sq._genre_key not in saved:
            saved[sq._genre_key] = []
        if sq._index not in saved[sq._genre_key]:
            saved[sq._genre_key].append(sq._index)
            saved[sq._genre_key].sort()
        self._set_genre_tracker(saved)

    def _on_square_right_click(self, sq, event):
        if not sq._filled:
            return
        menu = tkinter.Menu(self.winfo_toplevel(), tearoff=0, bg="#162F4A", fg="#E0F7FA",
                            activebackground="#0D3B5C", activeforeground="#E0F7FA",
                            font=("Arial", 11))
        menu.add_command(label="🧼 Despintar", command=lambda: self._on_square_unpaint(sq))
        menu.add_separator()
        menu.add_command(label="Cancelar", command=menu.destroy)
        menu.post(event.x_root, event.y_root)

    def _on_square_unpaint(self, sq):
        if not sq._filled:
            return
        sq._filled = False
        sq.configure(fg_color="#0B1B2B")

        saved = self._get_genre_tracker()
        if sq._genre_key in saved and sq._index in saved[sq._genre_key]:
            saved[sq._genre_key].remove(sq._index)
            if not saved[sq._genre_key]:
                del saved[sq._genre_key]
        self._set_genre_tracker(saved)
    # ═══════════════════════════════════════════════════════════════
    #  30 DAY READING CHALLENGE
    # ═══════════════════════════════════════════════════════════════
    def _get_day30_data(self):
        ch = self._ensure_challenges()
        return ch.get("reading_30", [])

    def _set_day30_data(self, data):
        ch = self._ensure_challenges()
        ch["reading_30"] = data
        self.db.set("challenges", ch)

    def _validate_day30(self, filled):
        """Si no es consecutivo desde 1, devuelve lista vacía (reset)."""
        if not filled:
            return []
        filled_sorted = sorted(filled)
        expected = list(range(1, filled_sorted[-1] + 1))
        if filled_sorted == expected:
            return filled_sorted
        return []

    def show_day30(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_day30()
        self.day30_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_day30(self):
        for w in self.day30_scroll.winfo_children():
            w.destroy()

        self._day30_circles = {}
        self._day30_streak_label = None

        container = CTkFrame(self.day30_scroll, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        CTkLabel(container, text="🔥 30 Day Reading Challenge", font=("Helvetica", 26, "bold")).pack(pady=(0, 5))
        CTkLabel(container, text="Colorea los números consecutivamente. Si fallas la secuencia, ¡todo se reinicia!",
                 font=("Arial", 12), text_color="#4A90A4").pack(pady=(0, 20))

        saved = self._get_day30_data()
        saved = self._validate_day30(saved)
        filled_set = set(saved)

        grid = CTkFrame(container, fg_color="transparent")
        grid.pack(expand=True, fill="both")

        for c in range(READING_30_COLS):
            grid.grid_columnconfigure(c, weight=1)

        for idx, number in enumerate(READING_30_DATA):
            row = idx // READING_30_COLS
            col = idx % READING_30_COLS
            circ, lbl = self._build_day30_circle(grid, number, number in filled_set)
            circ.grid(row=row, column=col, padx=15, pady=15, sticky="n")
            self._day30_circles[number] = (circ, lbl)

        self._day30_streak_label = CTkLabel(container, text="", font=("Arial", 14, "bold"))
        self._day30_streak_label.pack(pady=(15, 0))
        self._update_day30_streak(saved)

    def _update_day30_streak(self, saved):
        if saved:
            self._day30_streak_label.configure(
                text=f"Racha actual: {len(saved)} / 30 días",
                text_color="#FF8A65"
            )
        else:
            self._day30_streak_label.configure(
                text="Haz clic en el 1 para empezar",
                text_color="#4A90A4"
            )

    def _build_day30_circle(self, parent, number, is_filled):
        size = 80
        fg = "#FF8A65" if is_filled else "#0B1B2B"
        border = "#FF8A65" if is_filled else "#4A90A4"

        circ = CTkFrame(parent, width=size, height=size, corner_radius=size // 2,
                      fg_color=fg, border_width=3, border_color=border)
        circ.grid_propagate(False)

        lbl = CTkLabel(circ, text=str(number), font=("Arial", 24, "bold"),
                       text_color="#E0F7FA" if is_filled else "#aaa")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        circ._number = number
        # Bind al frame y al label para mayor sensibilidad
        for widget in (circ, lbl):
            widget.bind("<Button-1>", lambda e, n=number: self._on_day30_click(n))
            widget.bind("<Button-3>", lambda e, n=number: self._on_day30_right_click(n, e))
            widget.configure(cursor="hand2")

        return circ, lbl

    def _paint_day30_circle(self, number, filled):
        if number not in self._day30_circles:
            return
        circ, lbl = self._day30_circles[number]
        if filled:
            circ.configure(fg_color="#FF8A65", border_color="#FF8A65")
            lbl.configure(text_color="#E0F7FA")
        else:
            circ.configure(fg_color="#0B1B2B", border_color="#4A90A4")
            lbl.configure(text_color="#aaa")

    def _on_day30_click(self, number):
        saved = self._get_day30_data()
        filled_set = set(saved)

        if number in filled_set:
            return

        filled_sorted = sorted(filled_set)
        # Regla: debe ser consecutivo desde 1
        if not filled_sorted:
            if number == 1:
                saved.append(1)
                self._set_day30_data(saved)
                self._paint_day30_circle(1, True)
                self._update_day30_streak(saved)
                return
            else:
                return
        else:
            last = filled_sorted[-1]
            if number == last + 1:
                saved.append(number)
                self._set_day30_data(saved)
                self._paint_day30_circle(number, True)
                self._update_day30_streak(saved)
                return
            else:
                # ¡Rota la secuencia! Resetear todo
                self._set_day30_data([])
                messagebox.showinfo("Reto fallido", "No seguiste la secuencia consecutiva.\nEl reto se ha reiniciado. ¡Vuelve a empezar!")
                self.render_day30()
                return

    def _on_day30_right_click(self, number, event):
        saved = self._get_day30_data()
        if number not in saved:
            return

        menu = tkinter.Menu(self.winfo_toplevel(), tearoff=0, bg="#162F4A", fg="#E0F7FA",
                            activebackground="#0D3B5C", activeforeground="#E0F7FA",
                            font=("Arial", 11))
        menu.add_command(label="🧼 Despintar", command=lambda: self._on_day30_unpaint(number))
        menu.add_separator()
        menu.add_command(label="Cancelar", command=menu.destroy)
        menu.post(event.x_root, event.y_root)

    def _on_day30_unpaint(self, number):
        saved = self._get_day30_data()
        if number in saved:
            saved.remove(number)
        validated = self._validate_day30(saved)
        self._set_day30_data(validated)

        if not validated:
            # Se rompió la secuencia al quitar → reset visual completo
            self.render_day30()
        else:
            # Sigue válido → solo despintar este círculo y actualizar contador
            self._paint_day30_circle(number, False)
            self._update_day30_streak(validated)

    # ═══════════════════════════════════════════════════════════════
    #  FORMULARIO
    # ═══════════════════════════════════════════════════════════════
    def _build_preview(self, img_path=None):
        """Destruye el preview anterior y crea uno nuevo limpio."""
        for w in self.cover_box.winfo_children():
            w.destroy()
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).resize((140, 190), Image.LANCZOS)
                if CTkImage:
                    ctk_img = CTkImage(light_image=img, dark_image=img, size=(140, 190))
                    self._form_preview_img = ctk_img
                    CTkLabel(self.cover_box, image=ctk_img, text="").place(relx=0.5, rely=0.5, anchor="center")
                    return
            except Exception:
                pass
        self._form_preview_img = None
        CTkLabel(self.cover_box, text="📕", font=("Arial", 48), text_color="#0D3B5C").place(relx=0.5, rely=0.5, anchor="center")

    def open_form(self, challenge_type, key):
        self._current_challenge_type = challenge_type
        self._current_challenge_key = key
        saved = self._get_saved(challenge_type, key)
        self.form_titulo.delete(0, "end")
        self.form_autor.delete(0, "end")
        self._form_foto_path = None
        self._form_preview_img = None
        foto = saved.get("foto") if saved else None
        self._build_preview(foto)
        if saved:
            self.form_titulo.insert(0, saved.get("titulo", ""))
            self.form_autor.insert(0, saved.get("autor", ""))
            if foto and os.path.exists(foto):
                self._form_foto_path = foto
        if challenge_type == "reto_lector":
            info = RETO_LECTOR_DATA.get(int(key), {})
            self.form_context_label.configure(
                text=f"📖 Libro favorito de {info.get('mes', '')}",
                text_color=info.get("color", "#aaa")
            )
        else:
            cinfo = next((c for c in COLLECT_COLORS_DATA if c["key"] == key), {})
            self.form_context_label.configure(
                text=f"Color: {cinfo.get('name', '')}  |  Busca una portada de este color",
                text_color=cinfo.get("color", "#aaa")
            )
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.form_panel.pack(fill="both", expand=True, padx=20, pady=15)

    def close_form(self):
        self.form_panel.pack_forget()
        if self._current_challenge_type == "reto_lector":
            self.reto_panel.pack(fill="both", expand=True, padx=10, pady=10)
            self.render_reto_lector()
        elif self._current_challenge_type == "collect_colors":
            self.collect_panel.pack(fill="both", expand=True, padx=10, pady=10)
            self.render_collect_colors()
        else:
            self.show_folders()

    def save_form(self):
        titulo = self.form_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Campo requerido", "El título es obligatorio.")
            return
        data = {
            "titulo": titulo,
            "autor": self.form_autor.get().strip(),
            "foto": self._form_foto_path or None
        }
        self._set_saved(self._current_challenge_type, self._current_challenge_key, data)
        self._cover_cache.clear()
        messagebox.showinfo("Éxito", "Reto guardado correctamente.")
        self.close_form()

    # ═══════════════════════════════════════════════════════════════
    #  ALPHABET READING CHALLENGE
    # ═══════════════════════════════════════════════════════════════
    def _get_alpha_data(self):
        ch = self._ensure_challenges()
        return ch.get("alphabet", {})

    def _set_alpha_data(self, data):
        ch = self._ensure_challenges()
        ch["alphabet"] = data
        self.db.set("challenges", ch)

    def show_alpha(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.day30_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_alpha()
        self.alpha_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_alpha(self):
        for w in self.alpha_scroll.winfo_children():
            w.destroy()

        container = CTkFrame(self.alpha_scroll, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        CTkLabel(container, text="🔤 Alphabet Reading Challenge", font=("Helvetica", 26, "bold")).pack(pady=(0, 5))
        CTkLabel(container, text="Escribe un libro y autor para cada letra del abecedario",
                 font=("Arial", 12), text_color="#4A90A4").pack(pady=(0, 25))

        saved = self._get_alpha_data()

        main = CTkFrame(container, fg_color="transparent")
        main.pack(expand=True, fill="both")
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_columnconfigure(2, weight=0)

        # Dividir en dos columnas: A-M (13) y N-Z (13)
        left_col = CTkFrame(main, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        right_col = CTkFrame(main, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        for idx, letter in enumerate(ALPHABET_LETTERS):
            is_left = idx < 13
            parent = left_col if is_left else right_col
            data = saved.get(letter, {"titulo": "", "autor": ""})
            self._build_alpha_row(parent, letter, data)

    def _build_alpha_row(self, parent, letter, data):
        is_saved = bool(data.get("titulo") and data.get("autor")) and (self._alpha_editing != letter)

        # Fondo distintivo para guardados
        row_bg = "#1a2a1a" if is_saved else "transparent"
        row = CTkFrame(parent, fg_color=row_bg, height=62, corner_radius=10)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        # Letra
        badge_color = "#4DD0E1" if is_saved else "#162F4A"
        border_color = "#4DD0E1" if is_saved else "#1E5F8E"
        badge = CTkFrame(row, width=42, height=42, corner_radius=8,
                         fg_color=badge_color, border_width=2, border_color=border_color)
        badge.pack(side="left", padx=(10, 12))
        badge.pack_propagate(False)
        CTkLabel(badge, text=letter, font=("Helvetica", 18, "bold"),
                 text_color="#E0F7FA" if is_saved else "#E67E22").place(relx=0.5, rely=0.5, anchor="center")

        # Campos
        fields = CTkFrame(row, fg_color="transparent")
        fields.pack(side="left", fill="both", expand=True, pady=4)

        if is_saved:
            # Modo solo lectura con estética de tarjeta guardada
            CTkLabel(fields, text=data.get("titulo", ""), font=("Arial", 13, "bold"),
                     text_color="#E0F7FA").pack(anchor="w")
            CTkLabel(fields, text=data.get("autor", ""), font=("Arial", 12),
                     text_color="#bbb").pack(anchor="w")

            # Botón editar
            btn_edit = CTkButton(row, text="✏️", width=36, height=36, corner_radius=8,
                               fg_color="#1E5F8E", hover_color="#0D3B5C",
                               command=lambda l=letter: self._on_alpha_edit(l))
            btn_edit.pack(side="right", padx=(8, 10))
        else:
            # Modo edición
            titulo = CTkEntry(fields, placeholder_text="Título del libro...", height=30,
                              corner_radius=6, font=("Arial", 13))
            titulo.pack(fill="x", pady=(1, 2))
            if data.get("titulo"):
                titulo.insert(0, data["titulo"])

            autor = CTkEntry(fields, placeholder_text="Autor...", height=30,
                             corner_radius=6, font=("Arial", 12), text_color="#81D4FA")
            autor.pack(fill="x", pady=(0, 1))
            if data.get("autor"):
                autor.insert(0, data["autor"])

            # Guardar: Tab entre campos o Enter en el segundo campo
            def on_titulo_tab(event, a=autor):
                a.focus_set()
                return "break"

            def on_autor_tab(event, l=letter, t=titulo, a=autor):
                self._try_alpha_save(l, t, a)
                return "break"

            def on_return(event, l=letter, t=titulo, a=autor):
                self._try_alpha_save(l, t, a)
                return "break"

            titulo.bind("<Tab>", on_titulo_tab)
            autor.bind("<Tab>", on_autor_tab)
            titulo.bind("<Return>", lambda e, a=autor: (a.focus_set(), "break")[1])
            autor.bind("<Return>", on_return)

    def _try_alpha_save(self, letter, titulo_widget, autor_widget):
        titulo = titulo_widget.get().strip()
        autor = autor_widget.get().strip()
        if titulo and autor:
            saved = self._get_alpha_data()
            saved[letter] = {"titulo": titulo, "autor": autor}
            self._set_alpha_data(saved)
            self._alpha_editing = None
            self.render_alpha()

    def _on_alpha_edit(self, letter):
        self._alpha_editing = letter
        self.render_alpha()

    # ═══════════════════════════════════════════════════════════════
    #  BOOKISH BINGO CHALLENGE
    # ═══════════════════════════════════════════════════════════════
    def _get_bingo_data(self):
        ch = self._ensure_challenges()
        return ch.get("bingo", [])

    def _set_bingo_data(self, data):
        ch = self._ensure_challenges()
        ch["bingo"] = data
        self.db.set("challenges", ch)

    def show_bingo(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.day30_panel.pack_forget()
        self.alpha_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_bingo()
        self.bingo_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_bingo(self):
        for w in self.bingo_scroll.winfo_children():
            w.destroy()

        container = CTkFrame(self.bingo_scroll, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        CTkLabel(container, text="🎀 Bookish Bingo", font=("Helvetica", 26, "bold")).pack(pady=(0, 5))
        CTkLabel(container, text="Haz clic en una casilla para marcarla como cumplida · Clic derecho para desmarcar",
                 font=("Arial", 12), text_color="#4A90A4").pack(pady=(0, 20))

        saved = set(self._get_bingo_data())

        grid = CTkFrame(container, fg_color="transparent")
        grid.pack(expand=True, fill="both")

        for c in range(5):
            grid.grid_columnconfigure(c, weight=1)

        self._bingo_cells = {}

        for idx, text in enumerate(BINGO_DATA):
            row = idx // 5
            col = idx % 5
            cell = self._build_bingo_cell(grid, idx, text, idx in saved)
            cell.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self._bingo_cells[idx] = cell

    def _build_bingo_cell(self, parent, index, text, is_done):
        bg_color = "#E8B4B8" if is_done else "#112240"
        border_color = "#D4A5A9" if is_done else "#1E5F8E"
        text_color = "#4a2c2f" if is_done else "#81D4FA"

        cell = CTkFrame(parent, width=170, height=170, corner_radius=16,
                        fg_color=bg_color, border_width=3, border_color=border_color)
        cell.grid_propagate(False)
        cell._index = index
        cell._done = is_done

        # Texto normal con wrap
        lbl = CTkLabel(cell, text=text, font=("Arial", 13 if is_done else 12, "bold" if is_done else "normal"),
                       text_color=text_color, wraplength=150, justify="center")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Checkmark si está hecho
        if is_done:
            check_bg = CTkFrame(cell, width=28, height=28, corner_radius=14,
                                fg_color="#4DD0E1", border_width=0)
            check_bg.place(relx=0.88, rely=0.12, anchor="center")
            CTkLabel(check_bg, text="OK", font=("Arial", 10, "bold"), text_color="#E0F7FA").place(relx=0.5, rely=0.5, anchor="center")

        # Bind clicks al frame y labels
        for widget in cell.winfo_children():
            widget.bind("<Button-1>", lambda e, i=index: self._on_bingo_click(i))
            widget.bind("<Button-3>", lambda e, i=index: self._on_bingo_right_click(i, e))
            widget.configure(cursor="hand2")
        cell.bind("<Button-1>", lambda e, i=index: self._on_bingo_click(i))
        cell.bind("<Button-3>", lambda e, i=index: self._on_bingo_right_click(i, e))
        cell.configure(cursor="hand2")

        return cell

    def _on_bingo_click(self, index):
        if self._bingo_cells[index]._done:
            return
        saved = list(self._get_bingo_data())
        if index not in saved:
            saved.append(index)
        self._set_bingo_data(saved)
        self._update_bingo_cell(index, True)

    def _on_bingo_right_click(self, index, event):
        if not self._bingo_cells[index]._done:
            return
        menu = tkinter.Menu(self.winfo_toplevel(), tearoff=0, bg="#162F4A", fg="#E0F7FA",
                            activebackground="#0D3B5C", activeforeground="#E0F7FA",
                            font=("Arial", 11))
        menu.add_command(label="Desmarcar", command=lambda: self._on_bingo_uncheck(index, menu))
        menu.add_separator()
        menu.add_command(label="Cancelar", command=menu.destroy)
        menu.post(event.x_root, event.y_root)

    def _on_bingo_uncheck(self, index, menu=None):
        if menu:
            menu.destroy()
        saved = list(self._get_bingo_data())
        if index in saved:
            saved.remove(index)
        self._set_bingo_data(saved)
        self._update_bingo_cell(index, False)

    def _update_bingo_cell(self, index, is_done):
        cell = self._bingo_cells.get(index)
        if not cell:
            return
        cell._done = is_done

        bg_color = "#E8B4B8" if is_done else "#112240"
        border_color = "#D4A5A9" if is_done else "#1E5F8E"
        text_color = "#4a2c2f" if is_done else "#81D4FA"

        cell.configure(fg_color=bg_color, border_color=border_color)

        # Hide all existing children instead of destroying (avoids TclError)
        for w in cell.winfo_children():
            w.place_forget()
            w.pack_forget()
            w.grid_forget()

        text = BINGO_DATA[index]
        lbl = CTkLabel(cell, text=text, font=("Arial", 13 if is_done else 12, "bold" if is_done else "normal"),
                       text_color=text_color, wraplength=150, justify="center")
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        if is_done:
            check_bg = CTkFrame(cell, width=28, height=28, corner_radius=14,
                                fg_color="#4DD0E1", border_width=0)
            check_bg.place(relx=0.88, rely=0.12, anchor="center")
            CTkLabel(check_bg, text="OK", font=("Arial", 10, "bold"), text_color="#E0F7FA").place(relx=0.5, rely=0.5, anchor="center")

        for widget in cell.winfo_children():
            widget.bind("<Button-1>", lambda e, i=index: self._on_bingo_click(i))
            widget.bind("<Button-3>", lambda e, i=index: self._on_bingo_right_click(i, e))
            widget.configure(cursor="hand2")
        cell.bind("<Button-1>", lambda e, i=index: self._on_bingo_click(i))
        cell.bind("<Button-3>", lambda e, i=index: self._on_bingo_right_click(i, e))
        cell.configure(cursor="hand2")

    # ═══════════════════════════════════════════════════════════════
    #  YEARLY READING CHALLENGE
    # ═══════════════════════════════════════════════════════════════
    def _get_yearly_data(self):
        ch = self._ensure_challenges()
        return ch.get("yearly", {})

    def _set_yearly_data(self, data):
        ch = self._ensure_challenges()
        ch["yearly"] = data
        self.db.set("challenges", ch)

    def show_yearly(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.day30_panel.pack_forget()
        self.alpha_panel.pack_forget()
        self.bingo_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_yearly()
        self.yearly_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_yearly(self):
        for w in self.yearly_scroll.winfo_children():
            w.destroy()

        container = CTkFrame(self.yearly_scroll, fg_color="transparent")
        container.pack(expand=True, fill="both")

        saved = self._get_yearly_data()

        main = CTkFrame(container, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_columnconfigure(2, weight=0)

        # --- COLUMNA IZQUIERDA: Lista de retos 1-16 ---
        left_col = CTkFrame(main, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        for idx in range(16):
            num = idx + 1
            text = YEARLY_DATA[idx]
            has_cover = str(num) in saved and saved[str(num)].get("foto")
            self._build_yearly_list_row(left_col, num, text, has_cover)

        # --- COLUMNA CENTRO: Lista de retos 17-31 ---
        mid_col = CTkFrame(main, fg_color="transparent")
        mid_col.grid(row=0, column=1, sticky="nsew", padx=(15, 15))

        for idx in range(16, 31):
            num = idx + 1
            text = YEARLY_DATA[idx]
            has_cover = str(num) in saved and saved[str(num)].get("foto")
            self._build_yearly_list_row(mid_col, num, text, has_cover)

        # --- COLUMNA DERECHA: Grid de números ---
        right_col = CTkFrame(main, fg_color="transparent")
        right_col.grid(row=0, column=2, sticky="nsew", padx=(15, 0))

        # Grid 7x5 de números
        grid_frame = CTkFrame(right_col, fg_color="transparent")
        grid_frame.pack(expand=True, fill="both")

        for c in range(5):
            grid_frame.grid_columnconfigure(c, weight=1)

        for idx in range(31):
            row = idx // 5
            col = idx % 5
            num = idx + 1
            has_cover = str(num) in saved and saved[str(num)].get("foto")
            cell = self._build_yearly_number_cell(grid_frame, num, has_cover)
            cell.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

    def _build_yearly_list_row(self, parent, num, text, has_cover):
        row = CTkFrame(parent, fg_color="transparent", height=38)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)

        # Número
        num_lbl = CTkLabel(row, text=f"{num}.", font=("Arial", 13, "bold"),
                           text_color="#8b7355" if not has_cover else "#a08060",
                           width=32)
        num_lbl.pack(side="left", padx=(0, 8))

        # Texto con línea de tachado sutil si tiene portada
        if has_cover:
            text_lbl = CTkLabel(row, text=text, font=("Arial", 13),
                                text_color="#a09080", wraplength=280, justify="left")
            text_lbl.pack(side="left", fill="x", expand=True)
            # Línea de tachado
            strike = CTkFrame(row, height=1, fg_color="#b0a090")
            strike.place(relx=0.10, rely=0.55, relwidth=0.86)
        else:
            text_lbl = CTkLabel(row, text=text, font=("Arial", 13),
                                text_color="#5c4a3a", wraplength=280, justify="left")
            text_lbl.pack(side="left", fill="x", expand=True)

    def _build_yearly_number_cell(self, parent, num, has_cover):
        w, h = 72, 96  # Rectangular vertical para portadas de libros
        bg = "#d4c4a8" if has_cover else "#e8dcc8"
        border = "#b0a080" if has_cover else "#c8b8a0"

        cell = CTkFrame(parent, width=w, height=h, corner_radius=2,
                        fg_color=bg, border_width=2, border_color=border)
        cell.grid_propagate(False)
        cell._num = num
        cell._has_cover = has_cover

        if has_cover:
            # Mostrar portada en vez de número
            img = self._load_yearly_cover(num)
            if img:
                CTkLabel(cell, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
            else:
                CTkLabel(cell, text=str(num), font=("Helvetica", 18, "bold"),
                         text_color="#8b7355").place(relx=0.5, rely=0.5, anchor="center")
        else:
            CTkLabel(cell, text=str(num), font=("Helvetica", 22, "bold"),
                     text_color="#5c4a3a").place(relx=0.5, rely=0.5, anchor="center")

        # Click para cargar portada
        cell.bind("<Button-1>", lambda e, n=num: self._on_yearly_click(n))
        for w in cell.winfo_children():
            w.bind("<Button-1>", lambda e, n=num: self._on_yearly_click(n))
        cell.configure(cursor="hand2")

        return cell

    def _load_yearly_cover(self, num):
        saved = self._get_yearly_data()
        data = saved.get(str(num), {})
        path = data.get("foto")
        if not path or not os.path.exists(path):
            return None
        cache_key = (path, (60, 84))
        if cache_key in self._cover_cache:
            return self._cover_cache[cache_key]
        try:
            img = Image.open(path).resize((60, 84), Image.LANCZOS)
            if CTkImage:
                ctk_img = CTkImage(light_image=img, dark_image=img, size=(60, 84))
                self._cover_cache[cache_key] = ctk_img
                return ctk_img
        except Exception:
            pass
        return None

    def _on_yearly_click(self, num):
        path = filedialog.askopenfilename(
            title=f"Seleccionar portada para el reto #{num}",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            saved = self._get_yearly_data()
            saved[str(num)] = {"foto": path}
            self._set_yearly_data(saved)
            self._cover_cache.clear()
            self.render_yearly()

    def refresh(self):
        self._cover_cache.clear()
        self.show_folders()
        self.build_folders()
        self.render_reto_lector()
        self.render_collect_colors()
        self.render_bracket()
        self.render_day30()
        self.render_alpha()
        self.render_bingo()
        self.render_yearly()