"""True-scale product photos on the grey tiles.

Every round downlight photo is resized so the fitting shows at its real size
relative to the others: Delta Recessed Fix Deep (70 mm) is the reference and
fills 37.1% of the tile width, so 1 mm = 0.53% of the tile width.

Sizes come from tile_sizes.csv (family, size, outer diameter in mm, thumb).
- size is blank for a single-size family, or the size word in the model name
  (Dea Amata XS 3.2W 18deg -> XS).
- thumb = yes scales the family thumbnail (first file in `images`) at that size;
  thumb = no leaves it alone (e.g. a thumbnail showing two fittings).

Unscaled sources are kept in originals/<same path>; the script always works
from those, so it can be re-run safely. When one photo is shared by several
sizes, the file is sized for the largest of them and the smaller sizes get an
`image_scale` value in products.csv (e.g. 0.28); the site shrinks the photo on
screen by that amount, so no extra files are needed.

Run automatically at the end of build_csv.py, or on its own:
    python3 true_scale.py
"""
import csv, os, re, shutil
from PIL import Image, ImageChops

REF_MM = 70.0          # Delta Recessed Fix Deep
REF_FRAC = 0.371       # Delta's width as a fraction of the tile width
MAX_FRAC = 0.90        # never fill more than 90% of the tile
BG_TOL = 12

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def size_of(family, model):
    if not model.startswith(family): return ''
    return re.sub(r'\s+[\d.]+W\b.*$', '', model[len(family):]).strip()

def original(path):
    o = os.path.join('originals', path)
    if not os.path.exists(o):
        os.makedirs(os.path.dirname(o), exist_ok=True)
        shutil.copy2(path, o)
    return o

def scale(src, dst, mm):
    im = Image.open(src).convert('RGB'); W, H = im.size; bg = im.getpixel((3, 3))
    mask = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L').point(lambda v: 255 if v > BG_TOL else 0)
    x0, y0, x1, y1 = mask.getbbox()
    target = min(REF_FRAC * mm / REF_MM, MAX_FRAC) * W
    s = target / (x1 - x0)
    sm = im.resize((round(W * s), round(H * s)), Image.LANCZOS)
    cx, cy = (x0 + x1) / 2 * s, (y0 + y1) / 2 * s
    out = Image.new('RGB', (W, H), bg); out.paste(sm, (round(W / 2 - cx), round(H / 2 - cy)))
    out.save(dst, quality=90, optimize=True)

def run(products='products.csv', table='tile_sizes.csv'):
    sizes = {}
    for r in csv.DictReader(open(table, encoding='utf-8-sig')):
        sizes.setdefault(r['family'], {})[r['size'].strip()] = (float(r['diameter_mm']), r['thumb'].strip().lower())
    rows = list(csv.DictReader(open(products, encoding='utf-8')))
    cols = list(rows[0].keys())
    fam_first = {}
    users = {}                                   # image path -> {(family, size): mm}; a photo can be shared across families
    def mm_of(r):
        f = r['family']; sz = size_of(f, r['model']) if len(sizes[f]) > 1 else next(iter(sizes[f]))
        return (f, sz), sizes[f].get(sz, (None,))[0]
    for r in rows:
        f = r['family']
        if f not in sizes: continue
        fam_first.setdefault(f, r)
        if r['model_image']:
            key, mm = mm_of(r)
            if mm: users.setdefault(r['model_image'], {})[key] = mm
    made, scales = 0, {}
    for img, uses in users.items():
        if not os.path.exists(img) and not os.path.exists(os.path.join('originals', img)): continue
        big = max(uses.values())
        scale(original(img), img, big); made += 1
        for key, mm in uses.items():
            if mm < big: scales[(img,) + key] = round(mm / big, 3)
    for f, first in fam_first.items():
        thumb = (first['images'] or '').split(';')[0]
        pick = [(mm, t) for sz, (mm, t) in sizes[f].items() if t == 'yes']
        if thumb and pick and (os.path.exists(thumb) or os.path.exists(os.path.join('originals', thumb))):
            scale(original(thumb), thumb, pick[0][0]); made += 1
    if 'image_scale' not in cols: cols.append('image_scale')
    for r in rows:
        f = r['family']
        r['image_scale'] = scales.get((r['model_image'],) + mm_of(r)[0], '') if f in sizes else r.get('image_scale', '')
    with open(products, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f'true_scale: {made} images scaled, {len(scales)} size/photo pairs shrunk on screen')

if __name__ == '__main__':
    run()
