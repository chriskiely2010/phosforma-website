"""Write a real HTML page for every product: public/products/<slug>/index.html.

Each page is the normal site (same index.html, same script) with the product already
rendered inside <main id="app">, plus its own title, description, share image, canonical
link and Google product data. Visitors see no difference; search engines and link
previews get a proper page per product.

Run after make_public.py:  python3 prerender.py <repo>

GO-LIVE SWITCH: set LIVE = True (and check SITE_URL) when phosforma.com.au points here.
While LIVE is False every page keeps 'noindex' and robots.txt blocks crawlers, so the
test site on pages.dev never competes with the real domain in Google.
"""
import html, json, os, re, shutil, socket, subprocess, sys, time, xml.sax.saxutils as sx

LIVE = False
SITE_URL = 'https://www.phosforma.com.au'

repo = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/phosforma-website'
pub = os.path.join(repo, 'public')
src = open(os.path.join(pub, 'index.html'), encoding='utf-8').read()

# ---- 1. render every product page in a headless browser --------------------------
port = 8790
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '-d', pub],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(50):
    try: socket.create_connection(('127.0.0.1', port), 0.2).close(); break
    except OSError: time.sleep(0.1)
js = r"""
const {chromium}=require('playwright');(async()=>{
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1300,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
const base='http://127.0.0.1:%d';
await p.goto(base+'/#all');await p.waitForSelector('a.card');
const slugs=[...new Set(await p.$$eval('a.card',a=>a.map(x=>x.getAttribute('href').match(/\/products\/([^/]+)\//)[1])))];
const out=[];
for(const s of slugs){
  await p.goto(base+'/#p-'+s);await p.waitForFunction(s=>location.pathname==='/products/'+s+'/'&&document.querySelector('#app h1'),s);
  out.push(await p.evaluate(()=>{const app=document.querySelector('#app');
    const img=[...app.querySelectorAll('img')].map(i=>i.getAttribute('src')).find(x=>x&&!x.startsWith('data:'))||'';
    const t=s=>(document.querySelector(s)?.textContent||'').trim();
    return {slug:location.pathname.split('/')[2],title:document.title,desc:document.querySelector('meta[name=description]').content,
      name:t('#app h1'),img,html:app.innerHTML};}));
}
require('fs').writeFileSync(process.argv[2],JSON.stringify({out,errs}));await b.close();})();
""" % port
tmp = '/tmp/claude-0/prerender'; os.makedirs(tmp, exist_ok=True)
open(f'{tmp}/r.js', 'w').write(js)
try:
    subprocess.run(['node', f'{tmp}/r.js', f'{tmp}/out.json'], check=True, cwd='/tmp/claude-0')
finally:
    srv.terminate()
res = json.load(open(f'{tmp}/out.json'))
if res['errs']: print('page errors:', res['errs'][:5])

# ---- 2. write the pages ----------------------------------------------------------
def head_for(r):
    url = f"{SITE_URL}/products/{r['slug']}/"
    img = f"{SITE_URL}/{r['img']}" if r['img'] else ''
    e = lambda s: html.escape(s, quote=True)
    ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': r['name'],
          'description': r['desc'], 'url': url}
    if img: ld['image'] = img
    brand = r['title'].split(' | ')[1] if r['title'].count(' | ') >= 2 else ''
    if brand: ld['brand'] = {'@type': 'Brand', 'name': brand}
    return (f'<link rel="canonical" href="{e(url)}">\n'
            f'<meta property="og:type" content="product">\n<meta property="og:site_name" content="Phosforma">\n'
            f'<meta property="og:title" content="{e(r["title"])}">\n<meta property="og:description" content="{e(r["desc"])}">\n'
            f'<meta property="og:url" content="{e(url)}">\n' + (f'<meta property="og:image" content="{e(img)}">\n' if img else '') +
            '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>\n')

def page(base_html, r):
    h = base_html
    h = re.sub(r'<title>.*?</title>', f'<title>{html.escape(r["title"])}</title>', h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{html.escape(r["desc"], quote=True)}">\n' + head_for(r), h, count=1)
    h = h.replace('<main id="app" aria-live="polite"></main>', f'<main id="app" aria-live="polite">{r["html"]}</main>', 1)
    return h

base = src if not LIVE else src.replace('<meta name="robots" content="noindex, nofollow">\n', '')
if LIVE:
    open(os.path.join(pub, 'index.html'), 'w', encoding='utf-8').write(base)
pdir = os.path.join(pub, 'products')
shutil.rmtree(pdir, ignore_errors=True)
for r in res['out']:
    d = os.path.join(pdir, r['slug']); os.makedirs(d)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page(base, r))

# ---- 3. sitemap + robots ---------------------------------------------------------
urls = [f'{SITE_URL}/'] + [f"{SITE_URL}/products/{r['slug']}/" for r in res['out']]
open(os.path.join(pub, 'sitemap.xml'), 'w').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{sx.escape(u)}</loc></url>\n' for u in urls) + '</urlset>\n')
open(os.path.join(pub, 'robots.txt'), 'w').write(
    f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n' if LIVE else
    '# Pre-launch: keep the test site out of search engines. prerender.py sets this when LIVE = True.\nUser-agent: *\nDisallow: /\n')
print(f"{len(res['out'])} product pages written, sitemap {len(urls)} urls, LIVE={LIVE}")
