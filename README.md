# TRAZZO — Hogares de Autor

Sitio de TRAZZO, estudio de arquitectura residencial de autor en Mendoza, Argentina.

**Diseño · Técnica · Hogar**

## Qué hay acá

| Archivo | Qué es |
|---|---|
| `index.html` | El sitio completo: HTML, CSS y JS en un solo archivo, sin dependencias ni build. |
| `img/` | Imágenes optimizadas (WebP + JPG, en dos tamaños) que consume la página. |
| `build_images.py` | Genera `img/` a partir de las fotos originales. |

## Secciones

1. **Obra** — línea de tiempo 2023-2025; cada obra abre un panel de detalle.
2. **Estudio** — la trayectoria, con la imagen rotando al scrollear.
3. **En proceso** — vivienda en construcción, en blanco y negro.
4. **Contacto** — el formulario arma un mensaje de WhatsApp.

## Imágenes

Las fotos originales **no** están versionadas: pesan unos 64 MB. En `img/` van
las derivadas optimizadas (10,5 MB), que es lo único que la página necesita.

Para regenerarlas, copiá los originales a esta carpeta y corré:

```bash
python build_images.py
```

El script redimensiona a 2000 px y 1000 px de ancho, exporta WebP y JPG, y
quita la marca de agua de IA en las tres fotos que la traían.

Requiere Pillow:

```bash
pip install Pillow
```

## Publicar

No hay compilación: `index.html` se sirve tal cual. Para GitHub Pages, elegí
la rama `main` y la carpeta raíz en Settings → Pages.

## Pendientes

- Falta el nombre y el año de la casa de `fachada.png`, hoy sin proyecto propio.
- Confirmar el uso comercial de las tres imágenes que traían marca de agua de IA.
