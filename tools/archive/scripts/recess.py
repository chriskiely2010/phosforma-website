import numpy as np, cv2, os, sys, json, shutil
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'/home/claude/site/archive/scripts'); from photo2 import save_jpg
from rec import load, lower, fit, resid
SITE='/home/claude/site/'
def src(name):
    o=SITE+'originals/images/make/'+name
    return o if os.path.exists(o) else SITE+'images/make/'+name
def emask(shape,e,shrink=1.0,ss=4):
    H,W=shape; m=np.zeros((H*ss,W*ss),np.uint8)
    (cx,cy),(w,h),ang=e
    cv2.ellipse(m,((cx*ss+ss/2-0.5,cy*ss+ss/2-0.5),((w-2*shrink)*ss,(h-2*shrink)*ss),ang),255,-1)
    return cv2.resize(m,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
def opening_fit(a,m):
    L=a.mean(-1); dark=(L<90)&m; light=ndimage.binary_closing((L>150)&m,iterations=6)
    lab0,n0=ndimage.label(light); sz0=ndimage.sum(light,lab0,range(1,n0+1)); fl=lab0==(np.argmax(sz0)+1)
    hull=cv2.convexHull(np.stack(np.where(fl)[::-1],1).astype(np.int32)); H=np.zeros(m.shape,np.uint8); cv2.fillConvexPoly(H,hull,1)
    enc=ndimage.binary_erosion(H>0,iterations=2)&dark
    lab,n=ndimage.label(enc); sz=ndimage.sum(enc,lab,range(1,n+1)); k=np.argmax(sz)+1
    cs,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    return cv2.fitEllipse(max(cs,key=len))
def place(img,E,dst):
    a=img*E[...,None]+204*(1-E[...,None])
    ys,xs=np.where(E>0.5); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    side=(x1-x0)/0.8; cx,cy=(x0+x1)/2,(y0+y1)/2
    c=Image.new('RGB',(round(side),round(side)),(204,204,204))
    c.paste(Image.fromarray(np.clip(a,0,255).round().astype(np.uint8)),(round(side/2-cx),round(side/2-cy)))
    save_jpg(c.resize((800,800),Image.LANCZOS),dst)
def bbox(m):
    ys,xs=np.where(m); return xs.min(),xs.max(),ys.max()
LOG={}
RATIO={}
RATIO_W=json.load(open('ratio.json')) if os.path.exists('ratio.json') else {}
names=sorted(f for f in os.listdir(SITE+'images/make') if f.endswith('.jpg') and 'double' not in f and 'banner' not in f and 'dimension' not in f and 'thumb' not in f)
fl_black={}
OUT='/tmp/claude-0/rec/out/'; os.makedirs(OUT,exist_ok=True)
for n in sorted(names,key=lambda s:('white' in s, 'fl-mini' in s)):   # black first (white deep-pro-fl borrows its ellipse)
    p=src(n); a,d,m=load(p)
    if 'deep-pro-fl' in n:
        if 'black' in n and 'fl-mini' not in n:
            e=opening_fit(a,m); (cx,cy),(w,h),ang=e
            sx,sy=(h/2,w/2) if abs(ang-90)<45 else (w/2,h/2); yb=cy+sy; sy=0.40*sx
            e=((cx,yb-sy),(2*sx,2*sy),0.0); fl_black[n.replace('-black','')]=(e,bbox(m))
        else:
            ref=n.replace('-white','').replace('-black','').replace('fl-mini','fl-micro') if 'fl-mini-black' in n else n.replace('-white','')
            (cx,cy),(w,h),ang=fl_black[ref][0]; bx0,bx1,by=fl_black[ref][1]
            x0,x1,yb=bbox(m); s=(x1-x0)/(bx1-bx0)
            e=((x0+(cx-bx0)*s, yb-(by-cy)*s),(w*s,h*s),ang)
            if 'black' in n: fl_black[n.replace('-black','')]=(e,bbox(m))
    else:
        xs,ys=lower(m); e,inl=fit(xs,ys)
        (cx,cy),(w,h),ang=e; a_=min(w,h)/2 if abs(ang-90)<20 else w/2; bh=max(w,h)/2 if abs(ang-90)<20 else h/2
        # cv2 returns (w,h) with ang~90 meaning w is vertical axis
        semi_x,semi_y=(h/2,w/2) if abs(ang-90)<20 else (w/2,h/2)
        yb=cy+semi_y
        key=n.replace('-black','').replace('-white','')
        if 'deep-pro' not in n: e=((cx,cy),(w,h),ang)
        elif 'white' in n:
            L=a.mean(-1); band=np.zeros_like(m); band[:,int(cx-0.25*semi_x):int(cx+0.25*semi_x)]=True
            wt=(L>185)&m; lab2,n2=ndimage.label(wt); sz2=ndimage.sum(wt,lab2,range(1,n2+1)); wt=lab2==(np.argmax(sz2)+1)
            wy=np.where((wt&band).any(1))[0]; yt=wy.min()
            semi_y=(yb-yt)/2; RATIO[key]=semi_y/semi_x
        elif key in RATIO_W: semi_y=semi_x*RATIO_W[key]
        if 'deep-pro' in n: semi_y*=0.985; cy=yb-semi_y; e=((cx,cy),(2*semi_x,2*semi_y),0.0)
        if 'make-fl' in n: (cx,cy),(w,h),ang=e; k=0.985; e=((cx,cy),(w*k,h*k),ang)
        if 'make-fl' in n and 'medium-white' in n:
            (cx,cy),(w,h),ang=e; sx,sy=(h/2,w/2) if abs(ang-90)<45 else (w/2,h/2); yb=cy+sy; sy*=0.90; sx*=0.965; sy*=0.965; e=((cx,yb-sy),(2*sx,2*sy),0.0)
    LOG[n]=[round(float(v),1) for v in (*e[0],*e[1],e[2])]
    place(a,emask(m.shape,e),OUT+n)
json.dump(RATIO,open('ratio.json','w'));json.dump(LOG,open('log.json','w'),indent=0); print(len(LOG))
