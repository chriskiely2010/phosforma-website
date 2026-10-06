import json,sys,shutil,numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,'/home/claude/site/archive/scripts'); from photo2 import save_jpg
S='/home/claude/site/images/'
D='/mnt/user-data/uploads/ESSE-CI CORRECTIONS PART 2/'; L=json.load(open('/tmp/claude-0/esse/c2_list.json'))
def anchor(src,dst,sides,fx=0.8,fy=0.9):
    a=np.asarray(Image.open(src).convert('RGB'),np.float32); H,W=a.shape[:2]
    b=np.concatenate([a[:3].reshape(-1,3),a[-3:].reshape(-1,3),a[:,:3].reshape(-1,3),a[:,-3:].reshape(-1,3)])
    bg=np.median(b,0); a=np.clip(a*(204/bg),0,255)
    d=np.abs(a-204).max(-1); w=np.clip((d-3)/5,0,1)[...,None]; a=a*w+204*(1-w)
    m=ndimage.binary_opening(d>10,iterations=2); lab,n=ndimage.label(m)
    sz=ndimage.sum(m,lab,range(1,n+1)); m=np.isin(lab,[k+1 for k,v in enumerate(sz) if v>=60])
    ys,xs=np.where(m); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    bw,bh=x1-x0+1,y1-y0+1
    side=max(bw/fx,bh/fy)
    X=x0 if 'l' in sides else (x1+1-side if 'r' in sides else (x0+x1)/2-side/2)
    Y=y0 if 't' in sides else (y1+1-side if 'b' in sides else (y0+y1)/2-side/2)
    c=Image.new('RGB',(round(side),round(side)),(204,204,204))
    c.paste(Image.fromarray(a.round().astype(np.uint8)),(round(-X),round(-Y)))
    save_jpg(c.resize((800,800),Image.LANCZOS),dst)
T=S+'twos/'; TD=S+'twos-display/'
for f in ['twos-pc-black','twos-pc-white','twos-combo-pg-spots-black','twos-combo-pg-spots-white']:
    anchor(T+f+'.jpg',T+f+'.jpg','lt')
for i,f in ((49,'twos-display-dk-black'),(51,'twos-display-diffuser-white'),(52,'twos-display-dk-white')):
    anchor(D+L[i],TD+f+'.jpg','l')
shutil.copy(T+'twos-dk-black.jpg',T+'twos-thumb.jpg')
shutil.copy(TD+'twos-display-dk-black.jpg',TD+'twos-display-thumb.jpg')
shutil.copy(S+'groove-display/groove-display-profile-white.jpg',S+'groove-display/groove-display-thumb.jpg')
