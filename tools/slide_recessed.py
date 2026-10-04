"""Banner slide for recessed downlights: the full fitting shown in a ceiling section.

Upper part = ceiling void (dark grey), a white ceiling board, room below (light grey).
The side render (transparent PNG) is placed so the trim's flange sits on the board:
everything of the fitting below the board line is hidden except the trim face
(found by fitting an ellipse to the trim's lower edge), so springs and body read as
being above the ceiling.

    python3 slide_recessed.py <render.png> <out.jpg> [--x 0.70] [--h 0.78]
"""
import sys, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.optimize import least_squares

W, H = 1920, 800
VOID, BOARD, ROOM = (176, 176, 176), (255, 255, 255), (233, 233, 233)

def trim_ellipse(alpha):
    m = alpha > 40
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cols = np.arange(x0, x1 + 1)
    bottom = np.array([np.nonzero(m[:, x])[0].max() if m[:, x].any() else -1 for x in cols])
    mid = (cols > x0 + 0.2 * (x1 - x0)) & (cols < x1 - 0.2 * (x1 - x0))   # skip the springs at the sides
    keep = (bottom > y0 + 0.55 * (y1 - y0)) & mid
    px, py = cols[keep].astype(float), bottom[keep].astype(float)
    def res(p):
        cx, cy, rx, ry = p
        t = np.clip((px - cx) / rx, -1, 1)
        return cy + ry * np.sqrt(1 - t * t) - py
    p0 = [(x0 + x1) / 2, y1 - 0.15 * (y1 - y0), (x1 - x0) / 2.4, 0.12 * (y1 - y0)]
    r = least_squares(res, p0, loss='soft_l1', f_scale=4)
    return r.x  # cx, cy, rx, ry

def remove_clips(fit, y0, ex, ey, rx, ry):
    """Paint out spring clips that show over the trim face below the ceiling.
    Works on the fitting layer only: clip pixels (thin metal, far from the trim
    colour, in the outer ring of the trim ellipse) are filled from the trim around
    them; any clip pixel past the trim edge is made transparent."""
    import cv2
    arr = np.array(fit); rgb = arr[:, :, :3].copy(); al = arr[:, :, 3]
    h, w = al.shape; yy, xx = np.mgrid[0:h, 0:w]
    r = ((xx - ex) / rx) ** 2 + ((yy - ey) / ry) ** 2
    ring = (r < 1.1) & (r > 0.55) & (yy > y0) & (al > 128)
    if not ring.any(): return fit
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(float)
    med = np.median(g[ring & (r < 0.95)])
    sat = rgb.max(2).astype(int) - rgb.min(2).astype(int)
    clip = (ring & (np.abs(g - med) > 45) & (sat < 40)).astype('uint8') * 255
    clip = cv2.dilate(clip, np.ones((5, 5), np.uint8))
    clip[(yy <= y0) | (al == 0)] = 0
    rgb = cv2.inpaint(rgb, clip, 6, cv2.INPAINT_TELEA)
    al = al.copy(); al[(clip > 0) & (r > 0.97)] = 0
    return Image.fromarray(np.dstack([rgb, al]))

def make(src, dst, xfrac=0.70, hfrac=0.62, board=0.028, debug=False):
    im = Image.open(src).convert('RGBA')
    im = im.crop(im.split()[3].getbbox())
    cx, cy, rx, ry = trim_ellipse(np.array(im.split()[3]))
    s = hfrac * H / im.height
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    cx, cy, rx, ry = cx * s, cy * s, rx * s, ry * s
    top = 0.62 * H - (cy - 0.9 * ry)                       # board line at 62% of the height
    left = xfrac * W - cx
    line = top + cy - 0.9 * ry                             # board top just below the back edge of the trim
    bt = round(board * H)
    scene = Image.new('RGB', (W, H), ROOM)
    d = ImageDraw.Draw(scene)
    d.rectangle([0, 0, W, line], fill=VOID)
    d.rectangle([0, line, W, line + bt], fill=BOARD)
    # fitting
    fit = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fit.paste(im, (round(left), round(top)))
    keep = Image.new('L', (W, H), 0); kd = ImageDraw.Draw(keep)
    kd.rectangle([0, 0, W, line], fill=255)              # above the ceiling: all of it
    ex, ey = left + cx, top + cy
    kd.ellipse([ex - rx * 0.995, ey - ry * 1.04, ex + rx * 0.995, ey + ry * 1.04], fill=255)   # trim face
    keep = keep.filter(ImageFilter.GaussianBlur(1.2))
    a = Image.fromarray((np.array(fit.split()[3]).astype(float) * np.array(keep) / 255).astype('uint8'))
    fit.putalpha(a)
    fit = remove_clips(fit, line + bt, left + cx, top + cy, rx, ry)
    out = scene.convert('RGBA'); out.alpha_composite(fit)
    if debug:
        dd = ImageDraw.Draw(out); dd.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], outline=(255, 0, 0, 255), width=2)
    out.convert('RGB').save(dst, quality=88, optimize=True)
    return (cx, cy, rx, ry)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--x', type=float, default=0.70); ap.add_argument('--h', type=float, default=0.62)
    ap.add_argument('--debug', action='store_true')
    a = ap.parse_args(); print(make(a.src, a.dst, a.x, a.h, debug=a.debug))
