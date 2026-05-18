# Personal academic homepage for Yan-Ke Chen — design spec

**Date:** 2026-05-17
**Author:** YK Chen + Claude (brainstorm)
**Status:** Awaiting user review

---

## 1. Purpose & audience

A personal academic homepage for **Yan-Ke Chen (陈彦珂)**, postdoctoral researcher at the Center for High Energy Physics (CHEP), Peking University. The site presents biographical context, research themes, publications, and a **data-rich analytics dashboard** drawn from his INSPIRE-HEP author profile (`https://inspirehep.net/authors/2182746`).

**Primary audience:** international academic physics community — peers, search-committee chairs, collaborators, conference organisers, students.

**Success criteria:**
- A visitor unfamiliar with YK Chen can, in under two minutes, learn what he works on, where he is, and read his most representative papers.
- The analytics page communicates the shape of his research output (volume, citation arc, collaboration topology, thematic focus) in a single scroll.
- The owner can refresh INSPIRE data with a single command and republish in under five minutes.

**Non-goals:**
- Blog or news section.
- Contact form / mailing-list signup.
- Real-time INSPIRE queries from the browser (data is fetched at build).
- Bilingual content (English only, per user decision).

---

## 2. Information architecture

Five top-level pages, accessible from a shared top-bar nav:

| Path | Purpose | Data source |
|---|---|---|
| `/` (Home) | Hero · short bio · "by the numbers" strip · selected publications (5) · research themes (4 cards) | hand-written content + `inspire.json` |
| `/research` | One paragraph per theme × 4, each with its full publication list and selected highlights; full list of oral & poster presentations | hand-written + `inspire.json` |
| `/publications` | Full publication list, filterable by year / topic group / journal; each row: title, author list (YK bolded), venue, citation count, arXiv link, DOI link | `inspire.json` |
| `/analytics` | Four dashboard figures (see §6) | `inspire.json` (derived metrics) |
| `/cv` | HTML CV summary + prominent "Download PDF" button (linked to `CV_YKChen.pdf`) | hand-written + linked PDF |

**Footer (every page):** "Data sourced from INSPIRE-HEP. Last refreshed YYYY·MM·DD." + © + typography credit.

**Mobile:** single-column stack; nav collapses to a hamburger; figure-grids degrade to single column.

---

## 3. Visual design system — "Quiet Precision"

### 3.1 Concept

Editorial-academic minimalism. The character comes from typography, restraint, and how data and numbers are treated as visual elements — not from decoration. Reads like a beautifully set scientific publication.

### 3.2 Tokens (CSS custom properties)

```css
--paper:    #F6F4EE;   /* warm cream background, never pure white */
--paper-2:  #EFEBE1;   /* hover / elevated surface */
--ink:      #15120E;   /* warm near-black, primary text */
--ink-2:    #4C463D;   /* secondary text */
--ink-3:    #8C8579;   /* tertiary / muted text */
--rule:     #DCD5C5;   /* dividers, borders */
--rule-2:   #ECE6D6;   /* sub-dividers, faint grid */
--accent:   #1B2E5E;   /* indigo ink — links, primary line on charts */
--mark:     #B0492A;   /* sienna — used sparingly for "current" / "highlighted" only */
```

A faint SVG fractal-noise overlay (`opacity .035`, mix-blend `multiply`) gives the surface a paper feel.

### 3.3 Typography

| Role | Family | Source | Use |
|---|---|---|---|
| Display | **Newsreader** (variable, optical sizing) | Google Fonts | h1, h2, large numerals, paper titles |
| Body | **IBM Plex Sans** | Google Fonts | running text, UI labels |
| Mono | **IBM Plex Mono** | Google Fonts | arXiv IDs, metadata, axis ticks, nav |

Display rules:
- Use `font-variation-settings: "opsz" <px>` to match the rendered size — this is the single biggest reason Newsreader looks different from generic serifs.
- Italic + weight-300 italic for de-emphasised text (`<em>`).
- Tight tracking on display (`letter-spacing: -0.02em` and tighter as size grows).

### 3.4 Layout

- Max content width 1280px, fluid horizontal padding `clamp(1.5rem, 5vw, 4rem)`.
- Asymmetric two-column hero grid (1fr · 0.45fr on home; 1.4fr · 1fr on analytics hero).
- Section heads use an 8rem-wide "marginalia" column for the roman-numeral marker (`§ I`, `§ II`), with the section title to its right — echoes scientific paper sectioning.
- Dividers: 1px `--rule` between major sections; figure cards have 1px `--rule` borders.
- Generous vertical rhythm: `padding: clamp(3.5rem, 7vw, 5.5rem) 0` for blocks.

