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
    cct=str(cct).replace("Tunable white","Tunable white")
    img="images/delta-white-thumb.jpg" if cov=="White" else "images/delta-black-thumb.jpg"
    DELTA_MODELS.append((f"Delta {w} {opt}",code,"",w,f"{del_lm}lm",opt,f"Datasheet=files/delta/{code}.pdf",cct,drv,"",cov,img,f"CRI {cri}",f"{eff} lm/W",UGR.get(code,"")))

fam("Delta Recessed Fix Deep","Alphabet Lights","Interior","Recessed Downlight","Deep-set fixed downlight for a 55mm cut-out, with UGR 15 and 2-step MacAdam colour consistency.",
"A compact 4W or 7W fixed recessed downlight in aluminium with a PC dark cover. The deep-set source keeps glare low (UGR 15) while delivering high colour quality with CRI 95+ and less than 1% ripple. Electronic short-circuit, overload, over-temperature and no-load protection.",
"Cut-out Ø55mm. Minimum installation depth 80mm. Input voltage AC 220–240V. Power factor 0.95. Colour tolerance 2-step MacAdam. Ripple <1%. Operating temperature −25° to +45°. L90B10 @ 50,000h. L80B10 @ 100,000h. 7-year warranty",
"2700K | 3000K | 3500K | 4000K | Tunable white 2700-6500K | Tunable white 1800-4000K","CRI 90 | CRI 95+","DALI | Phase cut","","White | Black","recessed-round","Yes",
DELTA_MODELS,
"images/delta-thumb.jpg;images/delta-recessed-fix-deep-dimensions.jpg","images/delta-slide-1.jpg;images/delta-slide-2.jpg","images/delta-recessed-fix-deep-dimensions.jpg","Cut-out Ø55mm · minimum installation depth 80mm")
fam("Fusion DBM LED","Exporlux","Interior","Track Mounted","Three-phase track luminaire for work areas, with near-invisible DARKLIGHT optics.",
"FUSION is designed for work areas on three-phase track, so the number and position of luminaires can change at any time. DARKLIGHT optics keep the light source practically invisible from any angle, reducing glare for a comfortable workspace.",
"Dimensions 420 × 133 × 68mm. Thermo-lacquered aluminium body. PMMA lens with anti-glare reflector. Efficiency 125 lm/W. Colour stability 3 SDCM. L80B10 100,000h at Ta 25°C. Insulation class II. IK03. Weight 1.18kg. 230V AC 50Hz. Indoor use",
"3000K","CRI 80","DALI","IP20","Cotton RAL 9003 | Black Crown RAL 9011","surface-linear","Yes",
[("Fusion DBM LED 1050 3000K 60°","FUSI013","420 × 133 × 68mm","24W","3004lm","60°","Datasheet=files/FUSI013.pdf;IES;LDT","3000K","DALI","IP20","Black Crown RAL 9011","images/fusion-dbm.jpg","","","<19")],
"images/fusion-dbm.jpg;images/fusion-dbm-dimensions.jpg;images/fusion-dbm-photometric.jpg","","images/fusion-dbm-dimensions.jpg","420 × 133 × 68mm · 1.18kg")
fam("BSM Fixed","Rovasi","Interior","Recessed Downlight","Recessed downlights with an extensive range of reflectors for the best photometric result.",
"Recessed downlight range with symmetrical light distribution for task, accent or general lighting. Aluminium body and interior circle powder painted in various finishes, customised RAL on request. Deep ingress and black baffle for minimal glare. High-purity aluminium reflectors, facetted metalised or sandblasted anodised depending on beam angle. Passive heat management via aluminium heat sink or heat pipes.",
"Round design with trimless appearance in 88mm, 141mm and 172mm diameters. Accessory available to raise protection from IP20 to IP44 from below (reference dependent). Remote driver supplied depending on reference. Honeycomb accessory available.",
"2700K | 3000K | 4000K | Sunset Dim","CRI>90","DALI | DSI | 1-10V","IP20 | IP44 option","Multiple finishes","recessed-round","",
[("BSM Ø 88mm Fixed","","Compact trimless downlight for accent and general lighting.","","",""),
 ("BSM Ø 88mm Deep Fixed","","Deep-set source for increased visual comfort.","","",""),
 ("BSM Ø 141mm Fixed","","Mid-size downlight for general lighting.","","",""),
 ("BSM Ø 172mm Fixed","","High-output downlight for larger spaces.","","","")])
