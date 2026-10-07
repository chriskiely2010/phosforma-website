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
23. Merge `datasheet-draft` into main once the above is signed off.
