"""Rev 2 photo run (2026-10-06): redo the 5 Oct Esse-Ci and PUK product photos with photo2.py.

Jobs: /tmp/claude-0/esse/esse_jobs.json, /tmp/claude-0/esse/puk_jobs.json (built from the batch logs/definitions).
Output: /tmp/claude-0/esse/rev2/<family>/<file>.jpg  (800 x 800 on #CCCCCC, never enlarged).
Run:  python3 regen_photos.py [esse|puk] [name-filter]
"""
import json, os, sys, traceback
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photo2 import *

U = '/mnt/user-data/uploads/Downloads/Website Dont Delete/'
OUT = os.environ.get('REV2_OUT', '/tmp/claude-0/esse/rev2/')
SITE = '/home/claude/site/images/'
LOGF = OUT + 'log.json'
LOG = json.load(open(LOGF)) if os.path.exists(LOGF) else {}

CROPS = {'Make-Spiegazione-famiglia-DEF_crop-deep-pro-fl.png': ('Make-Spiegazione-famiglia-DEF.jpg', (1760, 760, 2380, 1405))}
BIGGER = {  # a larger render of the same product found in the batch folders
    ('Batch 2026-10-05 Esse-Ci - Teres LV Micro Zoom +2', 'teres-pro-zoom.jpg'): 'Esse-Ci_TERES-PRO-LV.png',
}


USE_AI = {'teres-micro_miniatura1x.jpg', 'TERES-MICRO-ZOOM_miniatura2x.jpg'}   # photographs with soft shadows
NO_LIT = {'HALL-LED-CIELINIG-EVO-PC-MINI-QUADRATA.jpg'}   # no diffuser to protect: the white band is trim


def src_path(batch, name):
    name = BIGGER.get((batch, name), name)
    if name in CROPS:
        o, box = CROPS[name]
        p = f'/tmp/claude-0/esse/{name}'
        if not os.path.exists(p):
            Image.open(U + batch + '/01 Sources/originals/' + o).crop(box).save(p)
        return p
    return shrink(U + batch + '/01 Sources/originals/' + name)


def shrink(p, limit=2400):
    """Sources above 2400 px are scaled down first (the output is 800 px; keeps memory inside the workspace)."""
    im = Image.open(p)
    if max(im.size) <= limit:
        return p
    q = '/tmp/claude-0/esse/shrunk/' + os.path.basename(p).rsplit('.', 1)[0] + '.png'
    if not os.path.exists(q):
        os.makedirs(os.path.dirname(q), exist_ok=True)
        im = im.convert('RGB'); sc = limit / max(im.size)
        im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS).save(q)
    return q


def enclosed_by_dark(rgb, thr=70):
    dark = lum(rgb) < thr
    return ndimage.binary_fill_holes(dark) & ~dark


def border_stats(rgb):
    """Share of the border that is plain white, and the noise of those white pixels (products may run off the frame)."""
    b = np.concatenate([rgb[:3].reshape(-1, 3), rgb[-3:].reshape(-1, 3), rgb[:, :3].reshape(-1, 3), rgb[:, -3:].reshape(-1, 3)])
    w = b.min(-1) >= 236
    return w.mean(), (b[w].std(0).max() if w.any() else 99)


# ---------------- Esse-Ci ----------------
def esse_one(out_rel, j):
    p = src_path(j['batch'], j['src'])
    rgb0 = np.asarray(Image.open(p).convert('RGB'), np.float32)
    wfrac, noise = border_stats(rgb0)
    clean = wfrac > 0.7 and j['src'] not in USE_AI
    tol = 3 if noise < 1.5 else 8
    # paint tone of the source: dark (black render) or light (white render)
    rgb, a = (cut_clean(p, tol=tol) if clean else cut(p))
    if not clean:   # small enclosed holes in an AI cut-out are lenses / reflectors, not background
        solid = a > 0.5
        holes = ndimage.binary_fill_holes(solid) & ~solid
        hl, hn = ndimage.label(holes)
        if hn:
            sz = ndimage.sum(holes, hl, range(1, hn + 1))
            small = np.isin(hl, [i + 1 for i, v in enumerate(sz) if v < 0.03 * solid.sum()])
            a = np.where(small, 1.0, a)
            src_rgb = np.asarray(Image.open(p).convert('RGB'), np.float32)
            rgb = np.where(small[..., None], src_rgb, rgb)          # original pixels, not the edge un-mix
    if clean and float(np.median(lum(rgb)[a > 0.9])) >= 110:
        # white product on white: highlights can equal the background, so the AI cut-out supplies the solid shape
        # and the colour cut-out the precise edge
        ai = matte_cached(p)
        solid = ndimage.binary_erosion(ndimage.binary_fill_holes(ai > 0.5), iterations=2)
        a = np.maximum(a, solid.astype(np.float32))
    L = lum(rgb)
    body = (a > 0.9)
    medL = float(np.median(L[body]))
    sfin = j['sfin'] or ('black' if medL < 110 else 'white')
    want = j['want'] or sfin
    info = dict(src=os.path.basename(p), clean=bool(clean), src_fin=sfin, want=want)
    if want == 'deeppro':
        raise RuntimeError('deeppro: done separately')
    if j['src'] == 'hall_led_pro-1.jpg':
        raise RuntimeError('KEEP: source too small (88 x 254 px), keep the 5 Oct photo')
    if j['src'] == 'GROOVE-DISPLAY_miniatura.jpg':
        raise RuntimeError('KEEP: white profile + white diffuser on white running off the frame, keep the 5 Oct photo')
    if sfin == 'grey':                                   # Arkeon Wall: grey render -> both finishes
        S = sat(rgb)
        paint = (L > 40) & (L < 235) & (S < 0.15)
        res = recolour(rgb, a, want, paint)
        img = None
    elif clean and sfin == 'black':                      # dark product on white: keep the render's own edges
        img = dark_on_white_to_v2(p, to=None if want == 'black' else 'white', tol=tol)
        res = None
    else:                                                # light product: precise cut-out, recolour to black if needed
        if want == 'black':
            S = sat(rgb)
            ring = (L < 228) & (a > 0.5)                   # trim / lip around a diffuser or lens
            lit = ndimage.binary_fill_holes(ring) & ~ring & (L >= 238)
            lit = ndimage.binary_opening(lit, iterations=2)
            if j['src'] in NO_LIT:
                lit[:] = False
            res = recolour(rgb, a, 'black', (L > 150) & (S < 0.12), protect=enclosed_by_dark(rgb) | lit)
        else:
            res = rgb
        img = None
    dst = OUT + out_rel
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if img is not None:
        im, sc = place_composited(img, dst)
        save_jpg(im, dst)
    else:
        sc = place(res, a, dst)
    info['scale'] = sc
    return info


