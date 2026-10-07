"""Photometric curves for the generated PDF datasheets.

Reads EULUMDAT (.ldt) files under photometry_src/ and writes files/photometry/c/<id>.json ({name, lm, w, g, c0, c180, c90, c270})
and files/photometry/i/<code prefix>.json ({code: id, or [id, flux] when measured at another colour temperature}).
c0 = C0-C180 plane, c90 = C90-C270 plane, both as absolute candela from gamma 0 (straight down) to 180.
Each code uses the LDT archive linked in its downloads (LDT=...), unpacked under photometry_src/<brand>/<archive>/; see pick().
Run:  python3 photometry.py
"""
import csv, glob, json, os, re

def num(s):
    return float(s.strip().replace(',', '.') or 0)

def read_ldt(path):
    L = open(path, encoding='latin-1').read().splitlines()
    isym, mc, ng = int(num(L[2])), int(num(L[3])), int(num(L[5]))
    lor = num(L[22])
    n = int(num(L[25]))
    i = 26
    lumens = [num(L[i + 2 + 6 * k]) for k in range(n)]  # per set: count, type, lumens, cct, cri, watts
    watts = [num(L[i + 5 + 6 * k]) for k in range(n)]
    nl = [abs(num(L[i + 6 * k])) for k in range(n)]
    i += 6 * n + 10                                  # lamp sets + direct ratios
    cang = [num(x) for x in L[i:i + mc]]; i += mc
    gang = [num(x) for x in L[i:i + ng]]; i += ng
    planes = {0: mc, 1: 1, 2: mc // 2 + 1, 3: mc // 2 + 1, 4: mc // 4 + 1}[isym]
    vals = [num(x) for x in L[i:i + planes * ng]]
    data = [vals[p * ng:(p + 1) * ng] for p in range(planes)]
    k = lumens[0] * (nl[0] or 1) / 1000.0           # cd/klm -> cd
    def plane(c):
        if isym == 1: return data[0]
        if isym == 2:                                # C0-C180 symmetric: stored 0..180
            c = c if c <= 180 else 360 - c
            return data[min(range(len(data)), key=lambda j: abs(cang[j] - c))]
        if isym == 3:                                # C90-C270 symmetric: stored 270..90
            c = (c - 270) % 360
            return data[min(range(len(data)), key=lambda j: abs(((cang[j] - 270) % 360) - c))]
        if isym == 4:
            c = c % 180; c = c if c <= 90 else 180 - c
            return data[min(range(len(data)), key=lambda j: abs(cang[j] - c))]
        return data[min(range(len(data)), key=lambda j: abs(cang[j] - c))]
    def full(a, b):                                  # one diagram line: plane a for gamma 0..180 and plane b mirrored
        return [round(v * k) for v in plane(a)], [round(v * k) for v in plane(b)]
    c0, c180 = full(0, 180); c90, c270 = full(90, 270)
    return {'name': L[8].strip() or os.path.basename(path), 'lm': round(lumens[0] * (nl[0] or 1) * lor / 100), 'w': watts[0],
            'g': gang, 'c0': c0, 'c180': c180, 'c90': c90, 'c270': c270}


def archive_files(url):
    arc = url.split('/')[-1]
    return sorted(f for f in glob.glob(os.path.join('photometry_src', '*', arc, '**', '*'), recursive=True) if f.lower().endswith('.ldt'))

def stem(f):
    return os.path.splitext(os.path.basename(f))[0].upper()

def num_re(n):
    return re.compile(r'(?<![\d.])' + re.escape(n) + r'(?=\s*(?:ø|°|\?|deg|degrees|_|\s|\.ldt|$))', re.I)

REFL_WORDS = {'black high gloss': ['black high gloss', 'black gloss', 'black glossy', 'nero s', 'nero m'], 'black matt': ['black matt', 'nero mat'],
              'silver high gloss': ['silver high gloss', 'silver gloss', 'silver glossy', 'argento'], 'white': ['white', 'bianco'],
              'gold': ['gold', 'oro'], 'chrome': ['chrome', 'cromo', 'silver reflector', 'silver matt'], 'copper': ['copper', 'rame'],
              'silver matt': ['silver matt']}

ESSE = None
def esse_stems():
    global ESSE
    if ESSE is None:
        ESSE = {}
        for f in sorted(glob.glob(os.path.join('photometry_src', 'esse-ci', '**', '*'), recursive=True)):
            if f.lower().endswith('.ldt'): ESSE.setdefault(stem(f), f)
    return ESSE

def pick_esse(code):
    """Esse-Ci names each LDT by its base code (e.g. 14PC15K315); order codes add DALI/finish letters (14PC15K315DW)."""
    st = esse_stems()
    def find(c):
        pre = [k for k in st if c.startswith(k) and len(k) >= len(c) - 5]
        if pre: return st[max(pre, key=len)]
        for cut in range(1, 5):                       # zoom / LV versions: same base, beam suffix in the file name
            base = c[:-cut]
            if len(base) < 6: break
            hit = sorted((k for k in st if k.startswith(base) and 'LV' not in k[len(base):]), key=lambda k: (len(k), k))
            if hit: return st[hit[0]]
        return None
    f = find(code)
    if f: return f, False
    for a, b in (('K4', 'K3'), ('K3', 'K4')):          # same optic, other colour temperature: scaled to this code's lumens
        if a in code:
            f = find(code.replace(a, b, 1))
            if f: return f, True
    return None, False

REFL_ABBR = {'black high gloss': ['bg'], 'black matt': ['bm'], 'silver high gloss': ['sg'], 'white': ['wh'], 'gold': ['go'], 'chrome': ['ch'],
             'copper': ['co'], 'silver matt': ['sm'], 'black': ['bm', 'bg']}

def pick(r, files):
    """Best LDT for a code within its archive(s): beam, colour temperature and reflector must agree where the file names say them;
    power only breaks ties. Returns (file, other_cct_flag)."""
    names = {f: os.path.relpath(f, 'photometry_src').replace('\\', '/').lower() for f in files}
    tests = []
    beam = re.match(r'\s*(\d+(?:\.\d+)?)', r.get('beam') or '')
    if beam:
        bv = float(beam.group(1))
        def bt(n, bv=bv):
            for m in re.finditer(r'(?<![\d.])(\d{1,3}(?:\.\d)?)(?:\s*(?:ø|°|\?|deg|degrees)|_ )', n):
                if abs(float(m.group(1)) - bv) <= 3: return True
            for m in re.finditer(r'_(\d{1,3})(?=_[a-z]{2}\.ldt|\.ldt|_)', n):    # e.g. ..._927_36_BG.ldt
                if m.group(1) not in ('927', '930', '940', '830', '840') and abs(float(m.group(1)) - bv) <= 3: return True
            return False
        def has_beam(n):
            if re.search(r'(?<![\d.])\d{1,3}(?:\.\d)?(?:\s*(?:ø|°|\?|deg|degrees)|_ )', n): return True
            return any(m.group(1) not in ('927', '930', '940', '830', '840') for m in re.finditer(r'_(\d{1,3})(?=_[a-z]{2}\.ldt|\.ldt|_)', n))
        tests.append((bt, has_beam))
    cctv = r.get('model_cct') or ''
    cct = re.match(r'(\d)(\d)00K', cctv) or (re.match(r'(3)(0)', '30') if 'warm dim' in cctv.lower() else None)
    if cct:
        cri = '9' if '90' in (r.get('model_cri') or '') else '8'
        cc = cct.group(1) + cct.group(2)
        pat = re.compile(r'(?<!\d)[89]' + cc + r'(?!\d)|(?<!\d)' + cc + r'00\s*k', re.I)
        pref = re.compile(r'(?<!\d)' + cri + cc + r'(?!\d)')
        tests.append((lambda n, pat=pat: bool(pat.search(n)), 'cct'))
    refl = next((x for x in (r.get('model_details') or '').split(' · ') if 'reflector' in x.lower()), '')
    rk = refl.lower().replace('reflector', '').strip()
    if rk in REFL_WORDS or rk in REFL_ABBR:
        words, ab = REFL_WORDS.get(rk, []), REFL_ABBR.get(rk, [])
        def rt(n, words=words, ab=ab):
            return any(w in n for w in words) or any(re.search(r'[ _]' + a + r'(?:\.ldt|_)', n) for a in ab)
        allw = [w for v in REFL_WORDS.values() for w in v]; alla = [a for v in REFL_ABBR.values() for a in v]
        def hasr(n): return 'reflector' in n or any(re.search(r'[ _]' + a + r'(?:\.ldt|_)', n) for a in alla)
        tests.append((rt, hasr))
    cand = list(files); other = False
    for t, has in tests:
        hit = [f for f in cand if t(names[f])]
        if hit: cand = hit
        elif has == 'cct':                       # measured at another colour temperature only: same optic, lumens scaled to this code
            other = True
            w = [f for f in cand if re.search(r'(?<!\d)[89]30(?!\d)|3000\s*k', names[f])]
            if w: cand = w
        elif any(has(names[g]) for g in cand): return None, False   # the files state this attribute, none for this code's value
    if cct and not other:
        best = [f for f in cand if pref.search(names[f])]
        if best: cand = best
    pw = re.match(r'\s*(\d+(?:\.\d+)?)\s*W', r.get('power') or '')
    if pw and len(cand) > 1:
        pr = re.compile(r'(?<![\d.])' + re.escape(pw.group(1)) + r'\s*w(?![a-z])', re.I)
        best = [f for f in cand if pr.search(names[f])]
        if best: cand = best
    if not cct and len(cand) > 1:                # tuneable white etc.: use the 3000K measurement, then 2700K
        for pat in (r'(?<!\d)[89]30(?!\d)|3000\s*k', r'(?<!\d)[89]27(?!\d)|2700\s*k'):
            w = [f for f in cand if re.search(pat, names[f])]
            if w: cand = w; other = True; break
    if len(set(map(stem, cand))) == 1 or len(cand) == 1: return cand[0], other
    return None, False

def run():
    curves, codes, nomatch = {}, {}, {}
    for r in csv.DictReader(open('products.csv', encoding='utf-8')):
        if not r['code']: continue
        urls = re.findall(r'(?:LDT|IES)=([^;]+)', r['downloads'] or '')
        files = [f for u in urls for f in archive_files(u.strip())]
        if not files: continue
        if 'esse-ci.com' in ''.join(urls): f, other = pick_esse(r['code'].upper())
        else: f, other = pick(r, files)
        if not f:
            nomatch.setdefault(r['family'], 0); nomatch[r['family']] += 1; continue
        cid = re.sub(r'[^a-z0-9]+', '-', os.path.relpath(f, 'photometry_src').lower()).strip('-')
        if cid not in curves:
            try: curves[cid] = read_ldt(f)
            except Exception as e:
                print('unreadable', f, e); continue
        codes[r['code']] = [cid, r['flux']] if other else cid
    # files/photometry/c/<curve>.json (one per LDT) and files/photometry/i/<first 3 chars of code>.json (code -> curve)
    import shutil
    shutil.rmtree('files/photometry', ignore_errors=True)
    os.makedirs('files/photometry/c'); os.makedirs('files/photometry/i')
    for cid, c in curves.items():
        json.dump(c, open(f'files/photometry/c/{cid}.json', 'w'), separators=(',', ':'))
    shards = {}
    for code, v in codes.items():
        shards.setdefault(re.sub(r'[^A-Za-z0-9]', '_', code[:3]).upper(), {})[code] = v
    for k, v in shards.items():
        json.dump(v, open(f'files/photometry/i/{k}.json', 'w'), separators=(',', ':'))
    print(f'photometry: {len(curves)} curves, {len(codes)} codes; no match: {sum(nomatch.values())} codes in {len(nomatch)} families')
    json.dump(nomatch, open('/tmp/photometry_nomatch.json', 'w'), indent=1)

if __name__ == '__main__':
    run()
