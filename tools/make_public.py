"""Copy the site into the GitHub repo: public/ = what goes online, tools/ = working files.
Run from the site folder:  python3 make_public.py ../phosforma-website
"""
import os, shutil, sys
repo = sys.argv[1] if len(sys.argv) > 1 else '../phosforma-website'
pub, tools = os.path.join(repo, 'public'), os.path.join(repo, 'tools')
txt = ''.join(open(f, encoding='utf-8').read() for f in ['index.html', 'catalogues.csv', 'partners.csv', 'products.csv'])
shutil.rmtree(pub, ignore_errors=True); os.makedirs(pub)
for f in ['index.html', 'products.csv', 'catalogues.csv', 'partners.csv', 'Phosforma_products_template.csv']:
    if os.path.exists(f) and (f in ('index.html', 'products.csv', 'catalogues.csv', 'partners.csv') or f in txt):
        shutil.copy(f, os.path.join(pub, f))
open(os.path.join(pub, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
# PDFs (datasheets, brochures) live in Cloudflare R2. They are kept in the repo's r2/ folder, which
# is NOT published; the GitHub workflow .github/workflows/r2-sync.yml copies r2/ to the R2 bucket.
# R2_LIVE = True: PDFs only in r2/ and the site links them from R2 (FILES_BASE in index.html).
R2_LIVE = True
r2 = os.path.join(repo, 'r2')
shutil.rmtree(r2, ignore_errors=True); os.makedirs(r2)
n = n2 = 0
for root in ['images', 'files']:
    for r, d, fs in os.walk(root):
        for x in fs:
            p = os.path.join(r, x)
            if p in txt:
                if x.lower().endswith('.pdf'):
                    os.makedirs(os.path.join(r2, r), exist_ok=True); shutil.copy(p, os.path.join(r2, p)); n2 += 1
                    if R2_LIVE: continue
                os.makedirs(os.path.join(pub, r), exist_ok=True); shutil.copy(p, os.path.join(pub, p)); n += 1
if os.path.exists('vendor'): shutil.copytree('vendor', os.path.join(pub, 'vendor'))
shutil.rmtree(tools, ignore_errors=True); os.makedirs(tools)
for f in ['build_csv.py', 'true_scale.py', 'make_public.py', 'tile_sizes.csv', 'Phosforma_products_template.csv', 'README.txt', 'delta_ugr.json', 'load_batches.py', 'prerender.py']:
    if os.path.exists(f): shutil.copy(f, os.path.join(tools, f))
for d in ['data', 'originals', 'archive']:
    if os.path.exists(d): shutil.copytree(d, os.path.join(tools, d))
print(n, 'site files copied to public/,', n2, 'PDFs to r2/', '(R2 live)' if R2_LIVE else '(R2 not live yet)')

# a real page per product (+ sitemap, robots) on top of the copied site
import subprocess
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prerender.py'), repo], check=True)
