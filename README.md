# Yan-Ke Chen — academic homepage

Personal homepage for Yan-Ke Chen (PKU CHEP postdoc, hep-ph) with an INSPIRE-HEP-fed analytics dashboard.

Live: https://yankechen.xyz (DNS setup required — see "Deploying" below).

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

GitHub Actions (`.github/workflows/deploy.yml`) triggers on:

- every push to `main` — instant rebuild after content edits;
- a daily cron at **03:00 UTC** — re-fetches INSPIRE so the analytics
  page stays current without manual intervention;
- manual `workflow_dispatch`.

Each run installs Python deps, runs `python -m scripts.fetch_inspire`
(falling back to the committed `inspire.json` if INSPIRE is
unreachable), builds the Astro site, and deploys to GitHub Pages.

### First-time setup

1. Push this repo to GitHub.
2. In **Settings → Pages**, set source to **GitHub Actions**.
3. Configure DNS for `yankechen.xyz`:
   - Add `A` records pointing the apex to GitHub's Pages IPs
     (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`,
     `185.199.111.153`), **or** add a `CNAME` record for the apex
     (if your DNS provider supports ALIAS / ANAME / flattened CNAME)
     pointing to `<gh-username>.github.io`.
   - For `www.yankechen.xyz` (optional), add a `CNAME` record
     pointing to `<gh-username>.github.io`.
4. In **Settings → Pages**, confirm `yankechen.xyz` is detected from
   `site/public/CNAME` and enable "Enforce HTTPS" once the cert
   provisions (typically within ~10 minutes of DNS propagation).
