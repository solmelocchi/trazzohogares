# -*- coding: utf-8 -*-
"""
TRAZZO — generacion del set de imagenes web.
Toma los originales de /web y escribe derivados optimizados en /web/img.

Por cada imagen produce:
    img/<slug>-lg.webp / .jpg   (2000 px de ancho)
    img/<slug>-md.webp / .jpg   (1000 px de ancho)

Ademas parcha la marca de agua de IA (estrella inferior derecha) en las
imagenes marcadas con watermark=True, espejando el sector contiguo.

Uso:  python build_images.py
"""
import json
import os

from PIL import Image, ImageFilter

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "img")

# (archivo origen, slug, tiene marca de agua)
IMAGES = [
    ("las_moras_luna.jpg",                        "las-moras-01",   False),
    ("las_moras_noche.jpg",                       "las-moras-02",   False),
    ("Complejo Las Moras - © Luis Abba-00-5.jpg", "las-moras-03", False),
    ("casa_alma.png",                             "casa-alma-01",   False),
    ("estar.png",                                 "casa-alma-02",   False),
    ("Gemini_Generated_Image_b36qb2b36qb2b36q.png", "peralitos-01",  True),
    ("estar peralitos.png",                       "peralitos-02",   True),
    ("LAR_DE_VIEYTES_II.png",                     "vieytes-01",     True),
    ("fachada.png",                               "casa-dusk-01",   False),
    ("fachada_posterior.png",                     "casa-dusk-02",   False),
    ("hotel_entrada.jpg",                         "vistalba-01",    False),
    ("20251029_202637.jpg",                       "vistalba-02",    False),
    ("20251029_202033.jpg",                       "vistalba-03",    False),
    ("20251031_194345.jpg",                       "vistalba-obra",  False),

    # Renders de la vivienda en construccion (seccion "En obra").
    ("FACHADA FRONTAL (1).png",                   "render-fachada", False),
    ("ESTAR COMEDOR7.png",                        "render-estar",   False),
    ("TERRAZA.jpeg",                              "render-terraza", False),
]

SIZES = [("lg", 2000), ("md", 1000)]

# Caja de la marca de agua, en fraccion del ancho/alto.
WM_X0, WM_Y0 = 0.910, 0.870


def strip_watermark(im):
    """Cubre la esquina inferior derecha espejando la region contigua,
    con un degradado en el borde izquierdo para que no se vea el corte."""
    w, h = im.size
    x0, y0 = int(w * WM_X0), int(h * WM_Y0)
    pw, ph = w - x0, h - y0
    if pw <= 0 or ph <= 0 or x0 - pw < 0:
        return im

    patch = im.crop((x0 - pw, y0, x0, h)).transpose(Image.FLIP_LEFT_RIGHT)
    patch = patch.filter(ImageFilter.GaussianBlur(0.6))

    # Mascara: opaca a la derecha, transparente en el borde izquierdo.
    mask = Image.new("L", (pw, ph), 255)
    feather = max(1, pw // 4)
    px = mask.load()
    for x in range(feather):
        v = int(255 * (x / feather))
        for y in range(ph):
            px[x, y] = v

    im.paste(patch, (x0, y0), mask)
    return im


def avg_color(im):
    small = im.convert("RGB").resize((1, 1), Image.LANCZOS)
    r, g, b = small.getpixel((0, 0))
    return "#%02x%02x%02x" % (r, g, b)


def main():
    os.makedirs(OUT, exist_ok=True)
    meta, total_in, total_out = {}, 0, 0

    for fname, slug, wm in IMAGES:
        path = os.path.join(SRC, fname)
        if not os.path.isfile(path):
            # los renders se listan sin extension: probamos las habituales
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                if os.path.isfile(path + ext):
                    path = path + ext
                    break
        if not os.path.isfile(path):
            print("  FALTA: %s  (la seccion queda sin esa imagen)" % fname)
            continue

        total_in += os.path.getsize(path)
        im = Image.open(path)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGB")

        if wm:
            im = strip_watermark(im)

        w, h = im.size
        meta[slug] = {"w": w, "h": h, "color": avg_color(im), "src": fname}

        for tag, target in SIZES:
            if w > target:
                nh = round(h * target / w)
                rz = im.resize((target, nh), Image.LANCZOS)
            else:
                rz = im.copy()

            jpg = os.path.join(OUT, "%s-%s.jpg" % (slug, tag))
            web = os.path.join(OUT, "%s-%s.webp" % (slug, tag))
            rz.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
            rz.save(web, "WEBP", quality=80, method=6)
            total_out += os.path.getsize(jpg) + os.path.getsize(web)

        print("  ok  %-16s %sx%s  %s" % (slug, w, h, meta[slug]["color"]))

    with open(os.path.join(OUT, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)

    print("\n  originales : %6.1f MB" % (total_in / 1048576))
    print("  derivados  : %6.1f MB" % (total_out / 1048576))


if __name__ == "__main__":
    main()