### 3.5 Motion

Restraint by default; one well-orchestrated load is worth more than scattered micro-interactions.

- **On first load**: staggered fade-up of hero children (`.stagger > *`) — 8px translate, 0.9s `cubic-bezier(.2,.7,.2,1)`, 80ms delay between siblings.
- **Sparkline in hero**: bars rise from 0 height after a 400ms hold.
- **Chart bars**: scale-X from 0 to 1 with the same easing, single play.
- **"Currently" dot**: 2.4s infinite radial pulse (only animated infinite element on the site).
- **Hover affordances**: links use a left-to-right underline grow (`background-size: 0% → 100% 1px`, 0.35s). Network nodes invert fill on hover.
- **No** scroll-jacking, parallax, or scroll-snap.
- Respect `prefers-reduced-motion`: disable all entrance animations and the pulse.

### 3.6 Distinctive moves (not negotiable — these are what make it not-generic)

- Section markers as roman numerals (`§ I`, `§ II`, ...) in sienna.
- Citation counts rendered as **oversized serif numerals** beside paper titles.
- An **inline sparkline** of papers-per-year embedded mid-sentence in the hero prose.
- Right-aligned monospace "margin notes" for metadata.
- Donut chart with a serif numeral (total) in its center, mono small caps below.

---

## 4. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Framework | **Astro 5+** | Ships zero JS for content pages; islands only where charts live. Static output deploys anywhere. |
| Language | **TypeScript** for components, JS interop where needed | Tightens the analytics page code where chart shapes matter. |
| Styling | **Tailwind CSS** + `@apply` for component-level abstractions; CSS custom properties for tokens | Tokens defined once, used everywhere. Keeps the "Quiet Precision" system enforceable. |
| Simple charts (line, bar, donut, h-index strip) | **Chart.js 4** | One-liner API, accepts our color tokens, easy to theme. |
| Force-directed network | **D3.js 7** (force simulation only — no other modules) | Chart.js can't do force layouts; D3 is the standard. |
| Data fetch | **Python 3.11+** script using `requests` + `pandas` | Matches user's strengths (scientific computing). Writes deterministic JSON. |
| Fonts | Google Fonts (Newsreader, IBM Plex Sans, IBM Plex Mono) | No license cost, no self-hosting complexity. |

**Two alternatives explicitly rejected:**
- *Next.js* — heavier; we never need server runtime since the site is read-only.
- *Hugo academic theme* — locks aesthetic into a template and would fight the "Quiet Precision" direction.

---

## 5. INSPIRE data pipeline

### 5.1 Flow

```
[Python build script]               [Astro build]            [Static output]
fetch_inspire.py     ──writes──►   src/data/inspire.json  ──reads──►  dist/**/*.html
                                                                       dist/**/*.json
```

The pipeline runs **at build time only**. The browser never calls INSPIRE.

### 5.2 The Python script (`scripts/fetch_inspire.py`)

Calls these INSPIRE-HEP REST endpoints:

1. `GET https://inspirehep.net/api/authors/2182746` — author profile (canonical name, ORCID, affiliations history).
2. `GET https://inspirehep.net/api/literature?q=author:Yan-Ke.Chen.1&size=250&fields=titles,authors,publication_info,arxiv_eprints,citation_count,citation_count_without_self_citations,references,first_author,collaborations,inspire_categories,abstracts,dois,texkeys`
   — paginated paper list (`page=1,2,...` until `next` link absent).
3. For each paper, the `authors[].record.$ref` is followed to resolve coauthor names + affiliations. (Coauthor records are cached locally to keep re-runs cheap.)

**Output:** `src/data/inspire.json` with the shape below. Derived metrics (h-index over time, keyword counts, journal counts, top-N papers, institution counts) are computed once and stored — so Astro components never re-derive on render.

