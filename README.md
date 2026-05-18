# Yan-Ke Chen — academic homepage

Personal homepage for Yan-Ke Chen (PKU CHEP postdoc, hep-ph) with an INSPIRE-HEP-fed analytics dashboard.

Live: TBD (default GitHub Pages URL until a custom domain is configured).

## Project layout

- `RS_CV/` — source-of-truth CV (LaTeX, photo). Untouched by the build.
- `scripts/` — Python data pipeline (INSPIRE fetch → JSON).
- `site/` — Astro 5 static site.
- `mockups/` — committed visual references.
- `docs/superpowers/` — design spec + implementation plan.

## Local development

```bash
# One-time setup
python3.11 -m venv scripts/.venv
source scripts/.venv/bin/activate
pip install -r scripts/requirements.txt -r scripts/requirements-dev.txt

cd site && npm install && cd ..
```

```bash
# Refresh INSPIRE data (writes site/src/data/inspire.json)
python -m scripts.fetch_inspire

# Run the dev server
cd site && npm run dev
```

```bash
# Build the static site for production
cd site && npm run build && npm run preview
```

## Deploying

Push to `main`. GitHub Actions runs `npm run build` and deploys
`site/dist/` to GitHub Pages.
