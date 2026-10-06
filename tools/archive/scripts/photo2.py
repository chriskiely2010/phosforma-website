"""Photo process v2 (2026-10-06) - replaces the threshold cut-out + flat recolour used for the 5 Oct batches.

1. Cut-out: IS-Net (AI matting, ~/.u2net/isnet-general-use.onnx; BiRefNet needs more than the 8 GB workspace) gives a soft alpha that holds
   white-on-white edges. The colour of edge pixels is "un-mixed" from the source background so no halo is left.
2. Placement: 800 x 800 on #CCCCCC, product inside 80 % of the tile, NEVER enlarged (max scale 1.0).
3. Recolour keeps the shading: the paint's own light-to-dark range is mapped onto the new paint's range
   (black RAL 9005: ~16-105, white RAL 9003: ~178-250) instead of flattening it to one value.
   Lenses, reflectors and diffusers are protected: only paint regions connected to the body are changed;
   small enclosed light/dark areas keep their original pixels.
"""
import numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
from scipy import ndimage

GREY = (204, 204, 204)
_sess = None


def matte(im):
    """BiRefNet alpha (float 0..1) at the image's own size."""
    global _sess
    if _sess is None:
        so = ort.SessionOptions()
        so.enable_cpu_mem_arena = False          # keeps peak memory inside the 8 GB workspace
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        so.intra_op_num_threads = 1
        _sess = ort.InferenceSession('/root/.u2net/isnet-general-use.onnx', so, providers=['CPUExecutionProvider'])
    x = np.asarray(im.convert('RGB').resize((1024, 1024), Image.BICUBIC), np.float32) / 255 - 0.5
    out = _sess.run(None, {'input_image': x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    out = (out - out.min()) / max(out.max() - out.min(), 1e-6)
    a = Image.fromarray((out * 255).astype(np.uint8)).resize(im.size, Image.BICUBIC)
    a = np.asarray(a, np.float32) / 255
    a = np.clip((a - 0.04) / 0.92, 0, 1)          # clean near-0 / near-1 noise
    return a


def unmix(rgb, a, bg):
    """Remove the background colour mixed into semi-transparent edge pixels: F = (C - (1-a)B) / a."""
    a3 = np.clip(a, 1e-3, 1)[..., None]
    f = (rgb - (1 - a3) * np.array(bg, np.float32)) / a3
    w = np.clip((a[..., None] - 0.15) / 0.35, 0, 1)          # faint edge pixels: keep source colour (no over-correction specks)
    return np.clip(f, 0, 255) * w + rgb * (1 - w)


def cut(path, bg=None):
    im = Image.open(path).convert('RGB')
    rgb = np.asarray(im, np.float32)
    if bg is None:  # background = median of the border
        b = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
        bg = tuple(np.median(b, 0))
    a = matte(im)
    return unmix(rgb, a, bg), a


def lum(rgb):
    return rgb @ np.array([0.299, 0.587, 0.114], np.float32)


def sat(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)


def body_mask(sel, a, keep_frac=0.02):
    """Paint = the selected pixels that form the body (large connected parts); small enclosed parts
    (a lit lens inside a dark reflector, a bright reflector in a black front) are left alone."""
    sel = sel & (a > 0.05)
    lab, n = ndimage.label(sel)
    if not n:
        return sel
    sizes = ndimage.sum(sel, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= keep_frac * sizes.max()])


TARGETS = {   # base, span, tint, where the body's middle tone should land (0 = base, 1 = base + span)
    'black':           (14, 80, np.array([1.0, 1.0, 1.03], np.float32), 0.22),    # RAL 9005
    'matt-black':      (16, 44, np.array([1.0, 1.0, 1.02], np.float32), 0.30),   # matt: low highlights
    'anthracite-grey': (30, 100, np.array([0.92, 1.0, 1.06], np.float32), 0.30),  # RAL 7016
    'white':           (182, 70, np.array([1.0, 1.0, 0.985], np.float32), 0.72), # RAL 9003
}


def tone(to, t, t_med):
    """Map 0..1 source shading onto the finish: a power curve chosen so the body's median lands on the finish's own
    middle tone (an evenly lit white render must not turn into grey, a dark render must not turn into flat white)."""
    base, span, tint, mid = TARGETS[to]
    g = float(np.clip(np.log(mid) / np.log(np.clip(t_med, 0.05, 0.95)), 0.35, 4.0))
    return base + span * t ** g, tint


def recolour(rgb, a, to, src_paint, protect=None):
    """to: 'black' or 'white'. src_paint: boolean selector of the original paint. Shading kept by mapping
    the paint's 2-98 % luminance range onto the target range; soft 2-px blend at the mask edge."""
    L = lum(rgb)
    m = body_mask(src_paint, a)
    if protect is not None:
        m &= ~protect
    lo, hi = np.percentile(L[m], 2), np.percentile(L[m], 98)
    t = np.clip((L - lo) / max(hi - lo, 1), 0, 1)
    new, tint = tone(to, t, float(np.median(t[m])))
    new3 = np.clip(new[..., None] * tint, 0, 255)
    w = ndimage.gaussian_filter(m.astype(np.float32), 1.0)[..., None]
    return new3 * w + rgb * (1 - w)


def place(rgb, a, out, canvas=800, box=0.8, max_up=1.5, shadow=False):
    ys, xs = np.where(a > 0.03)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([rgb[y0:y1, x0:x1], a[y0:y1, x0:x1] * 255]).clip(0, 255).astype(np.uint8)
    obj = Image.fromarray(rgba, 'RGBA')
    sc = min(canvas * box / obj.width, canvas * box / obj.height, max_up)
    obj = obj.resize((round(obj.width * sc), round(obj.height * sc)), Image.LANCZOS)
    base = Image.new('RGBA', (canvas, canvas), GREY + (255,))
    base.alpha_composite(obj, ((canvas - obj.width) // 2, (canvas - obj.height) // 2))
    base.convert('RGB').save(out, 'JPEG', quality=90, optimize=True, subsampling=0)
    return round(sc, 2)


_MC = {}


def matte_cached(path):
    if path not in _MC:
        _MC[path] = matte(Image.open(path))
    return _MC[path]


def background(path, rgb, tol):
    """Background of a plain-white render: near-white joined to the border, plus white areas the AI cut-out says are
    not product (the gap between two cables, an off-white patch behind the fitting). Enclosed white areas the AI
    counts as product (diffusers, lit lenses, white paint) stay product."""
    dist = (255 - rgb).max(-1)
    near = dist <= tol
    lab, n = ndimage.label(near)
    ai = matte_cached(path)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    if edge:   # white touching the frame is background unless the AI sees product there (a diffuser running off-frame)
        edge = sorted(edge)
        mean_ai = ndimage.mean(ai, lab, edge)
        edge = [e for e, v in zip(edge, mean_ai) if v < 0.5]
    bg = np.isin(lab, list(edge))
    light = rgb.min(-1) >= 228
    broad = ndimage.binary_dilation(ndimage.binary_opening(light & ~bg & ~near, iterations=3), iterations=3) & light & ~bg
    broad |= near & ~bg                                     # enclosed near-white areas (gaps, diffusers) are tested too
    lab2, n2 = ndimage.label(broad)                         # broad white areas only: thin pale cables stay product
    if n2:
        mean_ai = ndimage.mean(ai, lab2, range(1, n2 + 1))
        bad = [i + 1 for i, v in enumerate(mean_ai) if v < 0.3]
        bg |= np.isin(lab2, bad)
    # soft shadows on the white sweep: light, neutral, AI says not product, joined to the background
    shadow = (ai < 0.15) & (rgb.min(-1) >= 170) & (sat(rgb) < 0.08)
    shadow = ndimage.binary_opening(shadow & ~near, iterations=4)   # broad shadows only: thin pale cables stay product
    soft = (ai < 0.15) & (rgb.min(-1) >= 170) & (sat(rgb) < 0.08)
    shadow |= ndimage.binary_dilation(shadow, iterations=4) & soft          # the shadow's own soft edge
    bg = ndimage.binary_propagation(bg, mask=bg | shadow)
    # inside the AI's solid product shape nothing is background (bright lenses, highlights on a track bar)
    bg &= ~ndimage.binary_erosion(ndimage.binary_fill_holes(ai > 0.6), iterations=1)
    return bg, dist, ai


def cut_clean(path, tol=2, bg=None):
    """For renders on a plain, even background (Esse-Ci on white): background = pixels within `tol` of the
    background colour that connect to the image border. Everything else is product, so white-on-white edges,
    suspension wires and lit diffusers all stay. Edge alpha = a difference matte: how far an edge pixel is from
    the background compared with the product colour right next to it, so dark and white products both get
    clean anti-aliased edges. Background colour is then un-mixed out of those edge pixels."""
    im = Image.open(path).convert('RGB')
    rgb = np.asarray(im, np.float32)
    if bg is None:
        b = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
        bg = np.median(b, 0)
    bgm, _, ai = background(path, rgb, tol)
    dist = np.abs(rgb - np.array(bg, np.float32)).max(-1)
    fg = ~bgm
    fg |= ndimage.binary_fill_holes(fg) & (ai > 0.5)        # white areas inside the product the AI sees as product
    lab2, n2 = ndimage.label(fg)                       # drop specks (JPEG noise), keep the product and wires
    if n2:
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
        fg = np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s >= max(30, 0.0005 * sizes.max())])
    band = fg & ~ndimage.binary_erosion(fg, iterations=2)
    ref = ndimage.maximum_filter(np.where(fg & ~band, dist, 0), 7)
    ref = np.where(ref > 0, ref, ndimage.maximum_filter(dist * fg, 7))
    a = fg.astype(np.float32)
    a[band] = np.clip(dist[band] / np.maximum(ref[band], 1), 0, 1)
    out = ndimage.binary_dilation(fg, iterations=1) & ~fg   # 1-px outer ring for smooth edges
    a[out] = np.clip(dist[out] / np.maximum(ndimage.maximum_filter(dist * fg, 5)[out], 1), 0, 1) * 0.9
    return unmix(rgb, a, tuple(bg)), a


def dark_on_white_to(path, to='white', out_bg=204, tol=4):
    """Dark product photographed on plain white -> #CCCCCC background, paint recoloured, keeping the source's own
    anti-aliasing (no cut-out step, so edges and thin suspension cords stay exactly as smooth as the render).
    1. Background: near-white pixels joined to the border are multiplied down to #CCCCCC, as are the 3 px
       around them, so mixed edge pixels and cords become 'dark over grey' just like the original was 'dark over white'.
    2. Paint: large dark regions (thin cords excluded) are mapped to the new finish with their shading kept.
    3. Outer edge of the paint: re-mixed as alpha * new paint + (1 - alpha) * grey, alpha measured from the
       source, so the new white profile has the same smooth edge the black one had."""
    src = np.asarray(Image.open(path).convert('RGB'), np.float32)
    dist = (255 - src).max(-1)
    lab, n = ndimage.label(dist <= tol)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgz = ndimage.binary_dilation(np.isin(lab, list(edge)), iterations=3)
    img = np.where(bgz[..., None], src * (out_bg / 255.0), src)
    L, S = lum(src), sat(src)
    paint = ndimage.binary_opening((L < 185) & (S < 0.3), iterations=2)      # cords are thinner than this: left alone
    paint = body_mask(paint, np.ones_like(L))
    core = ndimage.binary_erosion(paint, iterations=1)
    lo, hi = np.percentile(L[core], 2), np.percentile(L[core], 98)
    t = np.clip((L - lo) / max(hi - lo, 1), 0, 1)
    if to == 'white':
        new = (192 + t ** 0.85 * 58)[..., None] * np.array([1.0, 1.0, 0.985], np.float32)
    else:
        new = (16 + t ** 1.15 * 92)[..., None] * np.array([1.0, 1.0, 1.03], np.float32)
    out = img.copy()
    out[core] = new[core]
    # outer edge: pixels near the paint that also touch the background zone
    ring = ndimage.binary_dilation(core, iterations=3) & ~core & bgz & ~ndimage.binary_opening(dist > tol, iterations=0) if False else \
           ndimage.binary_dilation(core, iterations=3) & ~core & bgz
    _, (iy, ix) = ndimage.distance_transform_edt(~core, return_indices=True)
    Fsrc = L[iy, ix]                       # source paint luminance at the nearest paint pixel
    Fnew = new[iy, ix]                     # its new colour
    alpha = np.clip((255 - L) / np.maximum(255 - Fsrc, 1), 0, 1)              # measured on the white source
    mix = alpha[..., None] * Fnew + (1 - alpha[..., None]) * out_bg
    out[ring] = mix[ring]
    # inner edge (paint next to diffuser / lens): soft blend so there is no hard seam
    inner = ndimage.binary_dilation(core, iterations=1) & ~core & ~bgz
    w = 0.5
    out[inner] = (w * new + (1 - w) * img)[inner]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def dark_on_white_to_v2(path, to='white', out_bg=204, tol=4):
    """Like dark_on_white_to but with no hard paint boundary: every pixel within 3 px of the paint is treated as
    a mix  alpha * paint + (1 - alpha) * light  (light = the white background or a lit diffuser), alpha measured
    from the source. It is re-mixed as  alpha * new paint + (1 - alpha) * (grey if background, else the light).
    Cords and anything further than 3 px from the paint keep their own (grey-composited) colour."""
    src = np.asarray(Image.open(path).convert('RGB'), np.float32)
    bg, dist, _ = background(path, src, tol)
    bgz = ndimage.binary_dilation(bg, iterations=4)
    img = np.where(bgz[..., None], src * (out_bg / 255.0), src)
    far = ndimage.binary_erosion(bg, iterations=3)          # clear background (incl. soft shadows): flat grey
    w = ndimage.gaussian_filter(far.astype(np.float32), 1.0)[..., None]
    img = img * (1 - w) + out_bg * w
    L, S = lum(src), sat(src)
    # thin parts outside the body (suspension cables, cords): extra contrast so they survive the downscale to 800 px
    body = ndimage.binary_dilation(ndimage.binary_opening((L < 140) & (S < 0.3), iterations=4), iterations=3)
    thin = ~ndimage.binary_erosion(bg, iterations=1) & ~body
    img = np.where(thin[..., None], out_bg - (out_bg - img) * 1.8, img)
    if to is None:
        return Image.fromarray(img.clip(0, 255).astype(np.uint8))
    raw = (L < 140) & (S < 0.3)
    core = ndimage.binary_opening(raw, iterations=4)
    thin = raw & ~core                                   # cables / cords stay as they are; other thin parts are paint
    lab, n = ndimage.label(thin, structure=np.ones((3, 3)))
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not (h > 40 and h > 3 * w):
            core |= lab == i
    core = body_mask(core, np.ones_like(L))
    core &= ~ndimage.binary_dilation(L >= 140, iterations=1)   # half-paint edge pixels are blended, not painted
    lo, hi = np.percentile(L[core], 2), np.percentile(L[core], 98)
    t_med = float(np.clip((np.median(L[core]) - lo) / max(hi - lo, 1), 0, 1))
    def mapc(Lv):
        t = np.clip((Lv - lo) / max(hi - lo, 1), 0, 1)
        v, tint = tone(to, t, t_med)
        return v[..., None] * tint
    d, (iy, ix) = ndimage.distance_transform_edt(~core, return_indices=True)
    F = np.where(core, L, L[iy, ix])                     # paint luminance under each pixel
    light = np.where(bgz, 255.0, np.maximum(ndimage.maximum_filter(L, 7), F + 1))
    alpha = np.where(core, 1.0, np.clip((light - L) / np.maximum(light - F, 1), 0, 1))
    lout = np.where(bgz, float(out_bg), light)[..., None] * np.ones(3, np.float32)
    new = alpha[..., None] * mapc(F) + (1 - alpha[..., None]) * np.where(bgz[..., None], lout, src)
    zone = (d <= 3)[..., None]
    out = np.where(zone, new, img)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def place_composited(img, out, canvas=800, box=0.8, max_up=1.5, bg=204):
    """Place an image that is already on a flat #CCCCCC background: crop to the product, never enlarge."""
    a = np.asarray(img.convert('RGB'), np.float32)
    m = np.abs(a - bg).max(-1) > 4                      # product incl. thin cables; drop isolated specks only
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    if n:
        sz = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, [i + 1 for i, v in enumerate(sz) if v >= 150])
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    pad = 4
    crop = img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))
    sc = min(canvas * box / crop.width, canvas * box / crop.height, max_up)
    crop = crop.resize((max(1, round(crop.width * sc)), max(1, round(crop.height * sc))), Image.LANCZOS)
    base = Image.new('RGB', (canvas, canvas), (bg, bg, bg))
    base.paste(crop, ((canvas - crop.width) // 2, (canvas - crop.height) // 2))
    return base, round(sc, 2)


def save_jpg(img, path, limit=300 * 1024):
    import io, os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for q in (90, 86, 82, 78):
        buf = io.BytesIO(); img.save(buf, 'JPEG', quality=q, optimize=True, subsampling=0)
        if buf.tell() <= limit or q == 78:
            open(path, 'wb').write(buf.getvalue()); return q