# ---------------- PUK ----------------
_mattes = {}
GLASS = None


def glass_masks():
    """Hand-set glass outlines from 5 Oct (puk_glass_fix.py), in the old 800 x 800 white-aluminium photos."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('pgf', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'puk_glass_fix.py'))
    src = open(spec.origin).read().split('def run(')[0]
    g = {}
    exec(src, g)
    return g['P'], {'coiny-bollard/coiny-bollard': (254, 121, 376, 213)}


def bbox204(im):
    a = np.asarray(im.convert('RGB'), np.float32)
    m = ndimage.binary_opening(np.abs(a - 204).max(-1) > 8, iterations=1)
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def glass_protect(key, new_real):
    """Map the old glass outline onto the new white-aluminium photo (product bounding boxes give scale + offset)."""
    global GLASS
    if GLASS is None:
        GLASS = glass_masks()
    P, E = GLASS
    if key not in P and key not in E:
        return None
    old = Image.open(SITE + key + '-white-aluminium.jpg')
    ox0, oy0, ox1, oy1 = bbox204(old)
    nx0, ny0, nx1, ny1 = bbox204(new_real)
    sx, sy = (nx1 - nx0) / max(ox1 - ox0, 1), (ny1 - ny0) / max(oy1 - oy0, 1)
    f = lambda x, y: (nx0 + (x - ox0) * sx, ny0 + (y - oy0) * sy)
    m = Image.new('L', (800, 800), 0); d = ImageDraw.Draw(m)
    for poly in P.get(key, []):
        d.polygon([f(x, y) for x, y in poly], fill=255)
    if key in E:
        x0, y0, x1, y1 = E[key]
        (a0, b0), (a1, b1) = f(x0, y0), f(x1, y1)
        d.rounded_rectangle((a0, b0, a1, b1), radius=28 * sx, fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2))


def puk_one(job):
    p = shrink(U + job['batch'] + '/01 Sources/originals/' + job['src'])
    if p not in _mattes:
        _mattes[p] = cut(p)
    rgb, a = _mattes[p]
    fin = job['fin']
    dst = OUT + job['out']
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    recol = fin in ('anthracite-grey', 'black', 'matt-black') and job['real_grey']
    if recol:
        L, S = lum(rgb), sat(rgb)
        paint = (L > 95) & (L < 240) & (S < 0.12)          # RAL 9006 body; opal / glass highlights above 240 stay
        res = recolour(rgb, a, fin, paint, protect=enclosed_by_dark(rgb, 60))
    else:
        res = rgb
    sc = place(res, a, dst)
    info = dict(src=job['src'], fin=fin, recoloured=bool(recol), scale=sc)
    if recol:   # bollard glass: put the real glass back
        key = job['out'].rsplit('-' + fin, 1)[0]
        real_dst = OUT + key + '-white-aluminium.jpg'
        if not os.path.exists(real_dst):
            place(rgb, a, real_dst)
        m = glass_protect(key, Image.open(real_dst))
        if m is not None:
            out = Image.composite(Image.open(real_dst).convert('RGB'), Image.open(dst).convert('RGB'), m)
            save_jpg(out, dst)
            info['glass'] = 'restored from real photo'
    return info


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'esse'
    filt = sys.argv[2] if len(sys.argv) > 2 else ''
    if which == 'esse':
        jobs = json.load(open('/tmp/claude-0/esse/esse_jobs.json'))
        done = {}
        for out_rel, j in sorted(jobs.items(), key=lambda kv: ('copy_of' in kv[1], kv[0])):
            if filt not in out_rel: continue
            try:
                if 'copy_of' in j and os.path.exists(OUT + j['copy_of']):
                    import shutil; os.makedirs(os.path.dirname(OUT + out_rel), exist_ok=True)
                    shutil.copy(OUT + j['copy_of'], OUT + out_rel); LOG[out_rel] = dict(copy_of=j['copy_of']); continue
                LOG[out_rel] = esse_one(out_rel, j)
            except Exception as e:
                LOG[out_rel] = dict(error=repr(e)); traceback.print_exc()
    else:
        jobs = json.load(open('/tmp/claude-0/esse/puk_jobs.json'))
        jobs.sort(key=lambda j: (j['src'], j['fin'] != 'white-aluminium'))   # real photo first (glass reference)
        for j in jobs:
            if filt not in j['out']: continue
            try:
                LOG[j['out']] = puk_one(j)
            except Exception as e:
                LOG[j['out']] = dict(error=repr(e)); traceback.print_exc()
    json.dump(LOG, open(LOGF, 'w'), indent=1)
    errs = [k for k, v in LOG.items() if 'error' in v]
    print(len(LOG), 'logged,', len(errs), 'errors', errs[:10])
