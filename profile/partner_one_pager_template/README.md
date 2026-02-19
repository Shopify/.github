# Shopify Partner One-Pager (A4)

This folder contains a reusable, A4-sized one-pager template for Shopify partners.

## What is included

- `build_partner_one_pager.py` - renders HTML and PDF
- `partner_profile.template.json` - fill-in template for new partners
- `partner_profile.eshop_guide.sample.json` - sample based on your provided example
- `assets/shopify-logo-*.svg` - official Shopify logos fetched from Shopify brand assets
- `assets/partner-logo-placeholder.svg` - placeholder partner logo

## Branding notes

This template follows Shopify-style visual treatment:

- official Shopify logo assets
- multiple visual themes (`aurora`, `slate`, `graphite`)
- premium dark and neutral-gray variants
- icon-led sections for faster scanning

When customizing:

- keep logo proportions unchanged
- avoid stretching or recoloring the Shopify logo
- keep sufficient clear space around logos
- prefer short, proof-based copy so content stays on one page

Reference: https://www.shopify.com/brand-assets

## Generate the PDF (A4)

From this folder:

```bash
python3 build_partner_one_pager.py \
  --input partner_profile.template.json \
  --theme aurora \
  --output-html partner_one_pager_a4.html \
  --output-pdf partner_one_pager_a4.pdf
```

Generate a sample using the uploaded partner example:

```bash
python3 build_partner_one_pager.py \
  --input partner_profile.eshop_guide.sample.json \
  --theme aurora \
  --output-html eshop_guide_one_pager_a4.html \
  --output-pdf eshop_guide_one_pager_a4.pdf
```

Generate additional design options:

```bash
python3 build_partner_one_pager.py \
  --input partner_profile.eshop_guide.sample.json \
  --theme slate \
  --output-html eshop_guide_one_pager_a4_slate.html \
  --output-pdf eshop_guide_one_pager_a4_slate.pdf

python3 build_partner_one_pager.py \
  --input partner_profile.eshop_guide.sample.json \
  --theme graphite \
  --output-html eshop_guide_one_pager_a4_graphite.html \
  --output-pdf eshop_guide_one_pager_a4_graphite.pdf
```

## JSON sections to fill for each new partner

- `strengths`
- `capabilities`
- `ideal_customer_profile`
- `success_stories`
- `other_technology_partners`
- `engagement_model`
- `contact`

Keep bullet points concise (ideally 1 line each) for best A4 output.
