import numpy as np, cv2, sys, json
from PIL import Image, ImageDraw
from scipy import ndimage
def load(p):
    a=np.asarray(Image.open(p).convert('RGB'),np.float32)
    d=np.abs(a-204).max(-1); m=ndimage.binary_opening(d>12,iterations=1)
    lab,n=ndimage.label(m); sz=ndimage.sum(m,lab,range(1,n+1)); m=np.isin(lab,[k+1 for k,v in enumerate(sz) if v>=100])
    return a,d,m
def lower(m):
    xs=np.where(m.any(0))[0]; ys=np.array([np.where(m[:,x])[0].max() for x in xs])
    return xs,ys
def fit(xs,ys,iters=3000,thr=1.5,seed=0):
    rng=np.random.default_rng(seed); P=np.stack([xs,ys],1).astype(np.float32); best=(0,None)
    for _ in range(iters):
        idx=np.sort(rng.choice(len(P),6,replace=False))
        try: e=cv2.fitEllipse(P[idx])
        except: continue
        (cx,cy),(w,h),ang=e
        if not(10<w<2000 and 10<h<2000): continue
        r=resid(P,e); inl=(r<thr)
        # must be lower arc: points below centre
        sc=inl.sum()
        if sc>best[0]: best=(sc,e)
    e=best[1]; inl=resid(P,e)<thr
    e=cv2.fitEllipse(P[inl]); return e,inl
def resid(P,e):
    (cx,cy),(w,h),ang=e; t=np.deg2rad(ang); c,s=np.cos(t),np.sin(t)
    x=P[:,0]-cx; y=P[:,1]-cy; u=x*c+y*s; v=-x*s+y*c
    a,b=w/2,h/2; r=np.sqrt((u/a)**2+(v/b)**2)
    return np.abs(r-1)*min(a,b)
if __name__=='__main__':
    out=[]
    for p in sys.argv[1:]:
        a,d,m=load(p); xs,ys=lower(m); e,inl=fit(xs,ys)
        im=Image.fromarray(a.astype(np.uint8)); dr=ImageDraw.Draw(im)
        mask=np.zeros(m.shape,np.uint8); cv2.ellipse(mask,(tuple(map(float,e[0])),tuple(map(float,e[1])),float(e[2])),1,1)
        im=np.asarray(im).copy(); im[mask>0]=(255,0,0)
        for x,y,k in zip(xs,ys,inl):
            if k: im[y,x]=(0,255,0)
        out.append(Image.fromarray(im).resize((400,400)))
        print(p.split('/')[-1],[round(v,1) for v in (*e[0],*e[1],e[2])],inl.sum(),len(xs))
    sh=Image.new('RGB',(400*min(4,len(out)),400*((len(out)+3)//4)))
    for i,o in enumerate(out): sh.paste(o,((i%4)*400,(i//4)*400))
    sh.save('fit.jpg')
