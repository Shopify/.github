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
- neutral white/gray layout
- Shopify green accent (`#95BF47`) for highlights

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
  --output-html partner_one_pager_a4.html \
  --output-pdf partner_one_pager_a4.pdf
```

Generate a sample using the uploaded partner example:

```bash
python3 build_partner_one_pager.py \
  --input partner_profile.eshop_guide.sample.json \
  --output-html eshop_guide_one_pager_a4.html \
  --output-pdf eshop_guide_one_pager_a4.pdf
```

## JSON sections to fill for each new partner

- `strengths`
- `capabilities`
- `ideal_customer_profile`
- `success_stories`
- `engagement_model`
- `contact`

Keep bullet points concise (ideally 1 line each) for best A4 output.
