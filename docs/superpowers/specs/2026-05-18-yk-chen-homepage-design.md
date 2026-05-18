# Personal academic homepage for Yan-Ke Chen — design spec

**Date:** 2026-05-18
**Owner:** YK Chen
**Status:** Awaiting user review (post-brainstorm)

---

## 1 · Purpose & audience

A personal academic homepage for **Yan-Ke Chen (陈彦珂)**, postdoctoral researcher at the Center for High Energy Physics (CHEP), Peking University. The site presents biographical context, research themes, publications and talks, and a **multi-dimensional analytics dashboard** drawn from his INSPIRE-HEP author profile (`https://inspirehep.net/authors/2182746`).

**Primary audience:** international physics community — peers, collaborators, and graduate students.

**Success criteria:**

- A peer unfamiliar with YK Chen can, in under 90 seconds, learn what he works on, where he is, and read three representative papers.
- A graduate student can read the *Research* page and understand the four research themes without prior context.
- The analytics page communicates eight distinct facets of YK's scholarly output (volume, impact trajectory, collaboration topology, author position, journal mix, topic focus, top-cited papers, h-index curve) in a single scroll.
- The owner can refresh INSPIRE data with one local command, commit, and push — the site rebuilds and redeploys via GitHub Actions in under 3 minutes.
- All paper titles and inline mathematics render as proper LaTeX (KaTeX), not as raw `$…$` strings.

**Non-goals:**

- Blog or news section.
- Contact form.
- Teaching pages (YK is a postdoc; not relevant yet).
- Bilingual content (English only).
- Live INSPIRE queries from the browser (data is fetched at build time).

---

## 2 · Information architecture

Six top-level pages, accessible from a shared top-bar nav:

| Path | Purpose | Primary data source |
|---|---|---|
| `/` (Home) | Hero · short bio · "by-the-numbers" strip · five selected publications · four research-theme cards | hand-written content + `inspire.json` |
| `/research` | Per-theme intro paragraph + full paper list for that theme; four themes total | hand-written + `inspire.json` |
| `/publications` | Full publication list, filterable by year / theme / journal; each row: title (with LaTeX), author list (YK bolded), venue, citation count, arXiv link, DOI link | `inspire.json` |
| `/talks` | Oral and poster presentations (from CV); each entry: event, title, location, date | hand-written |
| `/analytics` | Eight visualizations of scholarly output (see §6) | `inspire.json` (derived metrics) |
| `/cv` | HTML CV summary with prominent "Download PDF" button (links to `CV_YKChen.pdf`) | hand-written + linked PDF |

**Top nav (every page):** `RESEARCH · PUBLICATIONS · TALKS · ANALYTICS · CV`. Brand on left: `Yan-Ke Chen 陈彦珂`.

**Footer (every page):** "Data sourced from INSPIRE-HEP. Last refreshed YYYY·MM·DD." + external profile links (INSPIRE, ORCID *[TBD]*, Google Scholar *[TBD]*, GitHub *[TBD]*, email) + © + typography credit.

**Mobile:** single-column stack; nav collapses to a hamburger; grids of figures degrade to single column; force-directed network falls back to a static SVG snapshot below 768 px width.

---

## 3 · Visual design system — "Quiet Editorial"

### 3.1 Concept

The aesthetic combines **A's editorial-print color palette and layout** (cream paper, indigo and sienna accents, marginalia section markers, asymmetric grid) with **B's modern sans-serif typography** (Inter at multiple weights, tight optical tracking on display sizes). The result reads like a beautifully typeset contemporary editorial — the gravitas of print without serif retro-feel. Mathematics is rendered via KaTeX in display- and inline form so paper titles look correct.

### 3.2 Color tokens (CSS custom properties)

```css
--paper:    #F6F4EE;   /* warm cream background, never pure white */
--paper-2:  #EFEBE1;   /* hover / elevated surface */
--ink:      #15120E;   /* warm near-black, primary text */
--ink-2:    #4C463D;   /* secondary text */
--ink-3:    #8C8579;   /* tertiary / muted text */
--rule:     #DCD5C5;   /* dividers, borders */
--rule-2:   #ECE6D6;   /* sub-dividers, faint grid */
--accent:   #1B2E5E;   /* indigo — links, primary chart line */
--mark:     #B0492A;   /* sienna — "current" / "highlighted" only */
```

