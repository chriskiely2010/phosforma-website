import json,os,sys,numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'/home/claude/site/archive/scripts'); from photo2 import save_jpg
L=json.load(open('c2_list.json')); M=json.load(open('c2_map.json'))
D='/mnt/user-data/uploads/ESSE-CI CORRECTIONS PART 2/'; OUT='/tmp/claude-0/esse/c2out/'
def proc(i):
    a=np.asarray(Image.open(D+L[i]).convert('RGB'),np.float32); H,W=a.shape[:2]
    b=np.concatenate([a[:3].reshape(-1,3),a[-3:].reshape(-1,3),a[:,:3].reshape(-1,3),a[:,-3:].reshape(-1,3)])
    bg=np.median(b,0); a=np.clip(a*(204/bg),0,255)              # background level -> #CCCCCC
    d=np.abs(a-204).max(-1); w=np.clip((d-3)/5,0,1)[...,None]      # flatten noise near the background
    a=a*w+204*(1-w)
    m=ndimage.binary_opening(d>10,iterations=2); lab,n=ndimage.label(m)
    sz=ndimage.sum(m,lab,range(1,n+1)); m=np.isin(lab,[k+1 for k,v in enumerate(sz) if v>=150])
    ys,xs=np.where(m); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    t=dict(l=x0<=2,r=x1>=W-3,t=y0<=2,b=y1>=H-3)
    s=max(x1-x0,y1-y0)/0.8
    if t['l'] and t['r']: s=W
    if t['t'] and t['b']: s=min(s,H) if not(t['l'] and t['r']) else s
    if (t['l'] or t['r']) and not(t['l'] and t['r']): s=min(s,max(x1-x0,y1-y0)/0.8)
    cx,cy=(x0+x1)/2,(y0+y1)/2; X,Y=cx-s/2,cy-s/2
    if t['l']: X=0
    if t['r'] and not t['l']: X=W-s
    if t['t']: Y=0
    if t['b'] and not t['t']: Y=H-s
    can=Image.new('RGB',(round(s),round(s)),(204,204,204))
    can.paste(Image.fromarray(a.round().astype(np.uint8)),(round(-X),round(-Y)))
    can=can.resize((800,800),Image.LANCZOS)
    for k in M[str(i)]:
        p=OUT+k+'.jpg'; os.makedirs(os.path.dirname(p),exist_ok=True); save_jpg(can,p)
    return t
for i in range(67): print(i,{k for k,v in proc(i).items() if v} or '')