```jsonc
{
  "fetched_at": "2026-05-17T10:15:00Z",
  "author": {
    "id": "2182746",
    "name": "Yan-Ke Chen",
    "name_zh": "陈彦珂",
    "current_position": { "rank": "PostDoc", "institution": "Peking U., CHEP", "start": "2025-07" },
    "orcid": "…",
    "arxiv": "…"
  },
  "papers": [
    {
      "inspire_id": "…",
      "title": "Existence of the DD*K̄* and BB*K* three-body molecular states",
      "authors": [{ "name": "Y.-K. Chen", "is_you": true }, …],
      "venue": { "journal": "Phys. Rev. D", "volume": "…", "page": "…", "year": 2025 },
      "arxiv_id": "2602.12010",
      "doi": "10.1103/…",
      "citations": 12,
      "citations_no_self": 11,
      "year": 2025,
      "topic_group": "exotic-coupled-channel"   // hand-mapped, see §5.3
    }, …
  ],
  "metrics": {
    "papers_total": 17,
    "citations_total": 432,
    "h_index": 11,
    "first_author_count": 5,
    "by_year": [
      { "year": 2020, "papers": 0, "cum_citations": 0,   "h_index": 0  },
      { "year": 2021, "papers": 1, "cum_citations": 5,   "h_index": 1  },
      …
    ],
    "top_papers": [ /* top 10 by citations */ ],
    "keywords": [
      { "term": "tetraquark", "count": 12 },
      { "term": "heavy",      "count": 11 }, …
    ],
    "journals": [
      { "name": "Phys. Rev. D",     "count": 12 },
      { "name": "Eur. Phys. J. C",  "count": 2  }, …
    ],
    "coauthors": [
      { "name": "L. Meng",   "joint_papers": 9,  "inspire_id": "…", "current_institution": "PKU" },
      …
    ],
    "institutions": [
      { "name": "Peking University",   "city": "Beijing, CN",   "joint_papers": 14 }, …
    ]
  }
}
```

### 5.3 Topic group mapping

INSPIRE doesn't categorise papers into the user's four research themes. We maintain a tiny YAML file `scripts/topic_groups.yml` that maps each paper's INSPIRE id (or arXiv id, more stable) to one of the four group keys:

```yaml
em-chiral-pt:
  - 2412.02297
  - 2506.18800
  - 2602.05502
exotic-coupled-channel:
  - 2308.12424   # Virtual states / complex scaling
  - 2602.12010   # DD*K̄* and BB*K* three-body molecular states
  # NOTE: the CV's LaTeX source lists arXiv:2308.12424 twice (also against
  # the X(3872) coupled-channel paper) — that is a CV typo. The X(3872)
  # paper's real arXiv id must be looked up from INSPIRE and added here
  # by the build script's warning path on first run.
production:
  - 2009.01182
  - 2302.01696
spectrum-quark-models:
  - 2310.14597
  - 2508.11161
  - 2401.14899
  - 2310.13354
  - 2409.03373
  - 2406.17824
  - 2309.17068
  - 2211.09021
  - 2408.00503
```

When a new paper appears in INSPIRE that isn't in the YAML, the build script emits a warning and assigns it to `uncategorised` — visible on the publications page until the YAML is updated.

### 5.4 Error handling & resilience

- **HTTP failures**: retry with exponential backoff (3 attempts, 1s/2s/4s). If still failing, the build fails loudly with a non-zero exit — we never silently publish stale data without saying so.
- **Schema drift**: the script validates the response against a Pydantic model. Unknown fields are logged but ignored; missing required fields fail the build.
- **Stale-data fallback**: if INSPIRE is reachable but returns 0 papers (suspicious), the script aborts before overwriting the existing `inspire.json`. The previously committed file remains; the footer's "Last refreshed" date does not advance.
- **Rate limiting**: INSPIRE allows ~15 req/sec unauthenticated. The script sleeps 100ms between calls and uses a local on-disk JSON cache for coauthor-record lookups (`.cache/inspire-records/<id>.json`), so re-runs touch the network only for new authors.
- **Coauthor identity ambiguity**: if a coauthor record has no `$ref`, we fall back to the literal name string and mark `inspire_id: null` in the JSON. The coauthor still appears in the network, but unlinked.

---

## 6. Analytics page specification

Four dashboard figures, each rendered inside a `.figure` card with header (title + figure number) and caption.

### 6.1 § I — Trajectory

**Composite chart (Chart.js, mixed bar + line, dual y-axis):**
- X-axis: years 2020 → current year.
- Left y-axis: papers per year (bar, ink). Current year bar in sienna.
- Right y-axis: cumulative citations (line, indigo accent; soft indigo fill below the line at 12% alpha).
- Annotation: the final data point gets a callout line + label "<N> cites total".

**h-index strip (Chart.js bar):**
- Same x-axis, height ≈ 110px. Each year's h-index as a small bar. Current year sienna.

**Side panel (4 stat cards):**
- 17 papers / ~430 cites / h-index 11 / 5 first-author papers.
- Each card: oversized serif numeral, mono small-caps label, one-line sans context.