A faint SVG fractal-noise overlay (`opacity 0.035`, `mix-blend-mode: multiply`) gives the surface a paper feel.

### 3.3 Typography

| Role | Family | Source | Use |
|---|---|---|---|
| Display | **Inter** weight 500–600, tight tracking | Google Fonts (variable) | h1, h2, large numerals, paper titles |
| Body | **Inter** weight 400–500 | Google Fonts | running text, UI labels |
| Mono | **IBM Plex Mono** weight 400–500 | Google Fonts | arXiv IDs, metadata, axis ticks, nav links, section markers, year/citation values |
| Math | **KaTeX** default (KaTeX_Main / KaTeX_Math) | KaTeX CSS | inline + display math, all paper titles |

Display rules:

- `letter-spacing: -0.035em` on h1 (60 px), `-0.025em` on h2 (24–32 px).
- `font-variation-settings` left at default — Inter is a single-axis variable font (wght only).
- Numerals use `font-variant-numeric: tabular-nums` for stat blocks and tables.

### 3.4 Layout

- Max content width 1180 px, fluid horizontal padding `clamp(1.75rem, 5vw, 3.5rem)`.
- **Marginalia column.** Each major section uses a 90 px left column for the `§ I` / `§ II` roman-numeral marker rendered in IBM Plex Mono, with the section content to its right.
- Hero grid: 1fr · 0.42fr (content · photo).
- Generous vertical rhythm: section padding `clamp(2.25rem, 5vw, 3.5rem) 0`.
- 1 px `--rule` dividers between major sections; 1 px `--rule-2` dashed dividers for ticker / sub-sections.

### 3.5 Motion

- **Page load:** staggered fade-up of hero children, 8 px translate, 0.9 s `cubic-bezier(.2,.7,.2,1)`, 80 ms inter-sibling delay.
- **Hero "currently" dot:** 2.4 s infinite radial pulse in sienna (`--mark`) — the only animated infinite element on the site.
- **Chart bars:** scale-X from 0 → 1, single play on viewport entry.
- **Co-author network:** D3 force simulation runs once on load and freezes after ~600 ms.
- **Hover affordances:** links use a left-to-right underline grow (`background-size: 0% → 100% 1px`, 0.35 s).
- **Reduced motion:** `prefers-reduced-motion: reduce` disables entrance animations, pulse, and force simulation (network shows pre-computed positions).

### 3.6 Visual reference

A reviewed mockup of the home hero in this style lives at `.superpowers/brainstorm/<session>/content/visual-style-v2.html` from the brainstorm session and SHOULD be copied into `mockups/home.html` during implementation as the committed visual source-of-truth.

---

## 4 · Pages

### 4.1 Home (`/`)

Three marginalia-marked sections.

**§ I · Currently.** Asymmetric grid. Left column: pulsing sienna dot + h1 "Yan-Ke Chen" + one paragraph bio ("Postdoctoral researcher at the **Center for High Energy Physics, Peking University**. I study hadron spectroscopy, exotic states, low-energy hadron interactions, and electromagnetic properties of hadrons via χPT and quark potential models."). Right column: photo (from `RS_CV/photo.png`) with caption "CHEP · PKU · Jul 2025 →". Below the grid: a four-cell "by-the-numbers" strip (Papers / Citations / h-index / Co-authors) bounded by a 1 px top rule. Below that: a dashed ticker showing the most recent arXiv preprint with KaTeX-rendered title.

**§ II · Selected papers.** Five hand-curated papers (default: most recent + most cited within each theme). Each row: year (mono, narrow) · title with inline KaTeX + italic author list (YK in mono uppercase **bold**) · venue (mono, indigo, right-aligned). 1 px `--rule-2` between rows.

**§ III · Research themes.** Four-card 2 × 2 grid for the four CV themes (Spectrum from quark models · Hadron-hadron interaction · Electromagnetic properties · Production of exotic states). Each card: bold theme name + 2 short sentences (inline KaTeX where needed) + "→ Read more" link to `/research#<theme-slug>`.

