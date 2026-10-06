import json
M={}
def a(i,*keys):
    for k in keys: M.setdefault(i,[]).append(k)
A='arkeon-2-0/arkeon-2-0-'; a(0,A+'spot-white'); a(1,A+'linear-white'); a(65,A+'linear-black'); a(66,A+'spot-black')
H='hall-led-ceiling-pro/hall-led-ceiling-pro-'; a(3,H+'white'); a(16,H+'black')
P='hall-led-ceiling-ip65-pc/hall-led-ceiling-ip65-pc-'; a(58,P+'small-white'); a(59,P+'large-white'); a(60,P+'medium-white'); a(61,P+'mini-white')
a(53,'groove/groove-spot-white'); a(55,'groove/groove-spot-black'); a(57,'groove/groove-profile-black'); a(62,'groove/groove-profile-white')
a(54,'groove-display/groove-display-profile-white'); a(56,'groove-display/groove-display-profile-black')
T='twos/twos-'
for fin,ids in (('black',[31,32,33,34,35,36,37,38]),('white',[39,40,41,42,43,44,45,46])):
    for i,v in zip(ids,['spot-pro','combo-dk-spots','combo-pg-downlights','combo-2dk','diffuser','dk','downlight','track-module']):
        a(i,f'{T}{v}-{fin}')
D='twos-display/twos-display-'
for i,v in zip([47,48,49,50,51,52],['pc-black','diffuser-black','dk-black','pc-white','diffuser-white','dk-white']): a(i,D+v)
K='make/make-'
for i,s in ((4,'mini'),(21,'small'),(5,'medium'),(6,'large')): a(i,f'{K}fl-{s}-white')
for i,s in ((14,'mini'),(25,'small'),(12,'medium'),(13,'large')): a(i,f'{K}fl-{s}-black')
a(2,K+'deep-mini-white'); a(20,K+'deep-small-white'); a(15,K+'deep-mini-black'); a(27,K+'deep-small-black')
a(18,K+'double-mini-white'); a(19,K+'double-small-white'); a(28,K+'double-mini-black'); a(29,K+'double-small-black')
for s in ['micro','mini','small','medium','large']: a(24,f'{K}{s}-white'); a(26,f'{K}{s}-black')
a(9,K+'deep-pro-micro-black'); a(23,K+'deep-pro-mini-black'); a(22,K+'deep-pro-small-black')
a(63,K+'deep-pro-micro-white'); a(30,K+'deep-pro-mini-white'); a(64,K+'deep-pro-small-white')
a(7,K+'deep-pro-fl-micro-black'); a(8,K+'deep-pro-fl-mini-black'); a(17,K+'deep-pro-fl-small-black')
a(11,K+'deep-pro-fl-micro-white'); a(10,K+'deep-pro-fl-mini-white')
assert sorted(M)==list(range(67)), set(range(67))-set(M)
import os
keys=[k for v in M.values() for k in v]; assert len(keys)==len(set(keys))
miss=[k for k in keys if not os.path.exists('/home/claude/site/images/'+k+'.jpg')]; print('missing',miss)
json.dump(M,open('c2_map.json','w'),indent=0); print(len(keys),'site photos from 67 images')