### 6.2 § II — Reception

**Top-10 papers list (custom Tailwind component, not Chart.js):**
- Three-column grid: rank · (title + journal + bar) · citation count (oversized serif).
- Top paper highlighted in sienna for both the bar fill and the numeral.
- Hover reveals arXiv / DOI links (extends the bar row).

**Citation distribution view (deferred):** initial release ships only the top-10. A future enhancement may add a strip plot or histogram across all 17 papers; explicitly out of scope for v1 to keep the page tight.

### 6.3 § III — Themes & venues

**Two figures side-by-side:**

*Keyword frequency (custom component):*
- Top-10 terms extracted from titles + abstracts.
- Each row: term (serif) + qualifier in muted italic (e.g., "tetraquark *compact / molecular*") + horizontal bar in ink-2 + count in mono.
- Term extraction pipeline (in `scripts/fetch_inspire.py`):
  1. Concatenate `title` + `abstract` per paper.
  2. Lowercase, strip LaTeX (`$…$`, `\…`).
  3. Tokenize on whitespace + punctuation; remove a stopword list (English + physics-generic like "states", "model", "theory").
  4. Lemmatise via `nltk` (`wordnet`) — singularise plurals.
  5. Count term frequencies across papers (paper-level, not token-level).
  6. Manually curate a small `--keep` and `--collapse` map in `topic_groups.yml` to merge synonyms (e.g., "DH" → "doubly heavy", "χPT" / "ChPT" / "chiral perturbation theory" → "χPT").

*Journal donut (Chart.js doughnut):*
- Stroke-only style (no fill ring), with the four palette colors.
- Center: total paper count in display serif, "papers" mono caps below.
- Legend on the right: swatch + name + count (tabular figures via `font-feature-settings: "tnum"`).

### 6.4 § IV — Collaboration

