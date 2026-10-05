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

GO-LIVE CHECKLIST (the site is built pre-launch; going live = these steps)
--------------------------------------------------------------------------
Done
  [x] Real page per product at /products/<slug>/ (prerender.py, run by make_public.py)
      with title, description, share image, canonical link, Google product data
  [x] sitemap.xml generated on every build
  [x] Old #p-<slug> links forward to /products/<slug>/
To do before launch
  [ ] Redirects from the current phosforma.com.au pages to the new ones (_redirects file)
  [ ] Datasheets for all batches
  [ ] Contact / enquiry form, privacy policy, analytics
  [ ] Category and partner pages as real addresses too (same method as products)
Datasheets / PDFs (Cloudflare R2, bucket phosforma-files)
  - PDFs are kept in the repo's r2/ folder (not published) and copied to R2 by
    .github/workflows/r2-sync.yml on every push; check https://<bucket url>/_sync.txt
  - The site links them via FILES_BASE in index.html (R2_ON) and make_public.py (R2_LIVE)
Launch day
  [ ] R2: connect custom domain files.phosforma.com.au to the bucket (R2 > Settings > Custom Domains),
      set FILES_BASE in index.html to https://files.phosforma.com.au/ and turn off the r2.dev
      Public Development URL (Cloudflare rate-limits r2.dev; it is meant for testing)
  [ ] prerender.py: LIVE = True, confirm SITE_URL (www or not)
      -> removes noindex, robots.txt allows crawling and points to the sitemap
  [ ] Cloudflare Pages: add phosforma.com.au as custom domain, switch DNS
  [ ] Submit sitemap.xml in Google Search Console
