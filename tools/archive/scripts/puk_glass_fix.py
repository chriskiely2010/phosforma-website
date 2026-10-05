import numpy as np, glob, os, shutil
from PIL import Image, ImageDraw, ImageFilter
P={
 'boulevard/boulevard-01-180':[[(220,250),(250,262),(283,293),(330,304),(400,316),(470,322),(520,320),(560,310),(578,298),(584,300),(582,335),(545,382),(500,402),(450,416),(400,426),(300,426),(250,412),(224,392),(218,360)]],
 'boulevard/boulevard-01-360':[[(212,225),(250,251),(300,272),(350,283),(400,287),(450,282),(500,268),(550,250),(588,226),(589,368),(560,380),(500,381),(450,378),(400,372),(350,377),(300,381),(240,380),(211,368)]],
 'boulevard/boulevard-02-180':[[(314,145),(320,148),(345,155),(370,160),(400,165),(430,169),(455,170),(475,167),(485,161),(488,166),(486,180),(472,200),(445,211),(400,219),(360,218),(332,212),(318,200),(313,180)]],
 'boulevard/boulevard-02-360':[[(311,122),(330,131),(345,139),(370,145),(400,148),(430,145),(455,139),(472,131),(488,122),(489,193),(460,193),(430,190),(400,187),(370,189),(350,192),(311,193)]],
 'boulevard/boulevard-03-180':[[(344,108),(365,114),(400,119),(432,122),(456,120),(457,132),(450,137),(440,142),(420,149),(400,154),(370,156),(352,153),(344,148)]],
 'boulevard/boulevard-03-360':[[(346,109),(370,114),(400,118),(430,114),(454,108),(454,148),(440,147),(420,146),(400,144),(380,146),(370,147),(346,148)]],
 'tron/tron-180':[[(369,289),(548,289),(549,350),(546,368),(535,385),(515,398),(480,408),(440,415),(400,417),(369,418)]],
 'tron/tron-360':[[(249,277),(358,277),(358,420),(340,419),(300,410),(265,398),(250,385),(247,360)],[(430,280),(550,280),(551,350),(548,372),(535,390),(510,403),(470,413),(430,419)]],
}
def mask(polys,ell=None):
    m=Image.new('L',(800,800),0);d=ImageDraw.Draw(m)
    for p in polys: d.polygon(p,fill=255)
    if ell: d.rounded_rectangle(ell,radius=28,fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2))
M={k:mask(v) for k,v in P.items()}
M['coiny-bollard/coiny-bollard']=mask([],(254,121,376,213))
def run(apply=False):
    prev=[]
    for k,m in M.items():
        orig=Image.open(k+'-white-aluminium.jpg').convert('RGB')
        for fin in ['anthracite-grey','black','matt-black']:
            p=f'{k}-{fin}.jpg'
            if not os.path.exists(p): continue
            bak=f'/tmp/claude-0/glass/bak/{p.replace("/","__")}'
            if not os.path.exists(bak): shutil.copy(p,bak)
            rec=Image.open(bak).convert('RGB')
            out=Image.composite(orig,rec,m)
            if apply: out.save(p,quality=90,optimize=True)
            prev.append((k,fin,rec,out))
    return prev
