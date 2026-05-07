# 📚 Book Journal App - Refactorizado

## Estructura del proyecto

```
book_journal/
├── main.py              # Punto de entrada y navegación principal
├── database.py          # Persistencia JSON y utilidades de ID
├── widgets.py           # Componentes reutilizables (StarRating, IconRating)
├── frames/
│   ├── __init__.py
│   ├── biblioteca.py    # Grid de libros
│   ├── review.py        # Formulario de reseñas
│   ├── tracker.py       # Tracker circular de lectura
│   ├── tbr.py           # Lista "To Be Read"
│   ├── bookshelf.py     # Visualización de estantería
│   └── challenges.py    # Desafíos de lectura
```

## Cambios realizados

### Limpieza de código muerto
- Eliminados imports no utilizados: `PIL.Image/ImageDraw/ImageFont`, `CTkSegmentedButton`, `CTkSlider`, `CTkImage`.
- Eliminado método vacío `on_canvas_click` en Tracker.
- Eliminado `addtag_withtag` roto que no aportaba funcionalidad.

### Corrección de bugs
- **Tracker circular**: eliminada línea de coordenadas corrupta (`__class__(__import__('math')...)`). Ahora usa `math` importado correctamente.
- **IDs únicos**: TBR y Challenges ahora usan identificadores únicos en lugar de comparar por título/fecha o nombre/meta, evitando colisiones y bugs al editar/eliminar.
- **Review form**: los `CTkTextbox` de frases y reseña ahora se empaquetan de forma consistente dentro del layout.
- **Biblioteca**: validación de título obligatorio al agregar libro.
- **Ventanas modales**: `transient` + `grab_set` en diálogos para mejor UX.

### Modularización
- Cada vista reside en su propio módulo bajo `frames/`.
- `Database` y widgets genéricos están desacoplulados.
- Fácil de extender: agregar un nuevo frame solo requiere importarlo en `main.py`.

## Cómo ejecutar

```bash
cd book_journal
pip install customtkinter
python main.py
```

> El archivo `book_journal_data.json` se creará automáticamente en el directorio de trabajo.
