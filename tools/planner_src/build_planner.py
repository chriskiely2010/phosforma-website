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
 dict(path='inground-radius-rgb',name='Inground Radius RGB',store='irrgbplan',cct0='RGB_RGB_',rgb=True,ctrl='RGB controller',
      ccts=[['RGB_RGB_','RGB']],
      strips=[dict(id='RGB48/Nx 07W',label='RGB48 24V · 7.2 W/m',v=24,wm=7.2,max=9),
              dict(id='RGB48/Nx 11W',label='RGB48 24V · 11.5 W/m',v=24,wm=11.5,max=6.5)]),
 # RGBW48: MAX RUN chart lists RGBW48/Nx 9.6 W/m at 8 m (the Radius code says RGBW48/NN; same strip assumed - to confirm)
 dict(path='inground-radius-rgbw',name='Inground Radius RGBW',store='irrgbwplan',cct0='RGB_RGB_T930',rgb=True,w=True,ctrl='RGBW controller',
      ccts=[['RGB_RGB_922','2200K'],['RGB_RGB_T927','2700K'],['RGB_RGB_T930','3000K'],['RGB_RGB_T940','4000K']],
      strips=[dict(id='RGBW48/NN 09W',label='RGBW48 24V · 9.6 W/m',v=24,wm=9.6,max=8)]),
 # Pixel: PXL.RGBW96 is not on the MAX RUN chart; 5 m provisional (as other 24V strips of similar W/m) - to confirm
 dict(path='inground-radius-pixel',name='Inground Radius Pixel RGBW',store='irpxplan',cct0='RGBW_RGBW_',rgb=True,w=True,pixel=True,ctrl='pixel controller',
      ccts=[['RGBW_RGBW_','RGBW']],
      strips=[dict(id='PXL.RGBW96/Bx 26W',label='PXL.RGBW96 24V · 26.1 W/m',v=24,wm=26.1,max=5,tbc=True)]),
]
# ---- Esse-Ci interior profiles (Line to Light, interior engine). Values from Esse-Ci brochures TWOS ID 54 and TWOS DISPLAY ID 54
# (fetched 10 Oct 2026). Lumen pairs are [3000K, 4000K]. Code templates: {w} watts, {c} K3/K4; final code = base + D (DALI) + finish.
L6=[1121,1401,1681,1961,2241,2801];L4=[1128,1688,2248,2808];L3=[1121,1401,1681]
def rows(o,e,p,lens,ws,lm3,lm4,tpl,wlab=None):
  return [dict(o=o,e=e,p=p,len=l,w=w,wl=(wlab[i] if wlab else str(w)),lm=[a,b],t=tpl) for i,(l,w,a,b) in enumerate(zip(lens,ws,lm3,lm4))]
LPW=[24,30,36,42,48,60];HPW=[48,60,72,84,96,120];DILP=[36,46,56,66,76,96];DIHP=[60,76,92,108,124,156]
DILPL=['24+12','30+16','36+20','42+24','48+28','60+36'];DIHPL=['48+12','60+16','72+20','84+24','96+28','120+36'];PCW=[44,66,88,110]
PC3=[6600,9900,13200,16500];PC4=[7060,10560,14080,17600]
TWOS=(rows('DK','D','LP',L6,LPW,[2654,3316,3978,4641,5304,6628],[2790,3486,4182,4878,5573,6965],'54DK{w}{c}')
 +rows('DK','DI','LP',L6,DILP,[4059,5189,6319,7451,8582,10843],[4460,5472,6665,7858,9049,11435],'54DI{w}DK{c}',DILPL)
 +rows('CLD','D','LP',L6,LPW,[2877,3595,4314,5032,5749,7182],[2966,3707,4448,5188,5928,7405],'54CLD{w}{c}')
 +rows('CLD','D','HP',L6,HPW,[5255,6520,7883,9195,10505,13128],[5418,6722,8127,9480,10831,13538],'54CLD{w}{c}HP')
 +rows('CLD','DI','LP',L6,DILP,[4277,5465,6653,7840,9029,11405],[4451,5687,6923,8160,9396,11869],'54DI{w}CLD{c}',DILPL)
 +rows('CLD','DI','HP',L6,DIHP,[6648,8420,10193,11966,13739,17284],[6897,8736,10575,12414,14253,17932],'54DI{w}CLD{c}HP',DIHPL)
 +rows('PG','D','LP',L6,LPW,[2824,3530,4235,4940,5647,7059],[2912,3640,4367,5095,5819,7273],'54PG{w}{c}')
 +rows('PG','D','HP',L6,HPW,[5217,6521,7824,9129,10433,13041],[5379,6723,8068,9413,10757,13447],'54PG{w}{c}HP')
 +rows('PG','DI','LP',L6,DILP,[4225,5398,6527,7745,8919,11266],[4398,5619,6840,8062,9284,11727],'54DI{w}PG{c}',DILPL)
 +rows('PG','DI','HP',L6,DIHP,[6538,8281,10024,11767,13511,16997],[6786,8595,10405,12214,14024,17643],'54DI{w}PG{c}HP',DIHPL)
 +rows('PC60','D','HP',L4,PCW,PC3,PC4,'54PC{w}{c}60')+rows('PC110','D','HP',L4,PCW,PC3,PC4,'54PC{w}{c}110')+rows('AS','D','HP',L4,PCW,PC3,PC4,'54AS{w}{c}'))
