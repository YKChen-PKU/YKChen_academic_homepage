# Yan-Ke Chen — Academic Homepage

A redesigned personal academic homepage for **Yan-Ke Chen (陈炎柯)**, postdoctoral researcher at the Center for High Energy Physics, Peking University.

The site presents research themes, publications, talks, CV, and publication analytics. Bibliographic records and citation metrics come from [INSPIRE-HEP](https://inspirehep.net/authors/2182746) and are refreshed automatically once per day.

## Stack

- **Astro 6** static site with server-rendered KaTeX
- Plain CSS with responsive layouts and reduced-motion support
- Light-by-default themes with a manual dark-mode toggle and a default-English Chinese language toggle
- Static SVG charts; no client-side charting framework
- **Python** pipeline for INSPIRE-HEP data collection and metric derivation
- **GitHub Actions** for daily data refresh, build, and GitHub Pages deployment

The earlier [YKChen_academic_homepage](https://github.com/YKChen-PKU/YKChen_academic_homepage) repository was used as a read-only reference for content, data semantics, and the INSPIRE pipeline. This project contains a new visual design and frontend implementation.

## Project layout

```text
.github/workflows/deploy.yml    Daily refresh and Pages deployment
scripts/                       INSPIRE client, parsers, metrics, and tests
site/
  public/                      Portrait, CV PDF, favicon, and CNAME
  src/
    components/                Shared UI and SVG analytics
    data/                      INSPIRE snapshot, themes, and talks
    layouts/                   HTML shell and metadata
    lib/                       Types, research content, math, chart helpers
    pages/                     Home, research, publications, analytics, talks, CV
    styles/global.css          Design tokens and responsive styles
```

## Local development

Requirements: Node.js **22.12 or newer** and Python **3.9 or newer** (CI uses Python 3.12).

```bash
python3 -m venv scripts/.venv
scripts/.venv/bin/python -m pip install -r scripts/requirements-dev.txt
cd site
npm install
npm run dev
```

Astro prints the local preview URL, normally `http://localhost:4321`.

### Refresh INSPIRE data

From the repository root:

```bash
scripts/.venv/bin/python -m scripts.fetch_inspire
```

This writes `site/src/data/inspire.json`. Use `--no-cache` to bypass the local HTTP cache. The generated snapshot is committed so the site can still be built when INSPIRE is unavailable.

### Tests and production build

```bash
scripts/.venv/bin/python -m pytest scripts/tests
cd site
npm run build
npm run preview
```

The production output is written to `site/dist/`.

## Editing content

- **Research descriptions and methods:** `site/src/lib/research.ts`
- **Education, work experience, and awards:** `site/src/lib/experience.ts`
- **arXiv ID → research theme mapping:** `site/src/data/themes.yaml`
- **Talks:** `site/src/data/talks.yaml`
- **CV page:** `site/src/pages/cv.astro`
- **Authoritative CV PDF:** `site/public/cv/CV_YKChen.pdf`
- **Portrait:** `site/public/photo.jpg`
- **Colors, typography, and layout:** `site/src/styles/global.css`

Do not manually edit `inspire.json`; refresh it through the Python pipeline. New papers remain untagged until their arXiv IDs are added to `themes.yaml`.

## Deployment

The workflow runs on pushes to `main`, on manual dispatch, and daily at **03:00 UTC**. It refreshes INSPIRE data, falls back to the committed snapshot if the fetch fails, builds the site, and deploys `site/dist/` to GitHub Pages.

For first-time deployment:

1. Push this repository to GitHub.
2. Set **Settings → Pages → Source** to **GitHub Actions**.
3. Keep `site/public/CNAME` containing `yankechen.xyz` and configure the domain's DNS for GitHub Pages.
4. Confirm the custom domain in GitHub Pages and enable HTTPS after the certificate is provisioned.
