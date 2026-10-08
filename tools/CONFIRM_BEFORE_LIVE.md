# To confirm before going live

Running list, added to as we go. Nothing here is fixed yet: everything is left as is until the final review.

Rule (Chris, 7 Oct): a Phosforma datasheet describes ONE code. Nothing on it may list options, ranges or other versions.

## Datasheet PDF (draft branch `datasheet-draft`, not on the test site)
1. Overview is now code-specific: the family's opening sentences only when they list no options (any sentence with "or", ranges, sizes, "can be ordered" etc. is dropped), then "This code (…) is the <model>: <its details>. <lm> at <CCT>, CRI, UGR, beam, control. <finish> finish." Check the wording on a few codes per brand.
1a. Dimensions are now code-specific: the code's own sizes (e.g. Arkeon 46DR66PGK4B shows Length 3088mm, not 1128–3088mm) plus the family section/profile; ranges, other lengths and modules are dropped. The 2d drawing is still the family drawing.
1b. Still family-level on the PDF: supply voltage sentence, lumen maintenance, chromaticity, IP text, dimension drawing. Check none of these lists options for a code.
1c. The on-screen datasheet page (#ds-CODE) and the code page still show family text: bring them in line with the PDF?
2. Supply Voltage / Current is taken from the specification sentence, so wording varies by supplier (e.g. "Input voltage AC 220–240V.", "48V").
3. Generated date was removed with the old bottom line: the PDF no longer shows when it was made.
4. Footer keeps the page number (1/2): keep or remove.
5. Reflector finish line only appears when the code names a reflector; Fitting finish/Reflector/Brand tags say STANDARD / PARTNER.
6. Brands without a logo in the Partners list show the brand name as text.
7. Lumen Maintenance / Chromaticity: 34 families have no value anywhere (PUK 19, Karizma 9 incl. Dea Vesta, Holectron 6).
8. Heading size, spacing and layout as built in the session (16pt headings, centre gap, Dimensions beside Overview).

## Photometric curves (polar curve + beam cone)
9. Beam angle shown under the diagrams is the supplier's measured value (half peak) and can differ from the catalogue beam in Technical Data (Teres Pro "15°" measures 27°, Make R Mini "24°" measures 35°). Rename to "Measured beam angle"?
10. Codes measured only at another colour temperature use that curve scaled to the code's lumens (e.g. PUK measures at 3000K; Karizma Warm Dim and Tuneable White use the 3000K file).
11. Esse-Ci zoom / LV versions use the narrowest or base-optic file (e.g. Teres LV Micro Zoom uses the 10° file).
12. About 4,000 codes have no curve because the supplier publishes no file for that exact version: beams not measured (Dea Durga 55°, Caro REC 12°, Dea Amata L 45°…), copper reflectors, Make double, Groove / Twos / Ben Pendant Small versions, Hall IP65 PC 36°. Their datasheets skip the Photometric section.
13. 15 families have no LDT link at all: Holectron (10: Inground Radius ×4, FL112 ×4, FL175 ×2), Delta Recessed Fix Deep, Fusion DBM LED, Teres Ark, Carmenta S Lente, Boulevard Mini.
14. Beam cone shown only for downward beams up to 70°; wider or sideways fittings show the polar curve only.
15. Check a few curves per brand against the supplier's own datasheet before launch.

## Brand
16. Brand guide (Nov 2016) lists 02 9727 2220 and 85–115 Alfred Rd, Chipping Norton; the site footer still says "Head office 02 9326 7438". Datasheets now show email only.
17. Rest of the site not yet moved to the brand colours/fonts (#10181f / #777779 / #ff5000, Helvetica Neue, two-tone logo).

## Earlier open items
18. Perla is not at the Hall Led Ceiling Pro scale (would overflow the tile).
19. Make Double recessed version needs renders.
20. FL175 vs FL112 render scale is inconsistent.
21. Karizma batch folder on the Mac still has the older pendant photos.
22. Ben IP54 not split by size; "Photo Review 6 Oct" flags; Fusion DBM track tile.
23. Datasheet format published to the test site on 7 Oct (Chris asked); Electrical data & installation section removed. Items above still to confirm before the real launch.

## Macrolux profiles without LED (batch 2026-10-07, added to the test site 7 Oct)
24. Codes: Macrolux has no 1000/2000mm codes; each row is the cut-to-length code plus the length (e.g. `1301.0210.00.94 L=1000`). Confirm with Macrolux they cut to these lengths, and the price.
25. Page names as Macrolux writes them (mt1_27, ml_20 LED, mt2_27/i); versions sharing a profile code share one page.
26. 23 shared accessories on one "Macrolux profile accessories" page; single pieces only (packs, corner cuts, corner modules, MD_45 H profile, driver brackets, LED primer, 24V cables left out).
27. Section renders added (Chris's 45 renders, 7 Oct): one render per profile for every finish (renders are one colour), prismatic render on DP diffuser codes; end caps/brackets/kits and the accessories page keep the line drawing. Still no dimensions or drawings, so the Phosforma PDF has no Dimensions section. Datasheet link = Macrolux's per-profile brochure.
28. Category: Macrolux pages moved to their own category "Profiles for Flexible Linear" (Interior), after Flexible Linear in the menu.
28a. Mounting not stated by Macrolux for 14 profiles (ma2_10, ma_12, mb_15, md_12, mt0_12, mt1_12, mx1_12, mx2_12, mt2_27, mt3_27, mx2_27/i, ala, hiss, mc_90).
29. mt3_27 opal only; New badge on all 37 pages; left out: LED-only profiles, groove 140 / Groove square, groove 70.

## Electron Linibox W and Linibox C (batch 2026-10-07, added to the test site 7 Oct)
30. Electron's per-code datasheets (1,728 PDFs, ~877 MB) were NOT uploaded: each code has the Phosforma PDF instead, plus Installation, LDT and Brochure. Upload Electron's own sheets to R2 later if wanted.
31. One page per family with sizes 8 / 13 / 17 as size tables; codes built from Electron's configurator key (no published list); DC / without-driver versions (2,304 codes) left out.
32. Flux from Electron's LDTs (1,728 checked against the sheet, all match); power = LED power; efficacy calculated; UGR per beam; IP65 / IK06; no RAL numbers.
33. Categories: Linibox W → Exterior Wall Mounted; Linibox C → Exterior Surface Downlights | Spotlights.
34. Photos are small (one three-colour photo per size, upscaled 1.5×); Linibox C shown as a surface fitting on grey; no banners.
35. LDT: Electron only publishes white non-dimmable files (same optics for every colour/control); Linibox C files are Electron's C files (identical to W apart from the name); 17-27C-90-AS header says CRI 80 but has CRI90 lumens.
36. Photometric fix (applies to all brands): LDT lamp flux is now read as the set total, which corrected Electron (4 LEDs) and 2 other supplier files.

## Inground Radius run planner (8 Oct 2026, on the test site at /planner/inground-radius/)
37. ANSWERED (Chris): curves can be laid either way with the same code.
38. ANSWERED (Chris): pieces connect in the chamber with male/female T1X connectors.
39. ANSWERED (Chris): max run is set by the strip. Planner uses Holectron's MAX RUN chart (one side): FL112 48V 4.8 W/m 28.5 m, 9.6 W/m 22.5 m; FL56 24V 2.4 W/m 18.5 m, 4.8 W/m 13 m, 9.6 W/m 7.5 m. Longer lines are split into separate runs (end caps back to back, one feed each). Confirm that is how Holectron wants long lines handled (vs feeding from both ends).
40. ANSWERED (Chris): straights only 505 / 1005 mm, as in the configurator.
41. ANSWERED (Chris): section modelled from the spec sheet is fine.
42. Planner offers white strips only (FL56 24V, FL112 48V; 2200/2700/3000/4000K). RGB / RGBW / Pixel versions not in the planner yet.
43. Driver line in the planner/PDF says "one per feed, sized and supplied separately by Phosforma"; no driver codes listed.

## Protection before launch (8 Oct 2026)
44. Chris: make the GitHub repo private (repo → Settings → Danger Zone → Change visibility). It is public as of 8 Oct 2026.
45. Run planner: move piece rules, code table and PDF generation to Cloudflare server functions; minify the browser code; add copyright notice and terms of use to the planner and its PDF.
46. Inground Radius R1975: catalogue prints 11.3°, but 32 pieces make 361.6° at 11.3°. Its length (385 mm) and radius give 11.26°, so the true angle is 11.25° (32 × 11.25° = 360°). Planner now uses 11.25°. Confirm with Holectron. All other radii divide 360° exactly (R6100 100 pcs, R2950 48, R1000 16, R515 8, R272 4).
47. Installation guide labels R515 as 383 mm; the specification sheet and order code say 393 mm (L0393). Planner uses 393 mm.
48. R1975 shown as 11.25° across the website (product rows, dimensions note, code pages, Phosforma datasheets) and the planner, 8 Oct 2026. Holectron's own datasheets and catalogue still print 11.3°.
