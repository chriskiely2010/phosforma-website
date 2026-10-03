import csv
F = []
def fam(family,brand,env,cat,tagline,desc,spec,cct,cri,control,ip,finishes,drawing,new,models,images="",slides="",dims="",dims_note=""):
    F.append(dict(family=family,brand=brand,environment=env,category=cat,tagline=tagline,description=desc,specification=spec,cct=cct,cri=cri,control=control,ip=ip,finishes=finishes,drawing=drawing,new=new,images=images,slides=slides,dimensions=dims,dimensions_note=dims_note,models=models))
DL="Datasheet;IES;LDT;Installation guide"

import openpyxl
_wb=openpyxl.load_workbook("/root/.claude/uploads/f57c3d16-1811-5f88-b488-7b3004148026/b856f5fd-Alphabet_Delta_7W_Recessed_Fix_Deep_index_1.xlsx",data_only=True)
import json
UGR=json.load(open("delta_ugr.json"))
DELTA_MODELS=[]
for r in _wb["Datasheets"].iter_rows(min_row=2,values_only=True):
    if not r[0]: continue
    code,w,cri,cct,opt,drv,cov,mod_lm,del_lm,eff,zipf,pdf=r[:12]
    drv="Phase cut" if str(drv).upper()=="PHASE CUT" else drv
    cct=str(cct)
    if "unable white" in cct.lower() or "uneable white" in cct.lower():
        cct="Tuneable White "+cct.split()[-1].replace("-","–")   # family filter says just "Tuneable White"; codes keep the range
    img="images/delta-white-thumb.jpg" if cov=="White" else "images/delta-black-thumb.jpg"
    DELTA_MODELS.append((f"Delta {w} {opt}",code,"",w,f"{del_lm}lm",opt,f"Datasheet=files/delta/{code}.pdf",cct,drv,"",cov,img,f"CRI {cri}",f"{eff} lm/W",UGR.get(code,"")))

fam("Delta Recessed Fix Deep","Alphabet Lights","Interior","Recessed Downlight","Deep-set fixed downlight for a 55mm cut-out, with UGR 15 and 2-step MacAdam colour consistency.",
"A compact 4W or 7W fixed recessed downlight in aluminium with a PC dark cover. The deep-set source keeps glare low (UGR 15) while delivering high colour quality with CRI 95+ and less than 1% ripple. Electronic short-circuit, overload, over-temperature and no-load protection.",
"Cut-out Ø55mm. Minimum installation depth 80mm. Input voltage AC 220–240V. Power factor 0.95. Colour tolerance 2-step MacAdam. Ripple <1%. Operating temperature −25° to +45°. L90B10 @ 50,000h. L80B10 @ 100,000h. 7-year warranty",
"2700K | 3000K | 3500K | 4000K | Tuneable White","CRI 90 | CRI 95+","DALI | Phase cut","","White | Black","recessed-round","Yes",
DELTA_MODELS,
"images/delta-thumb.jpg;images/delta-recessed-fix-deep-dimensions.jpg","images/delta-slide-1.jpg;images/delta-slide-2.jpg","images/delta-recessed-fix-deep-dimensions.jpg","Cut-out Ø55mm · minimum installation depth 80mm")
fam("Fusion DBM LED","Exporlux","Interior","Track Mounted","Three-phase track luminaire for work areas, with near-invisible DARKLIGHT optics.",
"FUSION is designed for work areas on three-phase track, so the number and position of luminaires can change at any time. DARKLIGHT optics keep the light source practically invisible from any angle, reducing glare for a comfortable workspace.",
"Dimensions 420 × 133 × 68mm. Thermo-lacquered aluminium body. PMMA lens with anti-glare reflector. Efficiency 125 lm/W. Colour stability 3 SDCM. L80B10 100,000h at Ta 25°C. Insulation class II. IK03. Weight 1.18kg. 230V AC 50Hz. Indoor use",
"3000K","CRI 80","DALI","IP20","Cotton RAL 9003 | Black Crown RAL 9011","surface-linear","Yes",
[("Fusion DBM LED 1050 3000K 60°","FUSI013","420 × 133 × 68mm","24W","3004lm","60°","Datasheet=files/FUSI013.pdf;IES;LDT","3000K","DALI","IP20","Black Crown RAL 9011","images/fusion-dbm.jpg","","","<19")],
"images/fusion-dbm.jpg;images/fusion-dbm-dimensions.jpg;images/fusion-dbm-photometric.jpg","","images/fusion-dbm-dimensions.jpg","420 × 133 × 68mm · 1.18kg")
fam("Dea Carmenta S","Karizma Luce","Interior","Recessed Downlight","A true piece of art, just by its design.",
"An adjustable low-glare luminaire with a wide choice of reflector colours. White or Silver suits workspaces and offices; Black or Gold adds an extra dimension to hotels and restaurants.",
"Recessed adjustable downlight, tilt 25° | rotation 355°. L80 50000H B10. 3-step MacAdam. Remote power supply. 230Vac | 50/60Hz.",
"2700K | 3000K | 4000K | Warm Dim","CRI>90","On/Off | DALI | Phase Dim","IP20","Black | White","recessed-adjustable","",
[("Dea Carmenta S Adjustable Downlight","","Tilt 25°, rotation 355°.","","","")])

cols=["family","brand","environment","category","tagline","description","specification","cct","cri","control","ip","finishes","drawing","new","images","slides","slide_tag","dimensions","dimensions_note","model","code","model_finish","model_image","model_cct","model_cri","model_control","model_ip","model_ugr","model_details","power","flux","efficacy","beam","downloads","ik","model_ik"]
with open("products.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols)
    for p in F:
        for i,mm in enumerate(p["models"]):
            m,code,det,pw,fl,bm=mm[:6]; dl=mm[6] if len(mm)>6 else DL; mcct=mm[7] if len(mm)>7 else ""; mctl=mm[8] if len(mm)>8 else ""; mip=mm[9] if len(mm)>9 else ""; mfin=mm[10] if len(mm)>10 else ""; mimg=mm[11] if len(mm)>11 else ""; mcri=mm[12] if len(mm)>12 else ""; meff=mm[13] if len(mm)>13 else ""; mugr=mm[14] if len(mm)>14 else ""
            row={k:(p.get(k,"") if i==0 else "") for k in cols[:19]}
            row["family"]=p["family"]
            row.update(model_ugr=mugr,model_cri=mcri,efficacy=meff,model=m,code=code,model_finish=mfin,model_image=mimg,model_cct=mcct,model_control=mctl,model_ip=mip,model_details=det,power=pw,flux=fl,beam=bm,downloads=dl)
            w.writerow([row.get(c,"") for c in cols])
print(sum(len(p["models"]) for p in F),"rows",len(F),"families")

# Supplier index sheets in the site's own column format replace any family of the same name.
import glob
rows=list(csv.DictReader(open("products.csv",encoding="utf-8")))
for path in sorted(glob.glob("data/*.csv")):
    sup=list(csv.DictReader(open(path,encoding="utf-8-sig")))
    names={r["family"] for r in sup}
    rows=[r for r in rows if r["family"] not in names]+[{c:r.get(c,"") for c in cols} for r in sup]
    print(path,len(sup),"rows,",len(names),"families")
with open("products.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
print(len(rows),"rows total")

# Resize product photos to true relative size (see true_scale.py / tile_sizes.csv).
import true_scale
true_scale.run()
