"""Merge the 2026-10-03 Karizma Luce batch sheets into data/karizma_luce.csv.

- Strips Datasheet= downloads (datasheets come in a later pass).
- Splits multi-size families into one product per size ("Casa XS", "Casa M Alto"),
  each with its own thumbnail copy, dimension drawing, dimension note and cut-out.
- Copies the batch images into images/<slug>/ and adds outer sizes to tile_sizes.csv.
"""
import csv, json, os, re, shutil, sys

BASE = '/mnt/user-data/uploads/Downloads/Website Dont Delete'
SKIP = {'Piccolo'}                      # phased out (user asked to remove it)
names = [n for n in json.load(open('/tmp/claude-0/names.json')) if n not in SKIP]

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def size_of(family, model):
    return re.sub(r'\s+[\d.]+W\b.*$', '', model[len(family):]).strip() if model.startswith(family) else ''

def note_for(note, size, sizes):
    """Pick this size's segment out of 'XS Ø45 × 66mm · S Ø57 × 81mm · M Alto ...'."""
    for seg in note.split(' · '):
        seg = seg.strip()
        # longest size token that prefixes the segment
        best = max((s for s in sizes if seg.startswith(s + ' ')), key=len, default=None)
        if best == size: return re.sub(r'\s+', ' ', seg[len(size):]).strip()
    return ''

def cutout_for(spec, size):
    m = re.search(r'Cut-out ([^.]*)\.', spec)
    if not m: return ''
    for part in m.group(1).split(' | '):
        mm = re.match(r'\s*(.+?)\s*\((.+?)\)\s*$', part)
        if mm and mm.group(2).strip() == size: return mm.group(1)
    return ''

def outer_mm(note):
    m = re.search(r'Ø\s*([\d.]+)', note)
    if m: return float(m.group(1))
    nums = [float(x) for x in re.findall(r'[\d.]+(?=\s*(?:×|mm))', note)]
    return max(nums[:2]) if nums else None

cols = None; out = []; tiles = []; report = []
for n in names:
    d = f'{BASE}/Batch 2026-10-03 Karizma Luce - {n}'
    rows = list(csv.DictReader(open(f'{d}/02 Sheet/karizma_luce.csv', encoding='utf-8-sig')))
    cols = cols or list(rows[0].keys())
    fam = rows[0]['family']; fslug = slug(fam)
    src = f'{d}/03 Site files/{fslug}'
    dst = f'images/{fslug}'; os.makedirs(dst, exist_ok=True)
    for fn in os.listdir(src):
        p = os.path.join(src, fn)
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(dst, fn))
            o = os.path.join('originals', dst, fn)       # fresh source for true_scale
            if os.path.exists(o): os.remove(o)
    head = {k: rows[0][k] for k in cols[:19]}
    for r in rows:
        r['downloads'] = ';'.join(x for x in r['downloads'].split(';') if x and not x.startswith('Datasheet='))
    sizes = []
    for r in rows:
        s = size_of(fam, r['model'])
        if s not in sizes: sizes.append(s)
    thumb = f'{dst}/{fslug}-thumb.jpg'
    if len(sizes) <= 1:
        first = True
        for r in rows:
            if not first:
                for k in cols[:19]: r[k] = r[k] if k == 'family' else ''
            first = False; out.append(r)
        mm = outer_mm(head['dimensions_note'])
        tiles.append((fam, mm)); report.append((fam, len(rows), mm, head['dimensions_note']))
        continue
    tag = head['tagline']
    for s in sizes:
        sub = [r for r in rows if size_of(fam, r['model']) == s]
        nf = f'{fam} {s}'
        note = note_for(head['dimensions_note'], s, sizes)
        cut = cutout_for(head['specification'], s)
        full_note = note + (f' · cut-out {cut}' if cut and 'cut-out' not in note else '')
        dim = f'{dst}/{fslug}-dimensions-{slug(s)}.png'
        if not os.path.exists(dim): dim = ''
        sthumb = f'{dst}/{fslug}-{slug(s)}-thumb.jpg'
        shutil.copy2(thumb, sthumb)
        o = os.path.join('originals', sthumb)
        if os.path.exists(o): os.remove(o)
        ntag = re.sub(r'\s*·\s*\d+ sizes', f' · cut-out {cut}' if cut else '', tag)
        for i, r in enumerate(sub):
            r['family'] = nf
            if i == 0:
                for k in cols[:19]:
                    if k != 'family': r[k] = head[k]
                r['tagline'] = ntag
                r['images'] = ';'.join(x for x in [sthumb, dim] if x)
                r['dimensions'] = dim; r['dimensions_note'] = full_note
            else:
                for k in cols[1:19]: r[k] = ''
            out.append(r)
        mm = outer_mm(note)
        tiles.append((nf, mm)); report.append((nf, len(sub), mm, full_note + ('' if dim else '  [no drawing]')))

# trimless-only products carry TR at the end of the title
for f in {r['family'] for r in out}:
    fr = [r for r in out if r['family'] == f]
    if all(r['model_finish'] == 'Trimless' for r in fr) and not f.endswith(' TR'):
        for r in fr: r['family'] = f + ' TR'
        tiles[:] = [(f + ' TR' if a == f else a, b) for a, b in tiles]

# existing data minus the families these batches replace (old Dea Carmenta S)
cur = list(csv.DictReader(open('data/karizma_luce.csv', encoding='utf-8-sig')))
new_f = {r['family'] for r in out}
old_carm = next((r for r in cur if r['family'] == 'Dea Carmenta S' and r['tagline']), None)
cur = [r for r in cur if r['family'] not in new_f]
if old_carm and old_carm.get('slides'):
    for r in out:
        if r['family'] == 'Dea Carmenta S' and r['tagline']: r['slides'] = old_carm['slides']; r['slide_tag'] = old_carm['slide_tag']
allc = list(cur[0].keys())
with open('data/karizma_luce.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=allc); w.writeheader()
    w.writerows(cur); w.writerows({c: r.get(c, '') for c in allc} for r in out)

t = list(csv.DictReader(open('tile_sizes.csv', encoding='utf-8-sig')))
have = {r['family'] for r in t}
t = [r for r in t if r['family'] not in new_f or r['family'] in ('Dea Carmenta S',)]
have = {r['family'] for r in t}
for fam, mm in tiles:
    if mm and fam not in have: t.append({'family': fam, 'size': '', 'diameter_mm': f'{mm:g}', 'thumb': 'yes'})
    elif mm and fam in have:
        for r in t:
            if r['family'] == fam: r['diameter_mm'] = f'{mm:g}'
with open('tile_sizes.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['family', 'size', 'diameter_mm', 'thumb']); w.writeheader(); w.writerows(t)

print(len(out), 'rows,', len(new_f), 'products; data now', len(cur) + len(out), 'rows')
for x in report: print(' ', x)
