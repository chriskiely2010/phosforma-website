"""Photometric curves for the generated PDF datasheets.

Reads EULUMDAT (.ldt) files under photometry_src/ and writes files/photometry/photometry.json:
  {"curves": {id: {name, lm, w, g:[gamma...], c0:[cd...], c90:[cd...]}}, "codes": {code: id}}
c0 = C0-C180 plane, c90 = C90-C270 plane, both as absolute candela from gamma 0 (straight down) to 180.
Codes are matched by family, colour temperature and reflector (see match()).
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

FOLDERS = {'Dea Vesta M PE': 'Dea-Vesta-M-PE-LDT', 'Dea Vesta M PE-in': 'Dea-Vesta-M-PE-in-LDT',
           'Dea Vesta S PE': 'Dea-Vesta-S-PE-LDT', 'Dea Vesta S PE-in': 'Dea-Vesta-S-PE-in-LDT',
           'Dea Eros M PE': 'Dea-Eros-M-PE-LDT', 'Dea Eros M PE-in': 'Dea-Eros-M-PE-in-LDT',
           'Dea Eros S PE': 'Dea-Eros-S-PE-LDT', 'Dea Eros S PE-in': 'Dea-Eros-S-PE-in-LDT', 'Perla': 'Perla-LDT'}
CCT = {'2700K': '927', '3000K': '930', '4000K': '940', 'Warm Dim': '930'}
REFL = {'gold': ['gold'], 'black high gloss': ['black gloss'], 'black matt': ['black matt'],
        'silver high gloss': ['silver gloss'], 'white': ['white'], 'chrome': ['chrome', 'silver reflector', 'silver matt']}

def match(fam, cct, refl, files):
    c = CCT.get(cct)
    if not c: return None
    cand = [f for f in files if re.search(r'[ _]' + c + r'[ _]', os.path.basename(f).replace('-', '_'))]
    if not cand: return None
    if fam.startswith('Dea Vesta'):
        r = refl.lower().replace(' reflector', '').strip()
        for key in REFL.get(r, []):
            hit = [f for f in cand if key in os.path.basename(f).lower().replace('glossy', 'gloss')]
            if hit: return hit[0]
        return None                                  # no file for this reflector (e.g. copper)
    return cand[0]

def run():
    curves, codes = {}, {}
    for fam, folder in FOLDERS.items():
        files = sorted(glob.glob(os.path.join('photometry_src', folder, '**', '*.ldt'), recursive=True))
        for r in csv.DictReader(open('products.csv', encoding='utf-8')):
            if r['family'] != fam or not r['code']: continue
            refl = next((s for s in r['model_details'].split(' · ') if 'eflector' in s), '')
            f = match(fam, r['model_cct'], refl, files)
            if not f: continue
            cid = re.sub(r'[^a-z0-9]+', '-', os.path.relpath(f, 'photometry_src').lower()).strip('-')
            if cid not in curves: curves[cid] = read_ldt(f)
            codes[r['code']] = cid
    os.makedirs('files/photometry', exist_ok=True)
    json.dump({'curves': curves, 'codes': codes}, open('files/photometry/photometry.json', 'w'), separators=(',', ':'))
    print(f'photometry: {len(curves)} curves, {len(codes)} codes')

if __name__ == '__main__':
    run()
