"""Challenges - Retos literarios con estética de carpetas."""
import os
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
    1:  {"mes": "ENERO",      "reto": "Un libro de un autor que no hayas leído antes",                          "color": "#AED6F1"},
    2:  {"mes": "FEBRERO",    "reto": "Un libro que sea parte de una saga que ya empezaste",                  "color": "#F5B7B1"},
    3:  {"mes": "MARZO",      "reto": "Un libro de romance",                                                    "color": "#F9E79F"},
    4:  {"mes": "ABRIL",      "reto": "Un libro que hable de libros",                                           "color": "#F5B7B1"},
    5:  {"mes": "MAYO",       "reto": "Un clásico literario",                                                   "color": "#D4EFDF"},
    6:  {"mes": "JUNIO",      "reto": "Un libro de menos de 100 páginas",                                       "color": "#AED6F1"},
    7:  {"mes": "JULIO",      "reto": "Un libro que tengas en tu librero más de 2 años y que no hayas leído",   "color": "#FADBD8"},
    8:  {"mes": "AGOSTO",     "reto": "Un libro basado en una historia real",                                   "color": "#FCF3CF"},
    9:  {"mes": "SEPTIEMBRE", "reto": "Un libro de un premio novel",                                            "color": "#E8DAEF"},
    10: {"mes": "OCTUBRE",    "reto": "Un libro de 300 páginas",                                                "color": "#D5F5E3"},
    11: {"mes": "NOVIEMBRE",  "reto": "Un libro de poesía",                                                     "color": "#D6EAF8"},
    12: {"mes": "DICIEMBRE",  "reto": "Un libro recomendado por un amigo",                                      "color": "#FADBD8"},
}

COLLECT_COLORS_DATA = [
    {"key": "red",        "name": "Red",        "color": "#E74C3C", "bg": "#FDEDEC"},
    {"key": "orange",     "name": "Orange",     "color": "#E67E22", "bg": "#FEF5E7"},
    {"key": "yellow",     "name": "Yellow",     "color": "#F1C40F", "bg": "#FCF3CF"},
    {"key": "green",      "name": "Green",      "color": "#27AE60", "bg": "#EAFAF1"},
    {"key": "light_blue", "name": "Light Blue", "color": "#5DADE2", "bg": "#EBF5FB"},
    {"key": "blue",       "name": "Blue",       "color": "#2980B9", "bg": "#D6EAF8"},
    {"key": "purple",     "name": "Purple",     "color": "#8E44AD", "bg": "#F4ECF7"},
    {"key": "pink",       "name": "Pink",       "color": "#FF69B4", "bg": "#FDEBF7"},
    {"key": "brown",      "name": "Brown",      "color": "#8B4513", "bg": "#F6ECE1"},
    {"key": "black",      "name": "Black",      "color": "#2C3E50", "bg": "#EAECEE"},
    {"key": "grey",       "name": "Grey",       "color": "#7F8C8D", "bg": "#F2F4F4"},
    {"key": "white",      "name": "White",      "color": "#BDC3C7", "bg": "#FBFCFC"},
]


# ═══════════════════════════════════════════════════════════════════
#  BRACKET DATA — VERTICAL (estructura clásica de torneo)
#  Basado en la foto de inspiración
# ═══════════════════════════════════════════════════════════════════
SLOT_W, SLOT_H = 75, 100
BEST_W, BEST_H = 140, 180

# Coordenadas según la estructura de la foto
# Izquierda: 3 columnas de slots, derecha: 3 columnas de slots
# Centro: Best book grande

# Columnas X
X_LEFT_3 = 80    # meses arriba izq (Jan, Feb, Mar)
X_LEFT_2 = 200   # round 2 izq
X_LEFT_1 = 320   # round 3 izq / semifinal izq
X_CENTER = 480   # final / best book
X_RIGHT_1 = 700  # semifinal der / round 3 der
X_RIGHT_2 = 820  # round 2 der
X_RIGHT_3 = 940  # meses arriba der (Apr, May, Jun)

# Meses abajo izq: Jul, Aug, Sep
X_LEFT_3B = 80
# Meses abajo der: Oct, Nov, Dec
X_RIGHT_3B = 940

