# 📚 Book Journal v2

## Estructura

```
book_journal_v2/
├── main.py              # Punto de entrada
├── database.py          # JSON + lógica de rachas
├── widgets.py           # StarRating, IconRating
├── frames/
│   ├── __init__.py
│   ├── biblioteca.py    # Grid libros + estados + filtros TBR/Leídos
│   ├── tracker.py       # Dona mensual + libros leyendo + rachas
│   ├── bookshelf.py     # Estantería con lomos personalizables
│   ├── review.py        # Libro abierto con navegación de páginas
│   └── challenges.py    # Reservado
```

## Funcionalidades

### 📖 Biblioteca
- Grid de libros con portada (foto desde ruta), título, autor, páginas, género, ubicación.
- Estados: **No leído / Leyendo / Leído**.
- Si está **Leído**: aparece puntuación con estrellas y formato (Físico/Digital/Audiolibro).
- Filtros rápidos: **Todos / TBR / Leídos**.
- Formulario embebido para añadir libros.

### 📅 Tracker
- **Dona circular** con días del mes.
- Selector de mes/año.
- Escala de color **degradada continua** según páginas leídas (gris → azul → verde → amarillo → naranja → rojo).
- Sobre cada día coloreado aparece la **cantidad de páginas** introducida.
- Panel lateral con lista de libros marcados como **"Leyendo"**.
- **Racha de lectura**: contador de días consecutivos. Se reinicia si falta un día.
- **Historial de rachas**: fechas de inicio/fin y duración de cada racha pasada.

### 🪴 Bookshelf
- Canvas con estantes.
- Selecciona un libro de tu biblioteca y elige **color del lomo**.
- Haz click en la estantería para **colocar el lomo** donde quieras.
- El **ancho del lomo es proporcional** a la longitud del título para que se lea completo.
- Lomos con efecto de brillo y sombra.

### ✍️ Review
- Diseño de **libro abierto**: dos páginas visibles.
- Navegación con botones **Anterior / Siguiente**.
- Págenes izquierda/derecha muestran reseñas guardadas.
- La última página derecha siempre es un **formulario en blanco** para escribir una nueva reseña.
- Al guardar, salta automáticamente a la spread donde se ve la nueva reseña.

### 🏆 Challenges
- Panel vacío reservado para futuras funcionalidades.

## Ejecutar

```bash
cd book_journal_v2
pip install customtkinter pillow
python main.py
```

> Se creará `book_journal_data.json` automáticamente.