### 4.2 Research (`/research`)

One long page, four anchored sections (`#spectrum`, `#interaction`, `#em`, `#production`). Each section: marginalia roman numeral + theme title + 2–4 paragraph intro (hand-written, accessible to grad students) + a denser list of the theme's papers (subset of `/publications`, filtered to that theme). The mapping of papers → themes is encoded in `site/src/data/themes.yaml` (hand-curated based on CV groupings).

### 4.3 Publications (`/publications`)

Full chronological list (newest first) from `inspire.json`. Each row: `[YEAR]` · title (KaTeX) · authors (`Y. K. Chen` bold and indigo when YK) · `arXiv:XXXX.YYYYY` · `DOI:…` · journal · citation count badge. Filter chips above the list: All years / By theme (4 chips) / Journal (PRD / EPJ C / etc) / Author position (first / middle / last). Filter state lives in URL query string for shareable links. No pagination — all papers shown.

### 4.4 Talks (`/talks`)

Two grouped sections: "Oral Presentations" and "Poster Presentations". Each entry: bold conference/workshop name + italic title (with KaTeX) + location · date (mono, right-aligned). Reverse chronological. Source: a hand-written `site/src/data/talks.yaml` because INSPIRE does not reliably track talks.

### 4.5 Analytics (`/analytics`)

Eight visualizations rendered as React/Astro islands on this page only. Layout (mobile collapses each row to one column):

```
[ ① Co-author network — full-width, ~480 px tall ]

[ ② Papers/year       ][ ③ Cumulative citations    ]

[ ④ h-index curve     ][ ⑤ Author position donut   ]

[ ⑥ Top cited papers  ][ ⑦ Journal venue split     ]

[ ⑧ Topic / keyword treemap — full-width, ~360 px ]
```

For each chart see §6 for data sources, library choice, and interaction.

**Page intro:** one short paragraph above the first chart explaining that data is sourced from INSPIRE-HEP at the date shown, with a "Refreshed YYYY·MM·DD" timestamp in mono.

### 4.6 CV (`/cv`)

HTML rendering of CV content — sections mirror `RS_CV/CV_YKChen.tex` (Personal Info, Education, Professional Experience, Awards, Service, Skills, Research Interests, Presentations, Publications). Prominent indigo button at the top: "Download PDF (CV_YKChen.pdf)" linking to `site/public/cv/CV_YKChen.pdf`. The PDF is copied from `RS_CV/CV_YKChen.pdf` during build (script step).

---

## 5 · Data pipeline

### 5.1 Flow

```
INSPIRE-HEP REST API
        │
        ▼
scripts/fetch_inspire.py        ◄── manual local run by YK
        │  (writes JSON)
        ▼
site/src/data/inspire.json      ◄── committed to git
        │  (Astro reads at build)
        ▼
Astro build → static HTML       ◄── runs in GH Actions on push
        │
        ▼
GitHub Pages deployment
```

### 5.2 INSPIRE client (`scripts/inspire_client.py`)