fam("BSM Adjustable","Rovasi","Interior","Recessed Downlight","Adjustable recessed downlights with an extensive range of reflectors.",
"Recessed downlight range with symmetrical light distribution for task, accent or general lighting. Aluminium body and interior circle powder painted in various finishes. Deep ingress and black baffle for minimal glare. High-purity aluminium reflectors in various finishes depending on the beam angle.",
"Round design with trimless appearance in 97mm, 158mm and 172mm diameters. Adjustable to 30°. Accessory available to raise protection from IP20 to IP44 from below. Honeycomb accessory available.",
"2700K | 3000K | 4000K | Sunset Dim","CRI>90","DALI | DSI | 1-10V","IP20 | IP44 option","Multiple finishes","recessed-adjustable","",
[("BSM Ø 97mm Adjustable","","Tilt 30°.","","",""),("BSM Ø 97mm Deep Adjustable","","Tilt 30°, deep-set source.","","",""),("BSM Ø 158mm Adjustable","","Tilt 30°.","","",""),("BSM Ø 172mm Deep Adjustable","","Tilt 30°, deep-set source.","","","")])
fam("One","O/M","Interior","Recessed Downlight","Outstanding glare control with a precisely defined beam.",
"Design: O/M. A ceiling-recessed luminaire using high-definition Lightcore micro-reflector optics, developed with Bartenbach GmbH, at extremely precise beam angles. For general and accent lighting, with excellent cut-off and optimum visual comfort.",
"Ceiling-recessed luminaire in aluminium. UGR<10. Recessing system with spring clips. Power supply included. 230Vac | 50/60Hz.",
"2700K | 3000K | 4000K","CRI>90","On/Off | DALI","IP20","Black | White","recessed-round","",
[("One Spot","","Narrow, defined beam for accent lighting.","","","Spot"),("One Medium / Flood","","Wider distribution for general lighting.","","","Medium | Flood"),("One Asymmetric","","Asymmetric distribution for wall washing.","","","Asymmetric")])
fam("inVision","O/M","Interior","Recessed Downlight","Next-generation double-focus lens: more efficient, more compact, more light.",
"Design: O/M + Bartenbach GmbH. A linear recessed luminaire with aluminium housing and perforated cover plate. Focal lens with complex surface ribs provides glare-free area illumination through a narrow aperture. Discreet general lighting for offices, retail, hotels and homes.",
"Easy recessing system with spring clips. Lengths 31 to 1200mm. Power supply included. Supplied with recessing accessories. 230Vac | 50/60Hz.",
"2700K | 3000K | 4000K | Tuneable White","CRI>90","On/Off | DALI","IP20","White | Black","recessed-linear","",
[("inVision 31 | 150 | 300mm","","Short modules for point and short linear runs.","1.1W – 6.7W","",""),("inVision 600 | 900 | 1200mm","","Long modules for continuous lines.","13W – 52W","",""),("inVision Tuneable White 600 | 1200mm","","Tuneable white versions.","23W | 46W","","")])
fam("Dea Amata M","Karizma Luce","Interior","Recessed Downlight","Exactly in the colour that suits you.",
"One of the most popular luminaires in the range, hence the name: Amata means 'loved' in Italian. Caring, reliable and timeless, with seven reflector finishes to suit any interior.",
"Recessed fixed downlight. L80 50000H B10. 3-step MacAdam. Remote power supply. 230Vac | 50/60Hz. Reflectors: Silver High Gloss | White | Chrome | Gold | Black Matt | Black High Gloss | Copper.",
"2700K | 3000K | 4000K | Warm Dim | Tuneable White","CRI>90","On/Off | DALI | Casambi | Phase Dim","IP43 | IP20","Black | White","recessed-round","",
[("Dea Amata M Fixed Downlight","","Fixed downlight.","","","")])
fam("Dea Carmenta S","Karizma Luce","Interior","Recessed Downlight","A true piece of art, just by its design.",
"An adjustable low-glare luminaire with a wide choice of reflector colours. White or Silver suits workspaces and offices; Black or Gold adds an extra dimension to hotels and restaurants.",
"Recessed adjustable downlight, tilt 25° | rotation 355°. L80 50000H B10. 3-step MacAdam. Remote power supply. 230Vac | 50/60Hz.",
"2700K | 3000K | 4000K | Warm Dim","CRI>90","On/Off | DALI | Phase Dim","IP20","Black | White","recessed-adjustable","",
[("Dea Carmenta S Adjustable Downlight","","Tilt 25°, rotation 355°.","","","")])
fam("Dea Ceres M","Karizma Luce","Interior","Recessed Downlight","A square downlight that adds a touch of magic.",
"The square Dea Ceres brings a fresh, modern look to any office. White, Silver or Chrome at 4000K for comfortable workspaces; Gold and Black for a warm, classy result.",
"Recessed adjustable downlight, tilt 25° | rotation 355°. L80 50000H B10. 3-step MacAdam. Remote power supply. 230Vac | 50/60Hz.",
"2700K | 3000K | 4000K | Warm Dim | Tuneable White","CRI>90","On/Off | DALI | Casambi | Phase Dim","IP20","Black | White","recessed-square","",
[("Dea Ceres M Adjustable Downlight","","Tilt 25°, rotation 355°.","","","")])
fam("Dea Fauna S | M","Karizma Luce","Interior","Surface Downlights | Spotlights","Deep recessed light source in a square surface-mounted body.",
"The square adjustable surface-mounted Dea Fauna combines a deep recessed light source with reflector colour options. Ideal where ceilings don't permit recessed luminaires.",
"Surface-mounted adjustable luminaire, tilt 25° – 355°. >50,000h L80/B10. 3-step MacAdam. Integral power supply. 230Vac | 50/60Hz. DALI on M version only.",
"2700K | 3000K | 4000K | Warm Dim","CRI>90","On/Off | Phase Dim | DALI","IP20","Black | White","surface-square","",
[("Dea Fauna S","","Small version.","","",""),("Dea Fauna M","","Medium version, DALI available.","","","")])
fam("Hall Led Ceiling Evo","Esse-Ci","Interior","Surface Downlights | Spotlights","The complete surface downlight solution for ceilings.",
"Available in four sizes and a range of powers and optics to suit every lighting need. IP44 protection, CoB technology and an integrated driver give optimum efficacy and simple installation.",
"CoB LED technology. Integrated driver. MacAdam 3. L80/B50 >50,000h. Photobiological risk group RG0.",
"3000K | 4000K","CRI>90","On/Off | DALI","IP44","White | Black","surface-cylinder","",
[("Hall Led Ceiling Evo Mini","","","","",""),("Hall Led Ceiling Evo Small","","","","",""),("Hall Led Ceiling Evo Medium","","","","",""),("Hall Led Ceiling Evo Large","","","","","")])
fam("Super","Rovasi","Exterior","Surface Downlights | Spotlights","Surface-mounted downlights with symmetrical light distribution.",
"Robust die-cast aluminium body and trim treated against corrosion, powder coated in various finishes, custom RAL on request. High-purity aluminium reflectors. 5mm tempered glass, silicone gasket and anti-condensation device. Passive heat management through the body. Bracket mounting with cable entry from the top.",
"Cylindrical design in 180mm and 235mm diameters. IK07, IK10 with optional polycarbonate diffuser. Integral driver. Optional 304 stainless steel vandal-resistant screws.",
"2700K | 3000K | 4000K","CRI>80","DALI | DSI","IP65","Multiple finishes","surface-cylinder","",
[("Super Ø 180mm","","Cylindrical surface downlight, 180mm diameter.","12W – 24W","1900lm – 3850lm","26° – 112°"),("Super Ø 235mm","","Cylindrical surface downlight, 235mm diameter.","12W – 36W","1900lm – 5770lm","13° – 109°")])
fam("Groove IP54","Esse-Ci","Exterior","Surface Downlights | Spotlights","IP54 surface-mounted linear profile with UGR<22.",
"Combines a continuous linear luminaire with the protection needed in industrial and commercial environments. Extruded aluminium body with epoxy powder coating, flexible diffuser with co-extruded gaskets against dust and water splashes.",
"350mA integrated driver. MacAdam 3. L80/B50 >50,000h. 5-year warranty. RG0. Satin anti-static methacrylate diffuser, UGR<22.",
"3000K | 4000K","CRI>90","On/Off | DALI","IP54","White | Black","surface-linear","",
[("Groove IP54 Low Power","","","","",""),("Groove IP54 High Power","","","","","")])
fam("Shape Compact","Macrolux","Interior","Track Mounted","Compact shaping projector with an optical system for maximum efficiency.",
"Combines efficiency and visual comfort for shops, galleries and contrast-rich accents. Adjustable beam, light shaper, 90° tilt and 360° rotation.",
"Track-mounted projector. 3-step MacAdam. L80/50000H B10. Adjustable beam angle 20° – 40°.",
"2700K | 3000K | 4000K","CRI>90","On/Off | DALI","IP20","Black | White","track","",
[("Shape Compact","","Adjustable beam with framing shaper.","","","20° – 40°")])
fam("Tesoro","Karizma Luce","Interior","Track Mounted","A powerful, versatile track spotlight.",
"A small reflector spotlight for 3-phase track. A favourite in retail and hospitality, with options in colour, control, CCT and beam.",
"350° rotation | 90° tilt. Specular aluminium reflector.",
"2700K | 3000K | 4000K | Warm Dim","CRI>80 | CRI>90","On/Off | Phase Dim | DALI | Casambi","IP20","White | Black","track","",
[("Tesoro","","3-phase track spotlight.","19W","1550lm – 2200lm","20° | 30° | 45°")])
fam("Neman Shape","Holectron","Interior","Ceiling Suspended | Pendants","Geometric pendants in any size from 560mm to 3080mm.",
"Triangles, squares and hexagons that fill the room with soft, uniform light. For retail, offices, restaurants and homes. Made in Europe. Direct, direct/indirect or indirect distribution.",
"Low output 1300 lm/m | Standard 2000 lm/m. Optics: NemanX louvre 30°/60°/90° | Microprism | Opal. Single lead cable per luminaire. CRI98+ on request.",
"2700K | 3000K | 3500K | 4000K | Tuneable White","CRI>80 | CRI>90 | CRI>95","On/Off | DALI","IP20","Black | Grey | White","pendant","",
[("Neman Shape Triangle","","","","1300 – 2000 lm/m",""),("Neman Shape Square","","","","1300 – 2000 lm/m",""),("Neman Shape Hexagon","","","","1300 – 2000 lm/m","")])
fam("Diamante","Esse-Ci","Interior","Profiles & Systems","A slim line of light with innovative glare control.",
"Rossi Bianchi Lighting Design. Visual comfort from a dark louvre, rhomboidal optics and micro-prismatic diffuser. Works stand-alone or as a system, and in a Free version for false ceilings.",
"DPL technology diffuser UGR<19 plus raster for glare control. MacAdam 3. L80/B50 >60,000h. Integrated driver. Suspended, surface and recessed versions. RG0.",
"3000K | 4000K","CRI>90","On/Off | DALI","IP20","White | Black","linear","",
[("Diamante Low Power Single Emission","","","","",""),("Diamante Low Power Double Emission","","","","",""),("Diamante High Power Single Emission","","","","",""),("Diamante High Power Double Emission","","","","","")])
fam("Tua","O/M","Exterior","Bollard","Wide, glare-free light from a concealed source.",
"Design: O/M + Eduardo Souto de Moura. An asymmetric high-purity aluminium reflector projects light far and wide without glare. Tua Optic omits the stand for a compact, discreet source.",
"Aluminium with anti-corrosion treatment and textured polyester paint. Anti-UV clear polycarbonate diffuser. 97% reflectance reflector. IP68 pass-through connector included. >50,000h L80/B10. 2-step MacAdam.",
"2700K | 3000K | 4000K","CRI>80","On/Off | DALI","IP65","White | Black | Graphite Black | Rust","bollard","",
[("Tua 600 | 900","","Bollard, 600 or 900mm.","","","Transverse | Longitudinal"),("Tua Optic","","Compact version without stand.","","",""),("Tua S 600 | 900","","Slim bollard.","","",""),("Tua Optic S","","","","","")])
fam("Altea Mini","LLD Light","Exterior","Inground","Ø26mm inground light for steps, paths and gardens.",
"IP67 fixed-optic light for floor, wall or ceiling. Anodised aluminium body with aluminium or AISI 316L stainless trim and tempered glass. Walk-over to 500kg. 24V DC or 350mA versions.",
"Ø26 x 48mm. 1 x 1W LED. Transparent tempered glass and PMMA lens. Lifetime 50,000h. Housing CAE21 and spring clips ML021 supplied separately.",
"3000K | 4000K","CRI>80","On/Off","IP67","Stainless Steel | Brushed Steel | Anodised Aluminium","inground","",
[("Altea Mini 28°","","","1W","130lm – 140lm","28°"),("Altea Mini 42°","","","1W","130lm – 140lm","42°")])

