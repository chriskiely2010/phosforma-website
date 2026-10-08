# Rebuild the Inground Radius planner page. Run from the site folder: python3 planner_src/build_planner.py
import re,json
svg=open('planner_src/logo.svg').read()
inner=re.search(r'<svg[^>]*>(.*)</svg>',svg,re.S).group(1)
logo=f'<defs><clipPath id="lp"><rect x="0" y="0" width="55.25" height="60"/></clipPath><clipPath id="lf"><rect x="55.25" y="0" width="80" height="60"/></clipPath></defs><g clip-path="url(#lp)" fill="var(--ink)">{inner}</g><g clip-path="url(#lf)" fill="var(--muted)">{inner}</g>'
T=json.load(open('planner_src/table.json'));T={k:v for k,v in T.items() if ('FL56/Nx ' in k or 'FL112/Nx.48V ' in k)}
s=open('planner_src/planner_src.html').read().replace('__TABLE__',json.dumps(T,separators=(',',':'))).replace('__LOGO__',json.dumps(logo))
open('planner/inground-radius/index.html','w').write(s);print(len(s),len(T))