DISPLAY=(rows('DK','D','LP',L6,LPW,[2654,3316,3978,4641,5304,6628],[2790,3486,4182,4878,5573,6965],'54DK{w}{c}R')
 +rows('CLD','D','LP',L6,LPW,[2877,3595,4314,5032,5749,7182],[2966,3707,4448,5188,5928,7405],'54CLD{w}{c}R')
 +rows('CLD','D','HP',L3,[48,60,72],[5255,6520,7883],[5418,6722,8127],'54CLD{w}{c}HPR')
 +rows('PG','D','LP',L6,LPW,[2824,3530,4235,4940,5647,7059],[2912,3640,4367,5095,5819,7273],'54PG{w}{c}R')
 +rows('PG','D','HP',L3,[48,60,72],[5217,6521,7824],[5379,6723,8068],'54PG{w}{c}HPR')
 +rows('AS','D','HP',L4,PCW,PC3,PC4,'54AS{w}{c}R'))
OPTICS=[dict(id='DK',name='DK microcell, 60°',ugr='UGR<16'),dict(id='CLD',name='CLD collimated diffuser',ugr='UGR<19'),dict(id='PG',name='PG satin diffuser',ugr='UGR<22'),
        dict(id='PC60',name='PC lens 60° (low glare)',ugr='UGR<19'),dict(id='PC110',name='PC lens 110° (extra wide)',ugr='UGR<22'),dict(id='AS',name='Asymmetric wall-washer lens',ugr='')]
PRODUCTS+=[
 dict(kind='interior',path='twos',name='Twos',brand='Esse-Ci',store='twosplan',mount='suspended',cct0='K3',ccts=[['K3','3000K'],['K4','4000K']],
      optics=OPTICS,bodies=TWOS,sec=dict(w=43,h=63),junction=81,perCircuit=25,
      acc=dict(joint='54AA11',j2='54AA05',j3='54AA06',j4='54AA07',caps='54AA09',susp='54AA13',susp3='54AA1330'),strips=[]),
 dict(kind='interior',path='twos-display',name='Twos Display',brand='Esse-Ci',store='twosdplan',mount='recessed',cct0='K3',ccts=[['K3','3000K'],['K4','4000K']],
      optics=[o for o in OPTICS if o['id'] in ('DK','CLD','PG','AS')],bodies=DISPLAY,sec=dict(w=43,h=57,flange=58),junction=81,perCircuit=25,
      acc=dict(joint='54AA11',caps='54AA09R'),strips=[]),
]
src=open('planner_src/planner_src.html').read()
for P in PRODUCTS:
  ids=[x['id'] for x in P['strips']]
  T={k:v for k,v in TABLE.items() if any(f'|{i} ' in k for i in ids)} if ids else {}
  out=src.replace('__TABLE__',json.dumps(T,separators=(',',':'))).replace('__LOGO__',json.dumps(logo)).replace('__PRODUCT__',json.dumps(P,ensure_ascii=False)).replace('__NAME__',P['name']).replace('__BRAND__',P.get('brand','Holectron')).replace('__SPLITS__','fills each straight with catalogue bodies and junctions' if P.get('kind')=='interior' else 'splits feeds by maximum run').replace('__NOTE__',
   ("Bodies, codes, power and light output are Esse-Ci's published values. Turns are 90° corner junctions; lines that meet form 3- and 4-way junctions. Accessories marked 'to confirm' are Phosforma's reading of the installation guide. A planning drawing, subject to Phosforma confirmation." if P.get('kind')=='interior' else
    "Pieces, codes, power and light output are Holectron's published values. Curves are laid either way; pieces join with male/female connectors in the chamber. The model follows the specification sheet section and is a planning drawing, subject to Phosforma confirmation."))
  os.makedirs(f"planner/{P['path']}",exist_ok=True);open(f"planner/{P['path']}/index.html",'w').write(out);print(P['path'],len(out),len(T))
