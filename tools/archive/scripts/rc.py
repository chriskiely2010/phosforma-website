import numpy as np, colorsys, sys
from PIL import Image, ImageFilter
SRC='/home/claude/site/images/inground-radius/'
def hsv(a):
    a=a/255.;mx=a.max(2);mn=a.min(2);d=mx-mn
    h=np.zeros_like(mx);r,g,b=a[...,0],a[...,1],a[...,2]
    m=d>1e-6
    hr=((g-b)/np.where(m,d,1))%6;hg=(b-r)/np.where(m,d,1)+2;hb=(r-g)/np.where(m,d,1)+4
    h=np.where(mx==r,hr,np.where(mx==g,hg,hb))*60;h=np.where(m,h,0)
    s=np.where(mx>0,d/np.where(mx>0,mx,1),0);return h%360,s,mx
def rgb(h,s,v):
    h=(h%360)/60;i=np.floor(h).astype(int)%6;f=h-np.floor(h)
    p=v*(1-s);q=v*(1-s*f);t=v*(1-s*(1-f))
    r=np.choose(i,[v,q,p,p,t,v]);g=np.choose(i,[t,v,v,q,p,p]);b=np.choose(i,[p,p,t,v,v,q])
    return (np.stack([r,g,b],2)*255).clip(0,255).astype('uint8')
# pixel gradient: cyan -> blue/violet -> pink, as in the reference
STOPS=[(0,185),(0.45,250),(0.75,280),(1,320)]
def grad(t):
    t=np.clip(t,0,1);xs=[a for a,_ in STOPS];ys=[b for _,b in STOPS];return np.interp(t,xs,ys)
def banner(fn,mode,axis):
    a=np.asarray(Image.open(SRC+fn).convert('RGB')).astype(float);h,s,v=hsv(a)
    m=((h>25)&(h<75)&(s>0.18)).astype(float)
    m=np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5)))/255.
    H,W=v.shape
    if mode=='red': nh=np.full_like(h,358.)
    else:
        yy,xx=np.mgrid[0:H,0:W];t=(xx/W) if axis=='x' else (1-yy/H)
        nh=grad(t)
    # lit core: keep V; push saturation a little lower near the hot core for a natural look
    ns=np.where(mode=='red',np.clip(s*1.05,0,1),np.clip(s*0.85,0,1))
    out=rgb(nh,ns,v)
    res=(a*(1-m[...,None])+out*m[...,None]).astype('uint8');return Image.fromarray(res)
def shape(fn,mode):
    a=np.asarray(Image.open(SRC+fn).convert('RGB')).astype(float);h,s,v=hsv(a)
    lum=a.mean(2)
    m=((lum>236)&(s<0.08)).astype('uint8')*255
    mi=Image.fromarray(m).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1))
    m=np.asarray(mi)/255.
    H,W=lum.shape;yy,xx=np.mgrid[0:H,0:W]
    if mode=='red': col=np.array([235,38,30.])[None,None,:]*np.ones((H,W,1))
    else:
        nh=grad(xx/W);col=rgb(nh,np.full_like(lum,0.62),np.full_like(lum,0.98)).astype(float)
    shade=(lum/255.)[...,None]
    lit=np.clip(col*(0.55+0.5*shade),0,255)
    res=(a*(1-m[...,None])+lit*m[...,None]).astype('uint8');return Image.fromarray(res)

def banner2(fn,mode,red_sat=1.0):
    a=np.asarray(Image.open(SRC+fn).convert('RGB')).astype(float);h,s,v=hsv(a)
    m=((h>25)&(h<75)&(s>0.18)).astype(float)
    m=np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5)))/255.
    if mode=='red': nh=np.full_like(h,358.);ns=np.clip(s*red_sat,0,1)
    else:
        from shp import along
        core=(m>0.5)&(v>0.6);nh=grad(along(core.astype(float)));ns=np.clip(s*0.85,0,1)
    out=rgb(nh,ns,v);return Image.fromarray((a*(1-m[...,None])+out*m[...,None]).astype('uint8'))
