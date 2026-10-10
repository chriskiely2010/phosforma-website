# Build the Line to Light planner pages, one per product, from one source.
# Run from the site folder: python3 planner_src/build_planner.py
import re,json,os
svg=open('planner_src/logo.svg').read()
inner=re.search(r'<svg[^>]*>(.*)</svg>',svg,re.S).group(1)
logo=f'<defs><clipPath id="lp"><rect x="0" y="0" width="55.25" height="60"/></clipPath><clipPath id="lf"><rect x="55.25" y="0" width="80" height="60"/></clipPath></defs><g clip-path="url(#lp)" fill="var(--ink)">{inner}</g><g clip-path="url(#lf)" fill="var(--muted)">{inner}</g>'
TABLE=json.load(open('planner_src/table.json'))
# max run from one side: Holectron Inground Radius specification sheet, MAX RUN chart
PRODUCTS=[
 dict(path='inground-radius',name='Inground Radius',store='irplan',cct0='T930',rgb=False,
      ccts=[['922','2200K'],['T927','2700K'],['T930','3000K'],['T940','4000K']],
      strips=[dict(id='FL112/Nx.48V 09W',label='FL112 48V · 9.6 W/m',v=48,wm=9.6,max=22.5),
              dict(id='FL112/Nx.48V 04W',label='FL112 48V · 4.8 W/m',v=48,wm=4.8,max=28.5),
              dict(id='FL56/Nx 09W',label='FL56 24V · 9.6 W/m',v=24,wm=9.6,max=7.5),
              dict(id='FL56/Nx 04W',label='FL56 24V · 4.8 W/m',v=24,wm=4.8,max=13),
              dict(id='FL56/Nx 02W',label='FL56 24V · 2.4 W/m',v=24,wm=2.4,max=18.5)]),
 dict(path='inground-radius-rgb',name='Inground Radius RGB',store='irrgbplan',cct0='RGB_RGB_',rgb=True,
      ccts=[['RGB_RGB_','RGB']],
      strips=[dict(id='RGB48/Nx 07W',label='RGB48 24V · 7.2 W/m',v=24,wm=7.2,max=9),
              dict(id='RGB48/Nx 11W',label='RGB48 24V · 11.5 W/m',v=24,wm=11.5,max=6.5)]),
]
src=open('planner_src/planner_src.html').read()
for P in PRODUCTS:
  ids=[x['id'] for x in P['strips']]
  T={k:v for k,v in TABLE.items() if any(f'|{i} ' in k for i in ids)}
  out=src.replace('__TABLE__',json.dumps(T,separators=(',',':'))).replace('__LOGO__',json.dumps(logo)).replace('__PRODUCT__',json.dumps(P,ensure_ascii=False)).replace('__NAME__',P['name'])
  os.makedirs(f"planner/{P['path']}",exist_ok=True);open(f"planner/{P['path']}/index.html",'w').write(out);print(P['path'],len(out),len(T))
