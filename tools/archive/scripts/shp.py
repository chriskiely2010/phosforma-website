import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd
SRC='/home/claude/site/images/inground-radius/'
def diffuser_mask(a):
    lum=a.mean(2)
    gx=nd.sobel(lum,1);gy=nd.sobel(lum,0);g=np.hypot(gx,gy)
    bg=np.abs(lum-204)<2.5
    cand=(lum>207)&(g<60)&~bg
    lab,n=nd.label(cand)
    # seed: brightest end-face pixels
    seedm=lum>247;sl,sn=nd.label(seedm)
    if sn==0: return np.zeros_like(lum,bool),None
    sizes=nd.sum(seedm,sl,range(1,sn+1));big=np.argmax(sizes)+1
    ys,xs=np.where(sl==big)
    ids=set(lab[ys,xs])-{0}
    # also include components touching the seed's dilation (lower half of end face, top band)
    dil=nd.binary_dilation(sl==big,iterations=4)
    ids|=set(np.unique(lab[dil]))-{0}
    m=np.isin(lab,list(ids))|(sl==big)
    # drop huge leaks (bigger than 12% of image)
    return m,(ys.min(),xs.min())
def colour(fn,mode,dbg=False):
    a=np.asarray(Image.open(SRC+fn).convert('RGB')).astype(float)
    m,seed=diffuser_mask(a)
    H,W=m.shape
    mi=Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    mf=np.asarray(mi)/255.
    lum=a.mean(2)/255.
    if mode=='red': col=np.array([238,35,28.])*np.ones((H,W,1))
    else:
        from rc import grad,rgb
        yy,xx=np.mgrid[0:H,0:W];col=rgb(grad(xx/W),np.full((H,W),0.6),np.full((H,W),1.0)).astype(float)
    lit=np.clip(col*(0.6+0.45*lum[...,None]),0,255)
    out=a*(1-mf[...,None])+lit*mf[...,None]
    return Image.fromarray(out.astype('uint8')),m.mean()

def along(m):
    ys,xs=np.where(m>0.5);pts=np.stack([xs,ys],1).astype(float);c=pts.mean(0)
    u,s,vt=np.linalg.svd(pts-c,full_matrices=False);d=vt[0]
    if d[1]>0: d=-d            # run from the lower (front) end upwards/away
    H,W=m.shape;yy,xx=np.mgrid[0:H,0:W];p=(xx-c[0])*d[0]+(yy-c[1])*d[1];pm=p[m>0.5]
    return np.clip((p-pm.min())/(pm.max()-pm.min()+1e-6),0,1)
def colour2(fn,mode):
    from rc import grad,rgb
    a=np.asarray(Image.open(SRC+fn).convert('RGB')).astype(float)
    m,_=diffuser_mask(a);H,W=m.shape
    mf=np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8)))/255.
    lum=a.mean(2)/255.
    if mode=='red': col=np.array([238,35,28.])*np.ones((H,W,1))
    else: col=rgb(grad(along(m)),np.full((H,W),0.6),np.full((H,W),1.0)).astype(float)
    lit=np.clip(col*(0.6+0.45*lum[...,None]),0,255)
    return Image.fromarray((a*(1-mf[...,None])+lit*mf[...,None]).astype('uint8'))
