"""Build ceiling-section banner slides for recessed downlights from side renders.

slide_sources.csv lists family, render (transparent side view) and output path.
Each output is made with slide_recessed.make() and written into the family's
`slides` column in data/*.csv (first row of the family), then run build_csv.py.
"""
import csv, glob
from slide_recessed import make
src = list(csv.DictReader(open('slide_sources.csv')))
by = {}
for r in src:
    try:
        make(r['render'], r['out'], linefrac=float(r['line']) if r.get('line') else None); by.setdefault(r['family'], []).append(r['out'])
    except Exception as e:
        print('FAILED', r['family'], e)
for path in glob.glob('data/*.csv'):
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig'))); cols = list(rows[0].keys()); hit = False
    for r in rows:
        if r['family'] in by and r['tagline']:
            r['slides'] = ';'.join(by[r['family']]); hit = True
    if hit:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print('slides:', {k: len(v) for k, v in by.items()})