**Coauthor network (D3 force simulation):**
- 16:10 aspect, ~800×500 viewBox, max ~30 nodes.
- You: sienna fill, larger radius (20px), serif italic label.
- Others: outlined nodes (paper fill, ink stroke); radius = `4 + sqrt(joint_papers) * 4`; mono labels.
- Edges: ink-3 at 35% opacity. An edge exists between every coauthor pair that has at least one joint paper (so YK connects to all; coauthors connect among themselves only when they've coauthored).
- Force: `forceManyBody(-180)`, `forceLink().distance(node => 60 + 6/sqrt(joint))`, `forceCenter`, `forceCollide(node.r + 4)`.
- Interactions: drag-to-reposition; hover shows tooltip with joint paper count + click-through to coauthor INSPIRE profile.
- A radial gradient scrim fades the edges of the viewport to `--paper` so the graph doesn't feel boxed in.

**Institution bars (custom component):**
- Top 6 institutions by joint-paper count.
- Same row pattern as keyword frequency: name (with city in muted italic) · indigo bar · count.

**Deferred:** a world map overlay. Sketched in §4 of the mockup caption but not in v1 — most institutions are domestic, so the map would be visually sparse. Re-evaluate when international collaborations expand.

---

## 7. Project structure

```
personal_profile/
├── CLAUDE.md                       # written after writing-plans completes
├── README.md
├── RS_CV/                          # source CV (kept as-is)
│   ├── CV_YKChen.pdf
│   ├── CV_YKChen.tex
│   └── photo.png
├── docs/
│   └── superpowers/specs/
│       └── 2026-05-17-yk-chen-homepage-design.md
├── mockups/                        # static HTML mockups (visual reference)
│   ├── index.html
│   └── analytics.html
├── scripts/
│   ├── fetch_inspire.py            # the build-time INSPIRE fetcher
│   ├── topic_groups.yml            # hand-mapped paper → theme
│   └── requirements.txt
├── site/                           # the Astro project
│   ├── astro.config.mjs
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── public/
│   │   ├── cv/CV_YKChen.pdf        # copy of RS_CV/CV_YKChen.pdf
│   │   └── photo.jpg
│   └── src/
│       ├── data/
│       │   └── inspire.json        # produced by scripts/fetch_inspire.py
│       ├── layouts/
│       │   └── Base.astro          # shell: head, top bar, footer, grain overlay
│       ├── components/
│       │   ├── Hero.astro
│       │   ├── NumbersStrip.astro
│       │   ├── PubList.astro       # selected + full list, mode prop
│       │   ├── ThemeCard.astro
│       │   ├── Figure.astro        # bordered chart-card wrapper
│       │   ├── Sparkline.astro
│       │   ├── charts/
│       │   │   ├── Trajectory.tsx   # Chart.js mixed bar+line — React island
│       │   │   ├── HIndexStrip.tsx
│       │   │   ├── TopPapers.astro
│       │   │   ├── Keywords.astro
│       │   │   ├── JournalDonut.tsx
│       │   │   ├── CoauthorNetwork.tsx  # D3 — React island
│       │   │   └── Institutions.astro
│       │   └── ui/  …
│       └── pages/
│           ├── index.astro          # /
│           ├── research.astro       # /research
│           ├── publications.astro   # /publications
│           ├── analytics.astro      # /analytics
│           └── cv.astro             # /cv
└── .github/workflows/
    └── refresh-inspire.yml          # (optional, deferred) GH Action: weekly fetch + PR
```

---

## 8. Build & deploy story

**Local development (the user's daily loop):**

```bash
# refresh data when needed (e.g., new paper appeared on INSPIRE)
python scripts/fetch_inspire.py          # writes site/src/data/inspire.json

# develop
cd site && npm run dev                   # http://localhost:4321

# build
cd site && npm run build                 # produces site/dist/

# preview production
cd site && npm run preview
```

**Deploy (chosen later — user said "decide later"):**

The `site/dist/` directory is fully static. Any of these work without code changes:
- GitHub Pages — push `dist/` to a `gh-pages` branch or use the official Pages action.
- Netlify / Vercel / Cloudflare Pages — point at the repo with `cd site && npm run build` as the build command and `site/dist` as the publish directory.
- Institutional / PKU hosting — `rsync site/dist/ user@host:/path/` after build.
- The optional GitHub Action (`refresh-inspire.yml`, deferred) reruns the Python fetcher weekly and opens a PR with the updated `inspire.json` for review before deploy.

---

## 9. Accessibility & responsiveness

- All charts have an `aria-label` describing the data and what trend it shows.
- The coauthor network has a text-list fallback rendered below it (visually hidden until tabbed-to or in print) listing every coauthor with joint-paper count — this is the source of truth that the visualisation paraphrases.
- Color contrast: `--ink` on `--paper` exceeds WCAG AAA. Accent indigo + ink-2 on paper both meet AA for normal text.
- `prefers-reduced-motion` disables all entrance and pulse animations.
- Mobile (≤720px): all multi-column layouts collapse to single column; the coauthor network keeps aspect ratio and shrinks; the journal donut stacks above its legend.
- Keyboard: every link and node is reachable; focus-visible outline is 2px indigo with 3px offset.

---

## 10. Open questions / decisions to revisit after v1

- **Dark mode**: deliberately deferred. The cream-paper aesthetic is the design's signature; a dark variant needs separate thought (not just inverted colors).
- **Search-engine optimisation**: minimal in v1 (just the obvious meta tags + JSON-LD `Person` schema with `sameAs` to INSPIRE / ORCID / arXiv / Google Scholar).
- **Selected vs full publications**: on `/`, "Selected" means the 5 the user hand-picks (configured in a small `selected.yml`), not "top 5 by citations" — to give the user editorial control.
- **Talks page**: kept on `/research` for v1; if it grows past ~20 entries, split into `/talks`.
- **Analytics auto-refresh**: ships as manual command for v1; the GitHub Action that auto-refreshes weekly is deferred until the manual flow has been used for a few months.

---

## 11. Acceptance checklist (used to validate the build)

- [ ] Home page renders all sections with real INSPIRE data, no placeholder strings.
- [ ] All five top-bar links resolve to a styled page (no 404, no `#`).
- [ ] `scripts/fetch_inspire.py` succeeds on a fresh machine with `pip install -r scripts/requirements.txt` and writes a non-empty, schema-valid `inspire.json`.
- [ ] `npm run build` succeeds with zero warnings about missing data and produces `site/dist/`.
- [ ] All four analytics figures render with real numbers (no placeholder values from the mockups).
- [ ] The site passes Lighthouse with Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 95 on mobile.
- [ ] `prefers-reduced-motion` disables entrance animations and the "currently" dot pulse.
- [ ] The "Last refreshed" date in the footer matches `fetched_at` in `inspire.json`.

---

## 12. References

- INSPIRE-HEP REST API: https://github.com/inspirehep/rest-api-doc
- Author profile (Yan-Ke Chen): https://inspirehep.net/authors/2182746
- Mockups (committed): `mockups/index.html`, `mockups/analytics.html`
- Source CV: `RS_CV/CV_YKChen.tex`, `RS_CV/CV_YKChen.pdf`