- Single `InspireClient` class with synchronous `requests`. Retry with exponential backoff on 429/5xx (max 5 attempts, base 2 s). Throttle ≤ 1 req/s.
- Methods: `fetch_author(recid)`, `fetch_author_works(recid, size=250)` (paginates), `fetch_record(arxiv_id)` (used only if a paper isn't on the author page).
- Custom `User-Agent: yan-ke-chen-homepage/<git-sha> (mailto:chenyanke@pku.edu.cn)`.
- Disk cache at `scripts/.cache/inspire/{path-hash}.json` keyed by query path; honored unless `--no-cache`.

### 5.3 Pydantic schema (`scripts/models.py`)

Top-level `InspireBundle`:

```python
class InspireBundle(BaseModel):
    fetched_at: datetime          # UTC
    author: AuthorProfile         # name, affiliations, recid, orcid
    papers: list[Paper]           # all works
    metrics: DerivedMetrics       # everything Analytics consumes
    themes: dict[str, list[str]]  # theme_slug -> [arxiv_id, ...]
```

`Paper` carries: `arxiv_id`, `inspire_id`, `title` (raw LaTeX), `authors` (list of `Author`), `journal_ref` (parsed: name, volume, page, year), `doi`, `citation_count`, `arxiv_categories`, `author_position` (`first|middle|last|sole`), `is_yk_first`, `theme_slug` (optional).

`DerivedMetrics` carries all values the dashboard needs (see §6).

### 5.4 Build script (`scripts/fetch_inspire.py`)

CLI entry point. Order of operations:

1. Fetch `author` and `papers` from INSPIRE.
2. Run `derive_metrics(papers)` (see §6.10) to populate `DerivedMetrics`.
3. Load `themes.yaml` (hand-curated arxiv_id → theme mapping) and join into papers.
4. Render Pydantic bundle → JSON; write to `site/src/data/inspire.json`.
5. Print summary (paper count, citation total, top cited, last-refreshed timestamp).

Run with `python scripts/fetch_inspire.py` after activating the venv described in §7.

### 5.5 Tests

- `respx`-mocked unit tests for the INSPIRE client (uses fixture `tests/fixtures/author_2182746.json`).
- Pure-function tests for `derive_metrics` (no network).
- One end-to-end test that runs `fetch_inspire.py --offline` against the fixture and validates the emitted `inspire.json` against the Pydantic schema.

---

## 6 · Analytics — eight charts

For every chart: title in Inter 500, mono caption with axis labels and "n=… papers · refreshed YYYY·MM·DD", indigo primary + sienna "current year / highlighted" + cream chart background. All charts respect `prefers-reduced-motion`.

### 6.1 Co-author network (`coauthor_network`) — D3 force

**Data:** nodes = every distinct co-author; edges = papers co-authored. YK is the central node (sienna, larger). Node size scales by `papers_together`. Edge width scales by collaboration depth. Hover shows author name + paper count + INSPIRE link.

**Notes:** ~30 nodes expected from current data. Force simulation runs for ~600 ms then freezes. Below 768 px width, replaces itself with a static SVG snapshot pre-computed at build time and inlined into the page.

### 6.2 Papers per year (`papers_per_year`) — stacked bar (Chart.js)

**Data:** count of papers per calendar year, stacked by author position: indigo (`first`) bottom, `--rule` (`middle`) middle, no `last` bar segment (kept in the donut). Current year shown in sienna. X axis: years (mono ticks). Y axis: count.

### 6.3 Cumulative citations + per-year (`citations_cumulative`) — combined chart

**Data:** muted gray bars for `citations_received_in_year`, indigo cumulative line on a secondary y-axis. Dot on the last point in sienna. Hover shows year + per-year + cumulative.

### 6.4 h-index trajectory (`h_index_curve`) — step line

**Data:** `h_index_at_end_of_year` for every year from first publication to present. Step-line (not smooth). Dashed Hirsch reference line (`h = years_since_PhD`) for context. Hover shows the actual citation-sorted list that produces that h value.

### 6.5 Author position (`author_position`) — donut

**Data:** count of papers where YK is `first`, `middle`, `last`. Indigo / sienna / `--rule` ring with center label showing `first / total` percentage. Legend mono right-aligned.

### 6.6 Top cited papers (`top_cited`) — ranked horizontal bars

**Data:** top-N papers by citation count (N = 8). Each row: rank number (mono, mark color) + truncated title (KaTeX, ellipsis after ~55 chars, full title on hover) + indigo bar proportional to citation count + numeric count (mono, right-aligned). Click row → opens INSPIRE record in new tab.

### 6.7 Journal / venue split (`journal_venue`) — horizontal bar

**Data:** count of papers by journal (PRD, EPJ C, CPC, J. Subatomic Part. Cosmol., arXiv-only, etc.). Sorted descending. arXiv-only bar uses sienna to distinguish preprint-only from journal-published.

### 6.8 Topic / keyword map (`topic_map`) — treemap (D3)

**Data:** four research themes → arXiv categories sub-cells → individual papers. Cell area = paper count. Theme cells colored by indigo lightness; "current" theme (most recent theme YK has published in) accented in sienna. Hover shows full paper title + year.

### 6.9 Derived metrics (`scripts/derive_metrics.py`)

Pure functions on the Pydantic `papers` list. Returns `DerivedMetrics` with:

```
papers_per_year:       dict[int, dict[Literal['first','middle','last'], int]]
citations_per_year:    dict[int, int]            # via paper.citation_count distributed by year proxy
cumulative_citations:  dict[int, int]
h_index_curve:         dict[int, int]
author_position_total: dict[Literal['first','middle','last'], int]
top_cited:             list[PaperRef]            # top 8
journal_split:         dict[str, int]
coauthor_graph:        dict[str, {papers: int, edges: dict[str,int]}]
treemap:               nested dict matching d3-hierarchy expectations
```

`citations_per_year` is the one fuzzy field — INSPIRE does not provide a per-year citation breakdown publicly. We approximate it from each paper's per-year citation history if reachable (`/api/literature/{id}/citations?facet_name=earliest_date`), or fall back to a flat distribution attributing all citations to the paper's own publication year. The `Refreshed YYYY·MM·DD · approximation: ...` caption notes which method was used.

### 6.10 Visual / library choices

- Chart.js 4 for bar/line/donut (charts 6.2, 6.3, 6.5, 6.7).
- D3 7 (force + hierarchy modules only) for charts 6.1 and 6.8.
- Plain SVG (no library) for charts 6.4 and 6.6 — they don't justify Chart.js overhead.

Each chart is its own Astro `.astro` file under `site/src/components/analytics/`, importing the data via `import data from "../../data/inspire.json"`.

---

## 7 · Tech stack

### 7.1 Frontend

- **Astro 5** with TypeScript and the integrations `@astrojs/tailwind`, `@astrojs/sitemap`, `@astrojs/react` (the last only for chart islands).
- **Tailwind CSS** with `darkMode: 'class'` (no dark mode shipped at launch, but the token system supports it). Theme aliases for the cream palette in `tailwind.config.ts`.
- **Chart.js 4** and **D3 7** loaded only on `/analytics` via Astro islands (`client:visible`).
- **KaTeX 0.16+** with `remark-math` + `rehype-katex` for any Markdown content, and a custom `<Math>` Astro component for in-page inline math (paper titles in publications, themes, ticker).
- **Inter** and **IBM Plex Mono** via Google Fonts CSS, self-hosted versions optional later.

### 7.2 Backend / build

- **Python 3.11+**, virtualenv at `scripts/.venv/`.
- Dependencies pinned in `scripts/requirements.txt` (`requests`, `pydantic v2`, `pyyaml`) and `scripts/requirements-dev.txt` (`pytest`, `respx`, `ruff`).
- `scripts/pytest.ini` config.

### 7.3 Repo layout

```
.
├── RS_CV/                       # CV LaTeX source (untouched)
├── scripts/                     # Python data pipeline
│   ├── inspire_client.py
│   ├── models.py
│   ├── derive_metrics.py
│   ├── fetch_inspire.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   └── tests/
│       ├── fixtures/author_2182746.json
│       ├── test_inspire_client.py
│       ├── test_models.py
│       └── test_derive_metrics.py
├── site/                        # Astro project
│   ├── astro.config.mjs
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── public/
│   │   ├── cv/CV_YKChen.pdf     # copied from RS_CV
│   │   └── photo.png            # copied from RS_CV
│   └── src/
│       ├── data/
│       │   ├── inspire.json     # committed; produced by fetch_inspire.py
│       │   ├── themes.yaml      # hand-curated arxiv_id -> theme
│       │   └── talks.yaml       # hand-curated talks
│       ├── pages/
│       │   ├── index.astro
│       │   ├── research.astro
│       │   ├── publications.astro
│       │   ├── talks.astro
│       │   ├── analytics.astro
│       │   └── cv.astro
│       ├── components/
│       │   ├── Nav.astro
│       │   ├── Footer.astro
│       │   ├── Math.astro       # KaTeX wrapper
│       │   ├── PaperRow.astro
│       │   ├── ThemeCard.astro
│       │   └── analytics/
│       │       ├── CoauthorNetwork.tsx
│       │       ├── PapersPerYear.tsx
│       │       ├── CitationsCumulative.tsx
│       │       ├── HIndexCurve.astro
│       │       ├── AuthorPosition.tsx
│       │       ├── TopCited.astro
│       │       ├── JournalSplit.tsx
│       │       └── TopicTreemap.tsx
│       └── styles/global.css    # tokens + KaTeX overrides
├── mockups/                     # committed visual references
│   └── home.html                # the hybrid A+B style mockup
├── docs/superpowers/
│   ├── specs/2026-05-18-yk-chen-homepage-design.md
│   └── plans/                   # implementation plan goes here
├── .github/workflows/
│   └── deploy.yml               # build + deploy to gh-pages
├── README.md
└── .gitignore
```

---

## 8 · Deployment

### 8.1 Hosting

GitHub Pages, default `*.github.io` URL initially. CNAME and `astro.config.mjs#site` are TBD — switch later when a custom domain is registered.

### 8.2 Build / deploy workflow

`.github/workflows/deploy.yml` triggers on push to `main`:

```yaml
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { contents: read, pages: write, id-token: write }
concurrency: { group: pages, cancel-in-progress: true }

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: site/package-lock.json }
      - run: npm ci
        working-directory: site
      - run: npm run build
        working-directory: site
      - uses: actions/upload-pages-artifact@v3
        with: { path: site/dist }
      - uses: actions/deploy-pages@v4
```

**Note:** Python is NOT invoked in CI — `inspire.json` is committed by YK locally and read from the repo. This keeps CI fast and removes the INSPIRE dependency from the deploy path.

### 8.3 Local refresh workflow

```bash
cd scripts
source .venv/bin/activate
python fetch_inspire.py            # writes ../site/src/data/inspire.json
cd ..
git add site/src/data/inspire.json
git commit -m "data: refresh INSPIRE bundle"
git push                            # triggers GH Pages rebuild
```

The script prints a one-page summary of the diff (new papers, +N citations, new top-cited).

---

## 9 · Accessibility, performance, error handling

- All charts must include `<title>` and `<desc>` SVG elements and an accompanying `<table>` (visually hidden) with raw values, so screen readers can read the data.
- Color is never the sole encoding — author-position bars carry text labels on hover and in the donut center label.
- Focus rings: 2 px solid `--accent`, 2 px offset on every interactive element. Visible on `:focus-visible` only.
- Headings are properly nested; one h1 per page; h2 for sections; nav is a `<nav aria-label="primary">`.
- Targets: Lighthouse Performance ≥ 95, Accessibility ≥ 95, on `/analytics` (the heaviest page).
- Fonts are loaded with `font-display: swap`; KaTeX stylesheet is preloaded on pages that use math.
- INSPIRE API failures during local refresh print an actionable error (rate limit / 5xx / unparseable response) and exit non-zero; the existing committed `inspire.json` is never overwritten on failure.
- LaTeX rendering failures in any title fall back to the raw `$…$` source with a console warning during build — they DO NOT break the build.

---

## 10 · Open items / TBDs (filled by YK after the spec lands)

| Item | Action | Owner |
|---|---|---|
| ORCID identifier | Add to footer + `inspire.json.author.orcid` | YK |
| Google Scholar URL | Add to footer | YK |
| GitHub username | Add to footer | YK |
| Hand-written bio paragraph for Home | Replace placeholder | YK |
| Four research-theme intro paragraphs for `/research` | Replace placeholder | YK |
| `themes.yaml` arxiv-id → theme mapping | Curate per CV groupings | YK |
| `talks.yaml` (from CV but check completeness) | Verify dates / titles | YK |
| Custom domain decision | Add CNAME and update `astro.config.mjs#site` | YK |

---

## 11 · Out of scope (deferred)

- Bilingual EN/中文 toggle.
- Server-side INSPIRE fetch on every site build.
- An RSS feed of new papers.
- Theme switcher / dark mode (the token system supports it but it isn't shipped).
- Embedded PDF viewer on `/cv` (a download link is sufficient).
- A search box (filters on `/publications` cover the use case).

---

**End of spec.**
