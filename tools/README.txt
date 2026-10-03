PHOSFORMA WEBSITE – MASTER COPY OF THE TEST SITE
================================================
This folder holds everything the test site is built from. Keep it.
If anything is lost online, the site can be rebuilt from these files.

index.html        The website itself (design, pages, layout).
products.csv      The product spreadsheet the site reads (all families and codes).
data/             Supplier index sheets in the site's format (e.g. karizma_luce.csv).
                  These are merged into products.csv.
build_csv.py      Script that rebuilds products.csv from the base range + data/ sheets.
delta_ugr.json    UGR values read from the Delta datasheets.
images/           Banners, thumbnails, reflector photos, dimension drawings.
files/            Datasheets the site links to. The 288 Delta PDFs (files/delta) are
                  the same files as your Downloads folder
                  Alphabet_Delta_7W_Recessed_Fix_Deep_DALI_PhaseCut, so they are not
                  duplicated in this zip.

To add products: fill a supplier sheet using Phosforma_products_template.csv,
add the images, and send them to Claude (or upload once the live site is set up).