# Filas Y
Y_TOP = 40       # meses arriba
Y_R2_TOP = 180   # round 2 arriba
Y_R3_TOP = 300   # round 3 arriba
Y_SEMI = 420     # semifinales
Y_FINAL = 420    # final (misma altura que semis)
Y_BEST = 380     # best book (centrado verticalmente)
Y_R3_BOT = 540   # round 3 abajo
Y_R2_BOT = 660   # round 2 abajo
Y_BOT = 780      # meses abajo

BRACKET_SLOTS = [
    # ── Top left: Jan, Feb, Mar ──
    {"id": "jan", "label": "Jan", "x": X_LEFT_3, "y": Y_TOP, "w": SLOT_W, "h": SLOT_H},
    {"id": "feb", "label": "Feb", "x": X_LEFT_3 + 110, "y": Y_TOP, "w": SLOT_W, "h": SLOT_H},
    {"id": "mar", "label": "Mar", "x": X_LEFT_3 + 220, "y": Y_TOP, "w": SLOT_W, "h": SLOT_H},
    # ── Top left round 2 ──
    {"id": "r2_tl", "label": "", "x": X_LEFT_3 + 55, "y": Y_R2_TOP, "w": SLOT_W, "h": SLOT_H},
    {"id": "r2_tr", "label": "", "x": X_LEFT_3 + 165, "y": Y_R2_TOP, "w": SLOT_W, "h": SLOT_H},
    # ── Top left round 3 ──
    {"id": "r3_t", "label": "", "x": X_LEFT_3 + 110, "y": Y_R3_TOP, "w": SLOT_W, "h": SLOT_H},
    # ── Left semifinal ──
    {"id": "semi_l", "label": "", "x": X_LEFT_1, "y": Y_SEMI, "w": SLOT_W, "h": SLOT_H},

    # ── Center: Best book (grande) ──
    {"id": "best", "label": "Best book\nof the year", "x": X_CENTER, "y": Y_BEST, "w": BEST_W, "h": BEST_H},
    # ── Final ──
    {"id": "final", "label": "", "x": X_CENTER + 25, "y": Y_FINAL, "w": SLOT_W, "h": SLOT_H},

    # ── Right semifinal ──
    {"id": "semi_r", "label": "", "x": X_RIGHT_1, "y": Y_SEMI, "w": SLOT_W, "h": SLOT_H},
    # ── Top right round 3 ──
    {"id": "r3_rt", "label": "", "x": X_RIGHT_3 - 110, "y": Y_R3_TOP, "w": SLOT_W, "h": SLOT_H},
    # ── Top right round 2 ──
    {"id": "r2_rtl", "label": "", "x": X_RIGHT_3 - 165, "y": Y_R2_TOP, "w": SLOT_W, "h": SLOT_H},
    {"id": "r2_rtr", "label": "", "x": X_RIGHT_3 - 55, "y": Y_R2_TOP, "w": SLOT_W, "h": SLOT_H},
    # ── Top right: Apr, May, Jun ──
    {"id": "apr", "label": "Apr", "x": X_RIGHT_3 - 220, "y": Y_TOP, "w": SLOT_W, "h": SLOT_H},
    {"id": "may", "label": "May", "x": X_RIGHT_3 - 110, "y": Y_TOP, "w": SLOT_W, "h": SLOT_H},
    {"id": "jun", "label": "Jun", "x": X_RIGHT_3, "y": Y_TOP, "w": SLOT_W, "h": SLOT_H},

    # ── Bottom left: Jul, Aug, Sep ──
    {"id": "jul", "label": "Jul", "x": X_LEFT_3B, "y": Y_BOT, "w": SLOT_W, "h": SLOT_H},
    {"id": "aug", "label": "Aug", "x": X_LEFT_3B + 110, "y": Y_BOT, "w": SLOT_W, "h": SLOT_H},
    {"id": "sep", "label": "Sep", "x": X_LEFT_3B + 220, "y": Y_BOT, "w": SLOT_W, "h": SLOT_H},
    # ── Bottom left round 2 ──
    {"id": "r2_bl", "label": "", "x": X_LEFT_3B + 55, "y": Y_R2_BOT, "w": SLOT_W, "h": SLOT_H},
    {"id": "r2_br", "label": "", "x": X_LEFT_3B + 165, "y": Y_R2_BOT, "w": SLOT_W, "h": SLOT_H},
    # ── Bottom left round 3 ──
    {"id": "r3_b", "label": "", "x": X_LEFT_3B + 110, "y": Y_R3_BOT, "w": SLOT_W, "h": SLOT_H},

    # ── Bottom right: Oct, Nov, Dec ──
    {"id": "oct", "label": "Oct", "x": X_RIGHT_3B - 220, "y": Y_BOT, "w": SLOT_W, "h": SLOT_H},
    {"id": "nov", "label": "Nov", "x": X_RIGHT_3B - 110, "y": Y_BOT, "w": SLOT_W, "h": SLOT_H},
    {"id": "dec", "label": "Dec", "x": X_RIGHT_3B, "y": Y_BOT, "w": SLOT_W, "h": SLOT_H},
    # ── Bottom right round 2 ──
    {"id": "r2_bbl", "label": "", "x": X_RIGHT_3B - 165, "y": Y_R2_BOT, "w": SLOT_W, "h": SLOT_H},
    {"id": "r2_bbr", "label": "", "x": X_RIGHT_3B - 55, "y": Y_R2_BOT, "w": SLOT_W, "h": SLOT_H},
    # ── Bottom right round 3 ──
    {"id": "r3_rb", "label": "", "x": X_RIGHT_3B - 110, "y": Y_R3_BOT, "w": SLOT_W, "h": SLOT_H},
]

