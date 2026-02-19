# Partner One-Pager Self-Serve Portal

This is a lightweight web app that lets partners submit their information and generate a branded A4 PDF one-pager automatically.

## What it does

- collects partner profile input via a web form
- accepts partner logo upload (`svg`, `png`, `jpg`, `jpeg`, `webp`)
- calls the existing one-pager renderer in `../partner_one_pager_template`
- generates and downloads a single-page A4 PDF

## Run locally

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open:

- `http://localhost:5050/`
- `http://localhost:5050/preview` (share-friendly colleague preview page)

Optional presets:

- `http://localhost:5050/?preset=template`
- `http://localhost:5050/?preset=sample`

## Notes

- default design theme is `graphite`
- additional themes are available in the form: `slate`, `aurora`
- max upload size is 8 MB
- sample PDFs can be accessed directly via `/sample-pdfs/<name>`
