# -*- coding: utf-8 -*-
"""
Procesa las fotos que dejes en web/fotos/<proyecto>/ y las deja listas
para la web, sin que haya que tocar una linea de codigo.

Como se usa
-----------
1. Arrastra las fotos a la carpeta del proyecto, por ejemplo
   web/fotos/las-moras/. El nombre del archivo no importa: el orden
   es alfabetico, asi que si queres mandarlas vos, numeralas 01, 02...
2. Corre:   python ingest_fotos.py
3. Listo. La web toma solas las fotos nuevas.

Que hace por cada foto
----------------------
- Endereza segun la orientacion de la camara (EXIF) y borra los metadatos.
- Genera dos tamanos (2000 px y 1000 px de ancho) en WebP y JPG.
- Escribe public/img/fotos.json, el indice que lee la web.

Requiere Pillow:  pip install Pillow
"""
import hashlib
import json
import os

from PIL import Image, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(BASE, "fotos")
# el sitio estatico sirve las fotos desde /img
_PUB = os.path.join(BASE, "public", "img")
SALIDA = _PUB if os.path.isdir(_PUB) else os.path.join(BASE, "img")
MANIFIESTO = os.path.join(SALIDA, "fotos.json")

TAMANOS = [("lg", 2000), ("md", 1000)]
EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")


def color_promedio(im):
    chico = im.convert("RGB").resize((1, 1), Image.LANCZOS)
    r, g, b = chico.getpixel((0, 0))
    return "#%02x%02x%02x" % (r, g, b)


def main():
    if not os.path.isdir(ENTRADA):
        print("No existe la carpeta 'fotos'. Corre el script desde /web.")
        return

    os.makedirs(SALIDA, exist_ok=True)
    manifiesto = {}
    if os.path.isfile(MANIFIESTO):
        with open(MANIFIESTO, encoding="utf-8") as fh:
            manifiesto = json.load(fh)

    total_fotos = 0
    for proyecto in sorted(os.listdir(ENTRADA)):
        carpeta = os.path.join(ENTRADA, proyecto)
        if not os.path.isdir(carpeta):
            continue

        archivos = sorted(f for f in os.listdir(carpeta)
                          if f.lower().endswith(EXTENSIONES))
        if not archivos:
            continue

        print("\n%s  (%d archivos)" % (proyecto, len(archivos)))
        fichas = []
        vistos = set()
        i = 0

        for nombre in archivos:
            ruta = os.path.join(carpeta, nombre)

            # la misma foto suele venir dos veces (numerada y "WhatsApp Image")
            firma = hashlib.md5(open(ruta, "rb").read()).hexdigest()
            if firma in vistos:
                print("   %-30s repetida, la salteo" % nombre[:30])
                continue
            vistos.add(firma)
            i += 1

            try:
                im = Image.open(ruta)
            except Exception as e:
                print("   no pude abrir %s: %s" % (nombre, e))
                continue

            # la foto de un celular viene rotada por metadato, no por pixeles
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGB")

            slug = "%s-f%02d" % (proyecto, i)
            w, h = im.size

            for etiqueta, ancho in TAMANOS:
                if w > ancho:
                    alto = round(h * ancho / w)
                    chica = im.resize((ancho, alto), Image.LANCZOS)
                else:
                    chica = im.copy()
                chica.save(os.path.join(SALIDA, "%s-%s.jpg" % (slug, etiqueta)),
                           "JPEG", quality=82, optimize=True, progressive=True)
                chica.save(os.path.join(SALIDA, "%s-%s.webp" % (slug, etiqueta)),
                           "WEBP", quality=80, method=6)

            fichas.append({"slug": slug, "w": w, "h": h,
                           "color": color_promedio(im),
                           "vertical": h > w, "origen": nombre})
            print("   %-22s %dx%d  ->  %s" % (nombre[:22], w, h, slug))
            total_fotos += 1

        manifiesto[proyecto] = fichas

    with open(MANIFIESTO, "w", encoding="utf-8") as fh:
        json.dump(manifiesto, fh, indent=2, ensure_ascii=False)

    print("\nListo: %d fotos procesadas." % total_fotos)
    print("Indice escrito en " + MANIFIESTO)
    for proyecto, fichas in manifiesto.items():
        print("   %-18s %d" % (proyecto, len(fichas)))


if __name__ == "__main__":
    main()