# Conexiones según la estructura de la foto
BRACKET_CONNECTIONS = [
    # Top left side
    ("jan", "r2_tl"), ("feb", "r2_tl"),
    ("feb", "r2_tr"), ("mar", "r2_tr"),
    ("r2_tl", "r3_t"), ("r2_tr", "r3_t"),
    ("r3_t", "semi_l"),
    # Bottom left side
    ("jul", "r2_bl"), ("aug", "r2_bl"),
    ("aug", "r2_br"), ("sep", "r2_br"),
    ("r2_bl", "r3_b"), ("r2_br", "r3_b"),
    ("r3_b", "semi_l"),
    # Left to center
    ("semi_l", "final"),
    # Top right side
    ("apr", "r2_rtl"), ("may", "r2_rtl"),
    ("may", "r2_rtr"), ("jun", "r2_rtr"),
    ("r2_rtl", "r3_rt"), ("r2_rtr", "r3_rt"),
    ("r3_rt", "semi_r"),
    # Bottom right side
    ("oct", "r2_bbl"), ("nov", "r2_bbl"),
    ("nov", "r2_bbr"), ("dec", "r2_bbr"),
    ("r2_bbl", "r3_rb"), ("r2_bbr", "r3_rb"),
    ("r3_rb", "semi_r"),
    # Right to center
    ("semi_r", "final"),
    # Final to best
    ("final", "best"),
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
            CTkLabel(self.body, text=subtitle, font=("Arial", 10), text_color="#555").pack(pady=(2, 0))

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
        CTkLabel(h3, text="🏆 Favorite Book of the Year", font=("Helvetica", 24, "bold")).pack(side="left", padx=15)

        # Scroll VERTICAL para el bracket (estructura vertical)
        self.bracket_scroll = CTkScrollableFrame(self.bracket_panel, width=900, height=650,
                                                  fg_color="transparent")
        self.bracket_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.bracket_canvas = self.bracket_scroll._parent_canvas
        self.bracket_canvas.configure(bg="#1a1a1a", highlightthickness=0)

        # ── Formulario (reutilizable) ──
        self.form_panel = CTkFrame(self, fg_color="#1e1e1e", corner_radius=16,
                                   border_width=2, border_color="#3a3a3a")
        CTkLabel(self.form_panel, text="📝 Completar Reto", font=("Helvetica", 22, "bold")).pack(pady=(18, 12))
        self.form_scroll = CTkScrollableFrame(self.form_panel, width=800, height=500, fg_color="transparent")
        self.form_scroll.pack(padx=25, pady=5, fill="both", expand=True)

        cover_box = CTkFrame(self.form_scroll, width=160, height=200, corner_radius=10,
                             fg_color="#2b2b2b", border_width=2, border_color="#444")
        cover_box.pack(pady=(0, 10))
        cover_box.pack_propagate(False)
        self.form_preview = CTkLabel(cover_box, text="", width=160, height=200)
        self.form_preview.place(relx=0.5, rely=0.5, anchor="center")
        CTkButton(self.form_scroll, text="📁 Examinar portada", width=160, height=34,
                  command=self.browse_form_photo).pack(pady=(0, 15))

        def form_row(label, attr_name, width=600):
            CTkLabel(self.form_scroll, text=label, font=("Arial", 11, "bold"), text_color="#888").pack(anchor="w", pady=(0, 2))
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
                  fg_color="#555", hover_color="#666").pack(side="left", padx=8)

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
            try:
                img = Image.open(path).resize((140, 190), Image.LANCZOS)
                if CTkImage:
                    self._form_preview_img = CTkImage(light_image=img, dark_image=img, size=(140, 190))
                    self.form_preview.configure(image=self._form_preview_img, text="")
            except Exception:
                self._form_preview_img = None

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

        f3 = FolderCard(container, title="Favorite Book of the Year",
                        subtitle="Bracket 2026 · Solo portadas",
                        icon="🏆", color="#FADBD8",
                        command=self.show_bracket)
        f3.grid(row=0, column=3, padx=15, pady=20)

    def show_folders(self):
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.bracket_panel.pack_forget()
        self.form_panel.pack_forget()
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
                        border_width=2, border_color=color, fg_color="#252525")
        card.grid_propagate(False)
        hdr = CTkFrame(card, fg_color=color, corner_radius=14, height=38)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)
        CTkLabel(hdr, text=info["mes"], font=("Helvetica", 14, "bold"),
                 text_color="#2c3e50").place(relx=0.5, rely=0.5, anchor="center")
        CTkLabel(card, text=info["reto"], font=("Arial", 11), text_color="#ccc",
                 wraplength=250, justify="center").pack(pady=(10, 8), padx=10)
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
                     text_color="#888", wraplength=250).pack()
        else:
            CTkLabel(content, text="Pendiente", font=("Arial", 12),
                     text_color="#666").place(relx=0.5, rely=0.4, anchor="center")
            CTkButton(content, text="➕ Añadir libro", width=140, height=30,
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
                        border_width=2, border_color=color, fg_color="#252525")
        card.grid_propagate(False)
        hdr = CTkFrame(card, fg_color=color, corner_radius=14, height=32)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)
        CTkLabel(hdr, text=cdata["name"], font=("Helvetica", 13, "bold"),
                 text_color="white" if cdata["key"] in ("black", "blue", "purple", "brown") else "#2c3e50"
                 ).place(relx=0.5, rely=0.5, anchor="center")
        slot = CTkFrame(card, width=120, height=160, corner_radius=10,
                        border_width=4, border_color=color, fg_color="#1e1e1e")
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
                     text_color="#888", wraplength=180).pack()
        else:
            CTkLabel(slot, text="📕", font=("Arial", 40), text_color="#444").place(relx=0.5, rely=0.5, anchor="center")
            CTkButton(card, text="➕ Añadir", width=120, height=28,
                      command=lambda k=cdata["key"]: self.open_form("collect_colors", k)).pack(pady=(8, 0))
        if saved:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e, k=cdata["key"]: self.open_form("collect_colors", k))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, k=cdata["key"]: self.open_form("collect_colors", k))
        return card

    # ═══════════════════════════════════════════════════════════════
    #  BRACKET — VERTICAL (estructura clásica de torneo)
    # ═══════════════════════════════════════════════════════════════
    def show_bracket(self):
        self.folders_panel.pack_forget()
        self.reto_panel.pack_forget()
        self.collect_panel.pack_forget()
        self.form_panel.pack_forget()
        self.render_bracket()
        self.bracket_panel.pack(fill="both", expand=True, padx=10, pady=10)

    def render_bracket(self):
        canvas = self.bracket_canvas
        canvas.delete("all")
        canvas.configure(bg="#1a1a1a")
        # Scroll vertical: ancho fijo, alto total del bracket
        canvas.configure(scrollregion=(0, 0, 1100, 950))

        # Dibujar conexiones (líneas con flechas)
        for src_id, dst_id in BRACKET_CONNECTIONS:
            src = next((s for s in BRACKET_SLOTS if s["id"] == src_id), None)
            dst = next((s for s in BRACKET_SLOTS if s["id"] == dst_id), None)
            if not src or not dst:
                continue

            # Punto de salida: centro del borde derecho/izquierdo del src
            # Punto de entrada: centro del borde izquierdo/derecho del dst
            if src["x"] < dst["x"]:
                # Src está a la izquierda de dst
                x1 = src["x"] + src["w"]
                y1 = src["y"] + src["h"] / 2
                x2 = dst["x"]
                y2 = dst["y"] + dst["h"] / 2
            else:
                # Src está a la derecha de dst (conexión inversa)
                x1 = src["x"]
                y1 = src["y"] + src["h"] / 2
                x2 = dst["x"] + dst["w"]
                y2 = dst["y"] + dst["h"] / 2

            canvas.create_line(x1, y1, x2, y2, fill="white", width=1.5, dash=(3, 3))
            # Flecha
            canvas.create_polygon(
                x2 - 5, y2 - 3,
                x2 - 5, y2 + 3,
                x2, y2,
                fill="white"
            )

        # Slots
        for slot in BRACKET_SLOTS:
            self._build_bracket_slot(canvas, slot)

    def _build_bracket_slot(self, canvas, slot_def):
        sid = slot_def["id"]
        w, h = slot_def["w"], slot_def["h"]
        saved = self._get_saved("bracket", sid)

        # Contenedor: slot + espacio para label
        container_h = h + 22
        container = CTkFrame(canvas, width=w, height=container_h, fg_color="transparent")

        border_w = 3 if sid == "best" else 2
        slot_frame = CTkFrame(container, width=w, height=h, corner_radius=4,
                              fg_color="#252525", border_width=border_w, border_color="white")
        slot_frame.place(x=0, y=18)
        slot_frame.pack_propagate(False)

        # Label del mes (dentro del contenedor, arriba del slot)
        label = slot_def.get("label", "")
        if label:
            lbl = CTkLabel(container, text=label, font=("Arial", 10, "bold"), text_color="white")
            lbl.place(x=w/2, y=2, anchor="n")

        # Portada o placeholder
        inner_w, inner_h = w - 8, h - 8
        if saved and saved.get("foto"):
            img = self._load_cover(saved["foto"], size=(inner_w, inner_h))
            if img:
                CTkLabel(slot_frame, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
            else:
                CTkLabel(slot_frame, text="📕", font=("Arial", 18)).place(relx=0.5, rely=0.5, anchor="center")
        else:
            sym = "♡" if sid == "best" else "+"
            size = 18 if sid == "best" else 14
            CTkLabel(slot_frame, text=sym, font=("Arial", size), text_color="#888").place(relx=0.5, rely=0.5, anchor="center")

        # Click para cargar portada
        slot_frame.configure(cursor="hand2")
        slot_frame.bind("<Button-1>", lambda e, s=sid: self.load_bracket_photo(s))
        for child in slot_frame.winfo_children():
            child.bind("<Button-1>", lambda e, s=sid: self.load_bracket_photo(s))
            child.configure(cursor="hand2")

        canvas.create_window(slot_def["x"], slot_def["y"], window=container, anchor="nw")

    def load_bracket_photo(self, slot_id):
        path = filedialog.askopenfilename(
            title="Seleccionar portada",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            self._set_saved("bracket", slot_id, {"foto": path})
            self._cover_cache.clear()
            self.render_bracket()

    # ═══════════════════════════════════════════════════════════════
    #  FORMULARIO
    # ═══════════════════════════════════════════════════════════════
    def open_form(self, challenge_type, key):
        self._current_challenge_type = challenge_type
        self._current_challenge_key = key
        saved = self._get_saved(challenge_type, key)
        self.form_titulo.delete(0, "end")
        self.form_autor.delete(0, "end")
        self._form_foto_path = None
        self._form_preview_img = None
        self.form_preview.configure(image=None, text="")
        if saved:
            self.form_titulo.insert(0, saved.get("titulo", ""))
            self.form_autor.insert(0, saved.get("autor", ""))
            foto = saved.get("foto")
            if foto and os.path.exists(foto):
                self._form_foto_path = foto
                try:
                    img = Image.open(foto).resize((140, 190), Image.LANCZOS)
                    if CTkImage:
                        self._form_preview_img = CTkImage(light_image=img, dark_image=img, size=(140, 190))
                        self.form_preview.configure(image=self._form_preview_img, text="")
                except Exception:
                    pass
        if challenge_type == "reto_lector":
            info = RETO_LECTOR_DATA.get(int(key), {})
            self.form_context_label.configure(
                text=f"Mes: {info.get('mes', '')}  |  {info.get('reto', '')}",
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

    def refresh(self):
        self._cover_cache.clear()
        self.show_folders()
        self.build_folders()
        self.render_reto_lector()
        self.render_collect_colors()
        self.render_bracket()