cols=["family","brand","environment","category","tagline","description","specification","cct","cri","control","ip","finishes","drawing","new","images","slides","slide_tag","dimensions","dimensions_note","model","code","model_finish","model_image","model_cct","model_cri","model_control","model_ip","model_ugr","model_details","power","flux","efficacy","beam","downloads"]
with open("products.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols)
    for p in F:
        for i,mm in enumerate(p["models"]):
            m,code,det,pw,fl,bm=mm[:6]; dl=mm[6] if len(mm)>6 else DL; mcct=mm[7] if len(mm)>7 else ""; mctl=mm[8] if len(mm)>8 else ""; mip=mm[9] if len(mm)>9 else ""; mfin=mm[10] if len(mm)>10 else ""; mimg=mm[11] if len(mm)>11 else ""; mcri=mm[12] if len(mm)>12 else ""; meff=mm[13] if len(mm)>13 else ""; mugr=mm[14] if len(mm)>14 else ""
            row={k:(p.get(k,"") if i==0 else "") for k in cols[:19]}
            row["family"]=p["family"]
            row.update(model_ugr=mugr,model_cri=mcri,efficacy=meff,model=m,code=code,model_finish=mfin,model_image=mimg,model_cct=mcct,model_control=mctl,model_ip=mip,model_details=det,power=pw,flux=fl,beam=bm,downloads=dl)
            w.writerow([row[c] for c in cols])
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
