# YK Chen academic homepage — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static Astro 5 personal academic homepage for Yan-Ke Chen (PKU CHEP postdoc, hep-ph), driven by an INSPIRE-HEP-fed JSON bundle, with an 8-figure analytics dashboard, deployed to GitHub Pages.

**Architecture:** A two-process pipeline. A Python script (`scripts/fetch_inspire.py`) hits the INSPIRE REST API, derives metrics, and writes `site/src/data/inspire.json`. An Astro 5 project consumes that JSON at build time and renders six static pages. Chart libraries (Chart.js, D3) are loaded only on the analytics page via `client:visible` islands; the rest of the site ships zero JS. Mathematics is rendered server-side with KaTeX so paper titles like `$DD^*\bar{K}^*$` come out correct without a client-side math engine.

**Tech Stack:**
- Python 3.11+ (`httpx`, `pydantic v2`, `pyyaml`, `pytest`, `respx`)
- Node 20+, Astro 5 + TypeScript
- Tailwind CSS 3 + `@astrojs/tailwind`
- Chart.js 4 (vanilla), D3 7 (force + hierarchy modules only)
- KaTeX 0.16 (server-side rendering via `katex` npm package)
- Inter + IBM Plex Mono via Google Fonts

**Spec:** `docs/superpowers/specs/2026-05-18-yk-chen-homepage-design.md`

**Implementation refinements from spec:**
- HTTP client uses `httpx` (sync) instead of `requests`, because `respx` (our mock library) targets `httpx`. The API surface is essentially identical.
- Chart components are pure `.astro` files with vanilla `<script>` blocks that import Chart.js / D3 directly. `@astrojs/react` is **not** added — there is no benefit to React for these simple data-in/SVG-out components and dropping it removes a build dependency.

---

## Phase A · Scaffolding

### Task A1: Write README and freeze repo skeleton

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
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
python scripts/fetch_inspire.py

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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with project layout and dev/build instructions"
```

---

### Task A2: Bootstrap Python toolchain

**Files:**
- Create: `scripts/requirements.txt`
- Create: `scripts/requirements-dev.txt`
- Create: `scripts/pytest.ini`
- Create: `scripts/tests/__init__.py`
- Create: `scripts/__init__.py`

- [ ] **Step 1: Write `scripts/requirements.txt`**

```text
httpx==0.27.2
pydantic==2.9.2
pyyaml==6.0.2
```

- [ ] **Step 2: Write `scripts/requirements-dev.txt`**

```text
-r requirements.txt
pytest==8.3.3
respx==0.21.1
pytest-cov==5.0.0
ruff==0.6.9
```

- [ ] **Step 3: Write `scripts/pytest.ini`**

```ini
[pytest]
testpaths = tests
addopts = -ra --strict-markers --strict-config
filterwarnings =
    error
```

- [ ] **Step 4: Create the empty package markers**

```bash
mkdir -p scripts/tests
touch scripts/__init__.py scripts/tests/__init__.py
```

- [ ] **Step 5: Create the venv and install**

```bash
python3.11 -m venv scripts/.venv
source scripts/.venv/bin/activate
pip install -r scripts/requirements.txt -r scripts/requirements-dev.txt
pytest --version
```

Expected: pytest prints version 8.3.3 with no errors.

- [ ] **Step 6: Commit**

```bash
git add scripts/requirements.txt scripts/requirements-dev.txt scripts/pytest.ini scripts/__init__.py scripts/tests/__init__.py
git commit -m "chore(scripts): pin Python dependencies and configure pytest"
```

---

### Task A3: Initialise the Astro project

**Files:**
- Create: `site/package.json`, `site/astro.config.mjs`, `site/tsconfig.json`, `site/tailwind.config.ts`, `site/postcss.config.js`, `site/src/styles/global.css`

- [ ] **Step 1: Scaffold Astro non-interactively**

```bash
cd site 2>/dev/null && echo "site/ already exists" && cd ..
npm create astro@latest site -- --template minimal --typescript strict --no-install --no-git --skip-houston --yes
```

If `site/` already exists from prior work, **stop and ask before overwriting**.

- [ ] **Step 2: Install dependencies inside `site/`**

```bash
cd site
npm install
npm install -D @astrojs/tailwind tailwindcss@3 postcss autoprefixer
npm install chart.js@4 d3@7 katex@0.16
npm install -D @types/d3@7
cd ..
```

- [ ] **Step 3: Replace `site/astro.config.mjs`**

```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.github.io',          // TBD — update when domain is decided
  integrations: [
    tailwind({ applyBaseStyles: false }),     // we apply our own base styles in global.css
    sitemap(),
  ],
  build: { format: 'directory' },
});
```

- [ ] **Step 4: Install the sitemap integration**

```bash
cd site && npm install @astrojs/sitemap && cd ..
```

- [ ] **Step 5: Write `site/tailwind.config.ts`**

```typescript
import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{astro,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        paper:   '#F6F4EE',
        'paper-2': '#EFEBE1',
        ink:     '#15120E',
        'ink-2': '#4C463D',
        'ink-3': '#8C8579',
        rule:    '#DCD5C5',
        'rule-2': '#ECE6D6',
        accent:  '#1B2E5E',
        mark:    '#B0492A',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      letterSpacing: {
        tightest: '-0.035em',
      },
    },
  },
  plugins: [],
} satisfies Config;
```

- [ ] **Step 6: Write `site/postcss.config.js`**

```javascript
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};
```

- [ ] **Step 7: Write `site/src/styles/global.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
@import 'katex/dist/katex.min.css';

:root {
  color-scheme: light;
}

html, body {
  background: theme('colors.paper');
  color: theme('colors.ink');
  font-family: theme('fontFamily.sans');
  -webkit-font-smoothing: antialiased;
}

/* Paper-feel noise overlay */
body::before {
  content: '';
  position: fixed; inset: 0;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2"/></filter><rect width="100%" height="100%" filter="url(%23n)" opacity="0.4"/></svg>');
  mix-blend-mode: multiply;
  opacity: 0.035;
  pointer-events: none;
  z-index: 0;
}

/* Make KaTeX inherit body font-size by default */
.katex { font-size: 1em !important; }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
```

- [ ] **Step 8: Replace `site/tsconfig.json`**

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "baseUrl": "./",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

- [ ] **Step 9: Smoke-test the build**

```bash
cd site && npm run build && cd ..
```

Expected: build completes without error and `site/dist/` exists.

- [ ] **Step 10: Commit**

```bash
git add site/package.json site/package-lock.json site/astro.config.mjs site/tsconfig.json site/tailwind.config.ts site/postcss.config.js site/src/styles/global.css
git rm site/src/pages/index.astro 2>/dev/null || true
git add -u site/
git commit -m "feat(site): Astro 5 scaffold with Tailwind, KaTeX, design tokens"
```

---

### Task A4: Commit static assets from RS_CV

**Files:**
- Create: `site/public/photo.png`
- Create: `site/public/cv/CV_YKChen.pdf`

- [ ] **Step 1: Copy the photo and PDF into `site/public/`**

```bash
mkdir -p site/public/cv
cp RS_CV/photo.png site/public/photo.png
cp RS_CV/CV_YKChen.pdf site/public/cv/CV_YKChen.pdf
```

- [ ] **Step 2: Verify they're not silly-large for static hosting**

```bash
ls -lh site/public/photo.png site/public/cv/CV_YKChen.pdf
```

Expected: photo < 1 MB, PDF < 5 MB. If photo is larger, run `sips -Z 1200 site/public/photo.png` (macOS) to shrink to 1200 px max dimension.

- [ ] **Step 3: Commit**

```bash
git add site/public/photo.png site/public/cv/CV_YKChen.pdf
git commit -m "assets: copy photo and CV PDF from RS_CV into site/public/"
```

---

## Phase B · Python data pipeline (TDD)

### Task B1: Pydantic models for the INSPIRE bundle

**Files:**
- Create: `scripts/models.py`
- Create: `scripts/tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

```python
# scripts/tests/test_models.py
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from scripts.models import (
    Author, AuthorProfile, JournalRef, Paper,
    DerivedMetrics, InspireBundle,
)


def test_author_minimal():
    a = Author(name='Y. K. Chen', is_yk=True, inspire_id='2182746')
    assert a.is_yk
    assert a.inspire_id == '2182746'


def test_paper_inspects_yk_first():
    paper = Paper(
        arxiv_id='2308.12424',
        inspire_id='2680001',
        title='Virtual states in coupled-channel problems',
        authors=[
            Author(name='Y. K. Chen', is_yk=True),
            Author(name='L. Meng', is_yk=False),
        ],
        year=2024,
        journal_ref=JournalRef(name='Phys. Rev. D', volume='109', page='034006', year=2024),
        doi='10.1103/PhysRevD.109.034006',
        citation_count=12,
        arxiv_categories=['hep-ph'],
        author_position='first',
    )
    assert paper.is_yk_first


def test_paper_position_validation():
    with pytest.raises(ValidationError):
        Paper(
            arxiv_id='x', inspire_id='1',
            title='t', authors=[], year=2024,
            journal_ref=None, doi=None,
            citation_count=0, arxiv_categories=[],
            author_position='last_first',  # invalid
        )


def test_bundle_round_trip():
    bundle = InspireBundle(
        fetched_at=datetime(2026, 5, 18, tzinfo=timezone.utc),
        author=AuthorProfile(
            recid='2182746',
            name='Yan-Ke Chen',
            current_affiliation='Peking University',
            orcid=None,
        ),
        papers=[],
        metrics=DerivedMetrics.empty(),
        themes={},
    )
    j = bundle.model_dump_json()
    InspireBundle.model_validate_json(j)
```

- [ ] **Step 2: Run the tests — expect failures**

```bash
cd scripts && pytest tests/test_models.py -v
```

Expected: ImportError / module not found for `scripts.models`.

- [ ] **Step 3: Write `scripts/models.py`**

```python
"""Pydantic schema for the INSPIRE bundle written to inspire.json."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

AuthorPosition = Literal['first', 'middle', 'last', 'sole']


class Author(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    is_yk: bool = False
    inspire_id: Optional[str] = None


class AuthorProfile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    recid: str
    name: str
    current_affiliation: Optional[str] = None
    orcid: Optional[str] = None


class JournalRef(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    volume: Optional[str] = None
    page: Optional[str] = None
    year: int


class Paper(BaseModel):
    model_config = ConfigDict(extra='forbid')
    arxiv_id: str
    inspire_id: str
    title: str                         # raw LaTeX preserved
    authors: list[Author]
    year: int
    journal_ref: Optional[JournalRef]
    doi: Optional[str]
    citation_count: int = 0
    arxiv_categories: list[str] = Field(default_factory=list)
    author_position: AuthorPosition
    theme_slug: Optional[str] = None

    @property
    def is_yk_first(self) -> bool:
        return self.author_position == 'first' or self.author_position == 'sole'


class CoauthorNode(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    papers_with_yk: int
    inspire_id: Optional[str] = None


class CoauthorEdge(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: str  # author name (or inspire_id once we have it)
    target: str
    weight: int  # number of shared papers


class CoauthorGraph(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nodes: list[CoauthorNode]
    edges: list[CoauthorEdge]


class TreemapNode(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    value: Optional[int] = None
    children: Optional[list['TreemapNode']] = None


class PaperRef(BaseModel):
    model_config = ConfigDict(extra='forbid')
    arxiv_id: str
    inspire_id: str
    title: str
    citation_count: int


class DerivedMetrics(BaseModel):
    model_config = ConfigDict(extra='forbid')
    papers_per_year: dict[int, dict[AuthorPosition, int]]
    citations_per_year: dict[int, int]
    citations_per_year_method: Literal['exact', 'approximate']
    cumulative_citations: dict[int, int]
    h_index_curve: dict[int, int]
    author_position_total: dict[AuthorPosition, int]
    top_cited: list[PaperRef]
    journal_split: dict[str, int]
    coauthor_graph: CoauthorGraph
    treemap: TreemapNode

    @classmethod
    def empty(cls) -> 'DerivedMetrics':
        return cls(
            papers_per_year={},
            citations_per_year={},
            citations_per_year_method='approximate',
            cumulative_citations={},
            h_index_curve={},
            author_position_total={'first': 0, 'middle': 0, 'last': 0, 'sole': 0},
            top_cited=[],
            journal_split={},
            coauthor_graph=CoauthorGraph(nodes=[], edges=[]),
            treemap=TreemapNode(name='root', children=[]),
        )


class InspireBundle(BaseModel):
    model_config = ConfigDict(extra='forbid')
    fetched_at: datetime
    author: AuthorProfile
    papers: list[Paper]
    metrics: DerivedMetrics
    themes: dict[str, list[str]]  # theme_slug -> [arxiv_id, ...]
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd scripts && pytest tests/test_models.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/models.py scripts/tests/test_models.py
git commit -m "feat(scripts): Pydantic schema for the INSPIRE bundle"
```

---

### Task B2: INSPIRE HTTP client with retry, throttle, and cache

**Files:**
- Create: `scripts/inspire_client.py`
- Create: `scripts/tests/test_inspire_client.py`
- Create: `scripts/tests/fixtures/author_2182746.json` (small stub; full fixture comes from Task B5)

- [ ] **Step 1: Write a minimal real fixture stub**

```bash
mkdir -p scripts/tests/fixtures
cat > scripts/tests/fixtures/author_2182746.json << 'EOF'
{
  "metadata": {
    "name": {"value": "Chen, Yan-Ke", "preferred_name": "Yan-Ke Chen"},
    "positions": [
      {"current": true, "institution": "Peking U.", "rank": "POSTDOC"}
    ],
    "ids": [{"schema": "INSPIRE BAI", "value": "Yan.Ke.Chen.1"}],
    "orcid": null
  }
}
EOF
```

- [ ] **Step 2: Write the failing tests**

```python
# scripts/tests/test_inspire_client.py
import json
from pathlib import Path

import httpx
import pytest
import respx

from scripts.inspire_client import InspireClient, InspireError

FIXTURE_AUTHOR = json.loads(
    (Path(__file__).parent / 'fixtures' / 'author_2182746.json').read_text()
)


@respx.mock
def test_fetch_author_parses_name_and_affiliation():
    respx.get('https://inspirehep.net/api/authors/2182746').mock(
        return_value=httpx.Response(200, json=FIXTURE_AUTHOR)
    )
    client = InspireClient(cache_dir=None)
    profile = client.fetch_author('2182746')
    assert profile.recid == '2182746'
    assert profile.name == 'Yan-Ke Chen'
    assert profile.current_affiliation == 'Peking U.'


@respx.mock
def test_fetch_author_retries_on_502():
    route = respx.get('https://inspirehep.net/api/authors/2182746').mock(
        side_effect=[
            httpx.Response(502, json={}),
            httpx.Response(200, json=FIXTURE_AUTHOR),
        ]
    )
    client = InspireClient(cache_dir=None, retry_base_delay=0.0)
    profile = client.fetch_author('2182746')
    assert profile.name == 'Yan-Ke Chen'
    assert route.call_count == 2


@respx.mock
def test_fetch_author_raises_after_max_retries():
    respx.get('https://inspirehep.net/api/authors/2182746').mock(
        return_value=httpx.Response(503, json={})
    )
    client = InspireClient(cache_dir=None, max_retries=2, retry_base_delay=0.0)
    with pytest.raises(InspireError, match='5xx'):
        client.fetch_author('2182746')


@respx.mock
def test_fetch_author_works_paginates(tmp_path):
    base = 'https://inspirehep.net/api/literature'
    respx.get(base, params={'q': 'a 2182746', 'size': 250, 'page': 1}).mock(
        return_value=httpx.Response(200, json={
            'hits': {'total': 251, 'hits': [{'metadata': {'arxiv_eprints': [{'value': str(i)}]}} for i in range(250)]},
        })
    )
    respx.get(base, params={'q': 'a 2182746', 'size': 250, 'page': 2}).mock(
        return_value=httpx.Response(200, json={
            'hits': {'total': 251, 'hits': [{'metadata': {'arxiv_eprints': [{'value': '999'}]}}]},
        })
    )
    client = InspireClient(cache_dir=None)
    raw = client.fetch_author_works('2182746')
    assert len(raw) == 251


def test_cache_round_trip(tmp_path):
    cache = tmp_path / 'cache'
    with respx.mock:
        respx.get('https://inspirehep.net/api/authors/2182746').mock(
            return_value=httpx.Response(200, json=FIXTURE_AUTHOR)
        )
        InspireClient(cache_dir=cache).fetch_author('2182746')
    # second call should be cache-only (no HTTP mock => would error if called)
    profile = InspireClient(cache_dir=cache).fetch_author('2182746')
    assert profile.name == 'Yan-Ke Chen'
```

- [ ] **Step 3: Run tests — expect failures (ImportError)**

```bash
cd scripts && pytest tests/test_inspire_client.py -v
```

- [ ] **Step 4: Write `scripts/inspire_client.py`**

```python
"""Synchronous INSPIRE-HEP REST client with retry, throttle, and disk cache."""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import httpx

from scripts.models import AuthorProfile

log = logging.getLogger(__name__)

INSPIRE_BASE = 'https://inspirehep.net/api'
USER_AGENT = 'yan-ke-chen-homepage/0.1 (+mailto:chenyanke@pku.edu.cn)'


class InspireError(RuntimeError):
    """Raised when INSPIRE returns an unrecoverable error."""


class InspireClient:
    """Thin synchronous client over the INSPIRE REST API."""

    def __init__(
        self,
        cache_dir: Optional[Path | str] = Path('scripts/.cache/inspire'),
        max_retries: int = 5,
        retry_base_delay: float = 2.0,
        throttle_seconds: float = 1.0,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.throttle_seconds = throttle_seconds
        self._last_call_at = 0.0
        self._http = httpx.Client(
            headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'},
            timeout=httpx.Timeout(30.0, connect=10.0),
        )

    # ----- public API --------------------------------------------------------

    def fetch_author(self, recid: str) -> AuthorProfile:
        data = self._get_json(f'/authors/{recid}')
        meta = data.get('metadata', {})
        name = meta.get('name', {}).get('preferred_name') or meta.get('name', {}).get('value', '')
        affil = None
        for pos in meta.get('positions') or []:
            if pos.get('current'):
                affil = pos.get('institution')
                break
        orcid = None
        for ident in meta.get('ids') or []:
            if ident.get('schema') == 'ORCID':
                orcid = ident.get('value')
        return AuthorProfile(recid=recid, name=name, current_affiliation=affil, orcid=orcid)

    def fetch_author_works(self, recid: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        page = 1
        page_size = 250
        while True:
            data = self._get_json(
                '/literature',
                params={'q': f'a {recid}', 'size': page_size, 'page': page,
                        'fields': 'titles,authors,arxiv_eprints,publication_info,dois,'
                                  'citation_count,arxiv_eprints,first_author,collaborations,'
                                  'preprint_date,publication_info,inspire_categories'},
            )
            hits = (data.get('hits') or {}).get('hits') or []
            out.extend(hits)
            total = (data.get('hits') or {}).get('total') or 0
            if page * page_size >= total:
                return out
            page += 1

    # ----- internals ---------------------------------------------------------

    def _get_json(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        cache_key = self._cache_key(path, params)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached
        body = self._request_with_retries(path, params)
        self._write_cache(cache_key, body)
        return body

    def _request_with_retries(self, path: str, params: Optional[dict]) -> dict[str, Any]:
        url = f'{INSPIRE_BASE}{path}'
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            r = self._http.get(url, params=params)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429 or 500 <= r.status_code < 600:
                delay = self.retry_base_delay * (2 ** (attempt - 1))
                log.warning('INSPIRE %s on %s — retry %d/%d in %.1fs',
                            r.status_code, url, attempt, self.max_retries, delay)
                time.sleep(delay)
                continue
            raise InspireError(f'INSPIRE {r.status_code} on {url}: {r.text[:200]}')
        raise InspireError(f'INSPIRE {r.status_code} (5xx/429) on {url} after {self.max_retries} attempts')

    def _throttle(self) -> None:
        delta = time.monotonic() - self._last_call_at
        if delta < self.throttle_seconds:
            time.sleep(self.throttle_seconds - delta)
        self._last_call_at = time.monotonic()

    def _cache_key(self, path: str, params: Optional[dict]) -> Optional[Path]:
        if not self.cache_dir:
            return None
        raw = json.dumps({'p': path, 'q': params}, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return self.cache_dir / f'{digest}.json'

    def _read_cache(self, key: Optional[Path]) -> Optional[dict[str, Any]]:
        if key and key.is_file():
            return json.loads(key.read_text())
        return None

    def _write_cache(self, key: Optional[Path], body: dict[str, Any]) -> None:
        if key:
            key.write_text(json.dumps(body))
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd scripts && pytest tests/test_inspire_client.py -v
```

Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/inspire_client.py scripts/tests/test_inspire_client.py scripts/tests/fixtures/author_2182746.json
git commit -m "feat(scripts): INSPIRE httpx client with retry, throttle, cache"
```

---

### Task B3: Paper-record parser (INSPIRE JSON → `Paper`)

**Files:**
- Create: `scripts/parsers.py`
- Create: `scripts/tests/test_parsers.py`
- Create: `scripts/tests/fixtures/literature_sample.json`

- [ ] **Step 1: Capture two representative INSPIRE literature records as a fixture**

Save the following as `scripts/tests/fixtures/literature_sample.json`. (These are stripped-down but realistic — only fields the parser needs.)

```json
[
  {
    "id": "2761091",
    "metadata": {
      "titles": [{"title": "Branching fractions of $B^-\\to D^- X_{0,1}(2900)$ and their implications"}],
      "authors": [
        {"full_name": "Chen, Yan-Ke", "ids": [{"schema": "INSPIRE BAI", "value": "Yan.Ke.Chen.1"}]},
        {"full_name": "Han, Jia-Jian"},
        {"full_name": "Lu, Qi-Fang"},
        {"full_name": "Wang, Jin-Peng"},
        {"full_name": "Yu, Fu-Sheng"}
      ],
      "arxiv_eprints": [{"value": "2009.01182", "categories": ["hep-ph"]}],
      "publication_info": [
        {"journal_title": "Eur. Phys. J. C", "journal_volume": "81", "page_start": "71", "year": 2021}
      ],
      "dois": [{"value": "10.1140/epjc/s10052-021-08857-8"}],
      "citation_count": 21,
      "first_author": {"full_name": "Chen, Yan-Ke"}
    }
  },
  {
    "id": "2680001",
    "metadata": {
      "titles": [{"title": "Tetraquark bound states in constituent quark models: Benchmark test calculations"}],
      "authors": [
        {"full_name": "Meng, Lu"},
        {"full_name": "Chen, Yan-Ke", "ids": [{"schema": "INSPIRE BAI", "value": "Yan.Ke.Chen.1"}]},
        {"full_name": "Ma, Yao"},
        {"full_name": "Zhu, Shi-Lin"}
      ],
      "arxiv_eprints": [{"value": "2310.13354", "categories": ["hep-ph", "hep-lat"]}],
      "publication_info": [
        {"journal_title": "Phys. Rev. D", "journal_volume": "108", "page_start": "114016", "year": 2023}
      ],
      "dois": [{"value": "10.1103/PhysRevD.108.114016"}],
      "citation_count": 47
    }
  }
]
```

- [ ] **Step 2: Write the failing tests**

```python
# scripts/tests/test_parsers.py
import json
from pathlib import Path
from scripts.parsers import parse_paper, YK_BAI

FIXTURES = json.loads((Path(__file__).parent / 'fixtures' / 'literature_sample.json').read_text())


def test_parse_yk_first_author():
    p = parse_paper(FIXTURES[0])
    assert p.arxiv_id == '2009.01182'
    assert p.inspire_id == '2761091'
    assert p.title.startswith('Branching fractions of $B^-')
    assert p.year == 2021
    assert p.author_position == 'first'
    assert p.is_yk_first
    assert p.journal_ref.name == 'Eur. Phys. J. C'
    assert p.doi.startswith('10.1140')
    assert p.citation_count == 21
    yk = [a for a in p.authors if a.is_yk]
    assert len(yk) == 1 and yk[0].name == 'Chen, Yan-Ke'


def test_parse_yk_middle_author():
    p = parse_paper(FIXTURES[1])
    assert p.author_position == 'middle'
    assert not p.is_yk_first


def test_yk_bai_constant_matches_inspire():
    assert YK_BAI == 'Yan.Ke.Chen.1'
```

- [ ] **Step 3: Run tests — expect ImportError**

```bash
cd scripts && pytest tests/test_parsers.py -v
```

- [ ] **Step 4: Write `scripts/parsers.py`**

```python
"""Translate raw INSPIRE literature JSON records into Paper instances."""
from __future__ import annotations

from typing import Any, Optional

from scripts.models import Author, JournalRef, Paper, AuthorPosition

YK_BAI = 'Yan.Ke.Chen.1'   # YK's INSPIRE BAI identifier — primary lookup key
YK_NAME_HINTS = ('Chen, Yan-Ke', 'Y. K. Chen', 'Yan-Ke Chen')


def _is_yk(raw_author: dict[str, Any]) -> bool:
    for ident in raw_author.get('ids') or []:
        if ident.get('schema') == 'INSPIRE BAI' and ident.get('value') == YK_BAI:
            return True
    return raw_author.get('full_name', '') in YK_NAME_HINTS


def parse_paper(raw: dict[str, Any]) -> Paper:
    meta = raw.get('metadata', {})
    arxiv = (meta.get('arxiv_eprints') or [{}])[0]
    arxiv_id = arxiv.get('value', '')
    categories: list[str] = list(arxiv.get('categories') or [])

    title = (meta.get('titles') or [{}])[0].get('title', '')

    authors_raw = meta.get('authors') or []
    authors: list[Author] = []
    yk_index: Optional[int] = None
    for i, a in enumerate(authors_raw):
        yk = _is_yk(a)
        if yk:
            yk_index = i
        bai = next(
            (x.get('value') for x in (a.get('ids') or []) if x.get('schema') == 'INSPIRE BAI'),
            None,
        )
        authors.append(Author(name=a.get('full_name', ''), is_yk=yk, inspire_id=bai))

    position: AuthorPosition
    if yk_index is None:
        position = 'middle'  # not present; should not happen, but defensive
    elif len(authors) == 1:
        position = 'sole'
    elif yk_index == 0:
        position = 'first'
    elif yk_index == len(authors) - 1:
        position = 'last'
    else:
        position = 'middle'

    pub = (meta.get('publication_info') or [{}])[0]
    year = pub.get('year') or 0
    jref: Optional[JournalRef] = None
    if pub.get('journal_title'):
        jref = JournalRef(
            name=pub.get('journal_title'),
            volume=str(pub.get('journal_volume')) if pub.get('journal_volume') is not None else None,
            page=str(pub.get('page_start')) if pub.get('page_start') is not None else None,
            year=year,
        )

    doi = None
    for d in meta.get('dois') or []:
        if d.get('value'):
            doi = d['value']; break

    return Paper(
        arxiv_id=arxiv_id,
        inspire_id=str(raw.get('id', '')),
        title=title,
        authors=authors,
        year=year,
        journal_ref=jref,
        doi=doi,
        citation_count=int(meta.get('citation_count') or 0),
        arxiv_categories=categories,
        author_position=position,
    )
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd scripts && pytest tests/test_parsers.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/parsers.py scripts/tests/test_parsers.py scripts/tests/fixtures/literature_sample.json
git commit -m "feat(scripts): parse INSPIRE literature records into Paper"
```

---

### Task B4: Derived metrics (pure functions)

**Files:**
- Create: `scripts/derive_metrics.py`
- Create: `scripts/tests/test_derive_metrics.py`

- [ ] **Step 1: Write the failing tests**

```python
# scripts/tests/test_derive_metrics.py
from scripts.models import Author, JournalRef, Paper
from scripts.derive_metrics import (
    derive_metrics, papers_per_year, h_index_curve,
    coauthor_graph, top_cited,
)


def _make_paper(year: int, position='first', cites=10, journal='Phys. Rev. D',
                arxiv='0000.00000', inspire_id='1', authors=None) -> Paper:
    if authors is None:
        authors = [
            Author(name='Y. K. Chen', is_yk=(position != 'last')),
            Author(name='L. Meng', is_yk=False),
        ]
        if position == 'last':
            authors = list(reversed(authors))
            authors[-1] = Author(name='Y. K. Chen', is_yk=True)
    return Paper(
        arxiv_id=arxiv, inspire_id=inspire_id,
        title='T', authors=authors, year=year,
        journal_ref=JournalRef(name=journal, year=year),
        doi=None, citation_count=cites,
        arxiv_categories=['hep-ph'], author_position=position,
    )


def test_papers_per_year_groups_by_position():
    papers = [
        _make_paper(2023, 'first'),
        _make_paper(2023, 'middle'),
        _make_paper(2024, 'first'),
    ]
    out = papers_per_year(papers)
    assert out[2023]['first'] == 1
    assert out[2023]['middle'] == 1
    assert out[2024]['first'] == 1


def test_h_index_curve_monotonic_non_decreasing():
    papers = [
        _make_paper(2021, cites=5, arxiv='a'),
        _make_paper(2022, cites=10, arxiv='b'),
        _make_paper(2023, cites=2, arxiv='c'),
        _make_paper(2024, cites=3, arxiv='d'),
    ]
    curve = h_index_curve(papers)
    years = sorted(curve.keys())
    for a, b in zip(years, years[1:]):
        assert curve[b] >= curve[a]
    assert curve[max(years)] >= 2  # at least the 2 papers with >=2 cites


def test_coauthor_graph_excludes_yk_self_loop():
    p = _make_paper(2024)
    g = coauthor_graph([p])
    names = {n.name for n in g.nodes}
    assert 'L. Meng' in names
    assert 'Y. K. Chen' not in names      # YK is the center, not in graph
    assert all(e.source != e.target for e in g.edges)


def test_top_cited_returns_n_sorted_desc():
    papers = [
        _make_paper(2023, cites=5, arxiv='a', inspire_id='1'),
        _make_paper(2023, cites=15, arxiv='b', inspire_id='2'),
        _make_paper(2023, cites=10, arxiv='c', inspire_id='3'),
    ]
    out = top_cited(papers, n=2)
    assert [p.citation_count for p in out] == [15, 10]


def test_derive_metrics_smoke():
    m = derive_metrics([_make_paper(2024, cites=3), _make_paper(2025, cites=8)])
    assert m.author_position_total['first'] == 2
    assert m.cumulative_citations[2025] == 11
```

- [ ] **Step 2: Run — expect failures**

```bash
cd scripts && pytest tests/test_derive_metrics.py -v
```

- [ ] **Step 3: Write `scripts/derive_metrics.py`**

```python
"""Pure functions that turn a list[Paper] into DerivedMetrics."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from scripts.models import (
    CoauthorEdge, CoauthorGraph, CoauthorNode,
    DerivedMetrics, Paper, PaperRef, TreemapNode,
)


# -------- per-chart helpers --------------------------------------------------

def papers_per_year(papers: Iterable[Paper]) -> dict[int, dict[str, int]]:
    out: dict[int, dict[str, int]] = defaultdict(lambda: {'first': 0, 'middle': 0, 'last': 0, 'sole': 0})
    for p in papers:
        out[p.year][p.author_position] += 1
    return dict(out)


def author_position_total(papers: Iterable[Paper]) -> dict[str, int]:
    out = {'first': 0, 'middle': 0, 'last': 0, 'sole': 0}
    for p in papers:
        out[p.author_position] += 1
    return out


def cumulative_citations(papers: Iterable[Paper]) -> dict[int, int]:
    """Cumulative citation total at end of each year up to the present.

    Approximation: citations are attributed to the paper's publication year.
    INSPIRE does not expose per-year citation history publicly.
    """
    per_year: dict[int, int] = defaultdict(int)
    for p in papers:
        per_year[p.year] += p.citation_count
    cumulative: dict[int, int] = {}
    running = 0
    for y in sorted(per_year):
        running += per_year[y]
        cumulative[y] = running
    return cumulative


def citations_per_year(papers: Iterable[Paper]) -> dict[int, int]:
    per_year: dict[int, int] = defaultdict(int)
    for p in papers:
        per_year[p.year] += p.citation_count
    return dict(per_year)


def h_index_curve(papers: Iterable[Paper]) -> dict[int, int]:
    """h-index calculated at end of each year, given citations accrued by 'now'."""
    plist = sorted(papers, key=lambda p: p.year)
    if not plist:
        return {}
    out: dict[int, int] = {}
    last_year = plist[-1].year
    first_year = plist[0].year
    for y in range(first_year, last_year + 1):
        through_year = [p.citation_count for p in plist if p.year <= y]
        through_year.sort(reverse=True)
        h = 0
        for i, c in enumerate(through_year, start=1):
            if c >= i:
                h = i
            else:
                break
        out[y] = h
    return out


def top_cited(papers: Iterable[Paper], n: int = 8) -> list[PaperRef]:
    sorted_p = sorted(papers, key=lambda p: -p.citation_count)[:n]
    return [
        PaperRef(arxiv_id=p.arxiv_id, inspire_id=p.inspire_id,
                 title=p.title, citation_count=p.citation_count)
        for p in sorted_p
    ]


def journal_split(papers: Iterable[Paper]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for p in papers:
        key = p.journal_ref.name if p.journal_ref else 'arXiv only'
        out[key] += 1
    return dict(out)


def coauthor_graph(papers: Iterable[Paper]) -> CoauthorGraph:
    plist = list(papers)
    # Count YK-co-author pair frequency, and pair-pair frequency among non-YK
    yk_pairs: dict[str, int] = defaultdict(int)
    cross_pairs: dict[tuple[str, str], int] = defaultdict(int)
    bai: dict[str, str] = {}
    for p in plist:
        non_yk = [a for a in p.authors if not a.is_yk]
        for a in non_yk:
            yk_pairs[a.name] += 1
            if a.inspire_id:
                bai[a.name] = a.inspire_id
        for i, a in enumerate(non_yk):
            for b in non_yk[i + 1:]:
                key = tuple(sorted((a.name, b.name)))
                cross_pairs[key] += 1
    nodes = [
        CoauthorNode(name=name, papers_with_yk=count, inspire_id=bai.get(name))
        for name, count in sorted(yk_pairs.items(), key=lambda kv: -kv[1])
    ]
    edges = [CoauthorEdge(source=a, target=b, weight=w) for (a, b), w in cross_pairs.items()]
    return CoauthorGraph(nodes=nodes, edges=edges)


def treemap(papers: Iterable[Paper]) -> TreemapNode:
    """Group by theme_slug → arxiv category → individual paper."""
    grouped: dict[str, dict[str, list[Paper]]] = defaultdict(lambda: defaultdict(list))
    for p in papers:
        theme = p.theme_slug or 'untagged'
        cat = (p.arxiv_categories or ['hep-ph'])[0]
        grouped[theme][cat].append(p)
    root = TreemapNode(name='root', children=[
        TreemapNode(name=theme, children=[
            TreemapNode(name=cat, children=[
                TreemapNode(name=p.title[:48], value=1) for p in paps
            ]) for cat, paps in cats.items()
        ]) for theme, cats in grouped.items()
    ])
    return root


# -------- top-level ---------------------------------------------------------

def derive_metrics(papers: list[Paper]) -> DerivedMetrics:
    cum = cumulative_citations(papers)
    return DerivedMetrics(
        papers_per_year=papers_per_year(papers),
        citations_per_year=citations_per_year(papers),
        citations_per_year_method='approximate',
        cumulative_citations=cum,
        h_index_curve=h_index_curve(papers),
        author_position_total=author_position_total(papers),
        top_cited=top_cited(papers, n=8),
        journal_split=journal_split(papers),
        coauthor_graph=coauthor_graph(papers),
        treemap=treemap(papers),
    )
```

- [ ] **Step 4: Run tests — expect pass**

```bash
cd scripts && pytest tests/test_derive_metrics.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/derive_metrics.py scripts/tests/test_derive_metrics.py
git commit -m "feat(scripts): derive_metrics — pure functions producing DerivedMetrics"
```

---

### Task B5: `fetch_inspire.py` CLI + first real `inspire.json`

**Files:**
- Create: `scripts/fetch_inspire.py`
- Create: `site/src/data/themes.yaml`
- Create: `site/src/data/inspire.json`  (machine-written; committed)

- [ ] **Step 1: Write `scripts/fetch_inspire.py`**

```python
"""CLI entry point: fetch INSPIRE → derive metrics → write inspire.json."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from scripts.derive_metrics import derive_metrics
from scripts.inspire_client import InspireClient, InspireError
from scripts.models import InspireBundle
from scripts.parsers import parse_paper

OUT_PATH = Path(__file__).resolve().parents[1] / 'site' / 'src' / 'data' / 'inspire.json'
THEMES_PATH = Path(__file__).resolve().parents[1] / 'site' / 'src' / 'data' / 'themes.yaml'
DEFAULT_RECID = '2182746'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Refresh INSPIRE data for the homepage.')
    ap.add_argument('--recid', default=DEFAULT_RECID, help='INSPIRE author recid')
    ap.add_argument('--no-cache', action='store_true', help='Bypass disk cache')
    args = ap.parse_args(argv)

    client = InspireClient(cache_dir=None if args.no_cache else Path('scripts/.cache/inspire'))

    try:
        author = client.fetch_author(args.recid)
        raw_works = client.fetch_author_works(args.recid)
    except InspireError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

    papers = [parse_paper(r) for r in raw_works]

    themes: dict[str, list[str]] = {}
    if THEMES_PATH.is_file():
        themes = yaml.safe_load(THEMES_PATH.read_text()) or {}
        slug_for: dict[str, str] = {}
        for slug, ids in themes.items():
            for arxiv_id in ids:
                slug_for[arxiv_id] = slug
        for p in papers:
            p.theme_slug = slug_for.get(p.arxiv_id)

    metrics = derive_metrics(papers)
    bundle = InspireBundle(
        fetched_at=datetime.now(timezone.utc),
        author=author,
        papers=papers,
        metrics=metrics,
        themes=themes,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(bundle.model_dump_json(indent=2))

    print(f'Wrote {OUT_PATH} — {len(papers)} papers, '
          f'{sum(p.citation_count for p in papers)} citations.')
    if metrics.top_cited:
        print('Top cited:')
        for i, p in enumerate(metrics.top_cited[:5], 1):
            print(f'  {i}. ({p.citation_count}) {p.title[:70]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

- [ ] **Step 2: Write a starter `site/src/data/themes.yaml`**

```yaml
# Curated arxiv-id → theme mapping. Update as new papers come out.
em_chiPT:
  - "2412.02297"
  - "2506.18800"
  - "2602.05502"
exotic_interactions:
  - "2308.12424"
  - "2602.12010"
  # X(3872) pole origin
  - "2308.12424"
production:
  - "2009.01182"
  - "2302.01696"
spectrum_quark_models:
  - "2310.14597"
  - "2508.11161"
  - "2401.14899"
  - "2310.13354"
  - "2409.03373"
  - "2406.17824"
  - "2309.17068"
  - "2211.09021"
  - "2408.00503"
```

- [ ] **Step 3: Real fetch (manual; needs network)**

```bash
mkdir -p site/src/data
source scripts/.venv/bin/activate
python -m scripts.fetch_inspire
```

Expected: prints `Wrote .../inspire.json — N papers, M citations.` with N ≈ 18.

- [ ] **Step 4: Sanity-check the output**

```bash
python -c "import json,pathlib; d=json.loads(pathlib.Path('site/src/data/inspire.json').read_text()); print(d['author']['name'], len(d['papers']))"
```

Expected: `Yan-Ke Chen 18` (or similar).

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_inspire.py site/src/data/themes.yaml site/src/data/inspire.json
git commit -m "feat(scripts): fetch_inspire.py CLI + first real inspire.json"
```

---

### Task B6: Replace the fixture stub with the real captured author payload

**Files:**
- Modify: `scripts/tests/fixtures/author_2182746.json`

- [ ] **Step 1: Capture the live author payload to the fixture**

```bash
mkdir -p scripts/tests/fixtures
python -c "
from pathlib import Path
import json, scripts.inspire_client as c
client = c.InspireClient(cache_dir=None)
data = client._get_json('/authors/2182746')
Path('scripts/tests/fixtures/author_2182746.json').write_text(json.dumps(data, indent=2))
print('captured', len(json.dumps(data)), 'bytes')
"
```

- [ ] **Step 2: Re-run client tests**

```bash
cd scripts && pytest tests/test_inspire_client.py -v
```

Expected: all 5 still pass with the real fixture.

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/fixtures/author_2182746.json
git commit -m "test(scripts): replace stub author fixture with real INSPIRE payload"
```

---

## Phase C · Astro shell + shared components

### Task C1: Layout, Nav, Footer

**Files:**
- Create: `site/src/layouts/Base.astro`
- Create: `site/src/components/Nav.astro`
- Create: `site/src/components/Footer.astro`
- Create: `site/src/lib/data.ts`

- [ ] **Step 1: Write `site/src/lib/data.ts`**

```typescript
import bundleJson from '../data/inspire.json';

export interface Paper {
  arxiv_id: string;
  inspire_id: string;
  title: string;
  authors: { name: string; is_yk: boolean; inspire_id: string | null }[];
  year: number;
  journal_ref: { name: string; volume: string | null; page: string | null; year: number } | null;
  doi: string | null;
  citation_count: number;
  arxiv_categories: string[];
  author_position: 'first' | 'middle' | 'last' | 'sole';
  theme_slug: string | null;
}

export interface InspireBundle {
  fetched_at: string;
  author: { recid: string; name: string; current_affiliation: string | null; orcid: string | null };
  papers: Paper[];
  metrics: {
    papers_per_year: Record<string, Record<string, number>>;
    citations_per_year: Record<string, number>;
    citations_per_year_method: 'exact' | 'approximate';
    cumulative_citations: Record<string, number>;
    h_index_curve: Record<string, number>;
    author_position_total: Record<string, number>;
    top_cited: { arxiv_id: string; inspire_id: string; title: string; citation_count: number }[];
    journal_split: Record<string, number>;
    coauthor_graph: { nodes: { name: string; papers_with_yk: number; inspire_id: string | null }[]; edges: { source: string; target: string; weight: number }[] };
    treemap: { name: string; value: number | null; children: any[] | null };
  };
  themes: Record<string, string[]>;
}

export const bundle = bundleJson as unknown as InspireBundle;

export const fetchedAt = new Date(bundle.fetched_at);

export const refreshedLabel = fetchedAt.toLocaleDateString('en-US', {
  year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC',
});
```

- [ ] **Step 2: Write `site/src/components/Nav.astro`**

```astro
---
const path = Astro.url.pathname.replace(/\/$/, '');
const links = [
  { href: '/research', label: 'Research' },
  { href: '/publications', label: 'Publications' },
  { href: '/talks', label: 'Talks' },
  { href: '/analytics', label: 'Analytics' },
  { href: '/cv', label: 'CV' },
];
---
<nav aria-label="primary" class="flex items-baseline justify-between border-b border-rule pb-4">
  <a href="/" class="text-[15px] font-semibold tracking-tight text-ink hover:text-accent">
    Yan-Ke Chen <span class="font-normal text-ink-3 text-[13px] ml-1">陈彦珂</span>
  </a>
  <ul class="flex gap-6 text-[12px] font-medium tracking-[0.08em] uppercase font-mono text-ink-2">
    {links.map((l) => (
      <li>
        <a href={l.href}
           class:list={["hover:text-accent transition-colors", path === l.href && "text-accent"]}
        >{l.label}</a>
      </li>
    ))}
  </ul>
</nav>
```

- [ ] **Step 3: Write `site/src/components/Footer.astro`**

```astro
---
import { refreshedLabel } from '../lib/data';
const orcid = ''; // TBD
const scholar = ''; // TBD
const github = ''; // TBD
---
<footer class="mt-16 pt-6 border-t border-rule text-[12px] font-mono text-ink-3 flex flex-wrap gap-x-6 gap-y-2 justify-between">
  <div>
    Data from <a class="text-accent hover:text-ink underline-offset-2" href="https://inspirehep.net/authors/2182746">INSPIRE-HEP</a>
    · refreshed {refreshedLabel}
  </div>
  <div class="flex gap-4">
    <a href="https://inspirehep.net/authors/2182746">INSPIRE</a>
    {orcid && <a href={`https://orcid.org/${orcid}`}>ORCID</a>}
    {scholar && <a href={scholar}>Scholar</a>}
    {github && <a href={`https://github.com/${github}`}>GitHub</a>}
    <a href="mailto:chenyanke@pku.edu.cn">Email</a>
  </div>
  <div>© {new Date().getFullYear()} Yan-Ke Chen</div>
</footer>
```

- [ ] **Step 4: Write `site/src/layouts/Base.astro`**

```astro
---
import '../styles/global.css';
import Nav from '../components/Nav.astro';
import Footer from '../components/Footer.astro';

interface Props {
  title: string;
  description?: string;
}
const { title, description = 'Personal academic homepage of Yan-Ke Chen' } = Astro.props;
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content={description} />
  <title>{title}</title>
  <link rel="icon" type="image/png" href="/photo.png" />
</head>
<body class="relative">
  <div class="relative z-10 max-w-[1180px] mx-auto px-[clamp(1.75rem,5vw,3.5rem)] py-10">
    <Nav />
    <main class="mt-2"><slot /></main>
    <Footer />
  </div>
</body>
</html>
```

- [ ] **Step 5: Build to verify wiring**

```bash
cd site && npm run build
```

Expected: builds without error. (No pages yet — Astro will warn about no routes; we'll fix that in Task C2/D1.)

- [ ] **Step 6: Commit**

```bash
git add site/src/layouts/Base.astro site/src/components/Nav.astro site/src/components/Footer.astro site/src/lib/data.ts
git commit -m "feat(site): Base layout with Nav and Footer; data import helper"
```

---

### Task C2: `<Math>` component + title-with-inline-math helper

**Files:**
- Create: `site/src/components/Math.astro`
- Create: `site/src/lib/math.ts`

- [ ] **Step 1: Write `site/src/components/Math.astro`**

```astro
---
import katex from 'katex';
interface Props { tex: string; displayMode?: boolean }
const { tex, displayMode = false } = Astro.props;
let html: string;
try {
  html = katex.renderToString(tex, {
    displayMode,
    throwOnError: false,
    output: 'html',
    strict: 'ignore',
  });
} catch (e) {
  console.warn('KaTeX render failed:', tex, e);
  html = `<span>${tex}</span>`;
}
---
<span class="katex-host" set:html={html}></span>
```

- [ ] **Step 2: Write `site/src/lib/math.ts`**

```typescript
import katex from 'katex';

/**
 * Render a string that may contain $...$ (inline math) segments to HTML.
 * Unbalanced dollars are treated as literal characters.
 */
export function renderInlineMath(input: string): string {
  if (!input.includes('$')) return escapeHtml(input);
  const parts: string[] = [];
  let i = 0;
  while (i < input.length) {
    const dollar = input.indexOf('$', i);
    if (dollar === -1) { parts.push(escapeHtml(input.slice(i))); break; }
    if (dollar > i) parts.push(escapeHtml(input.slice(i, dollar)));
    const end = input.indexOf('$', dollar + 1);
    if (end === -1) { parts.push(escapeHtml(input.slice(dollar))); break; }
    const tex = input.slice(dollar + 1, end);
    try {
      parts.push(katex.renderToString(tex, { throwOnError: false, output: 'html', strict: 'ignore' }));
    } catch {
      parts.push(escapeHtml(`$${tex}$`));
    }
    i = end + 1;
  }
  return parts.join('');
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
```

- [ ] **Step 3: Commit**

```bash
git add site/src/components/Math.astro site/src/lib/math.ts
git commit -m "feat(site): Math component and renderInlineMath helper (KaTeX SSR)"
```

---

### Task C3: PaperRow + ThemeCard components

**Files:**
- Create: `site/src/components/PaperRow.astro`
- Create: `site/src/components/ThemeCard.astro`

- [ ] **Step 1: Write `site/src/components/PaperRow.astro`**

```astro
---
import type { Paper } from '../lib/data';
import { renderInlineMath } from '../lib/math';

interface Props { paper: Paper }
const { paper } = Astro.props;

const authorList = paper.authors
  .map((a) => a.is_yk
    ? `<strong class="text-accent">${a.name}</strong>`
    : a.name)
  .join(', ');

const venueLine = paper.journal_ref
  ? `${paper.journal_ref.name} ${paper.journal_ref.volume ?? ''}${paper.journal_ref.page ? ', ' + paper.journal_ref.page : ''}`
  : 'arXiv preprint';
---
<article class="grid grid-cols-[64px_1fr_120px] gap-5 py-4 border-b border-rule-2 items-baseline">
  <div class="font-mono text-[11px] text-ink-3 tracking-wider">{paper.year}</div>
  <div>
    <div class="text-[15px] text-ink leading-snug" set:html={renderInlineMath(paper.title)}></div>
    <div class="text-[12px] text-ink-2 italic mt-1" set:html={authorList}></div>
    <div class="text-[11px] font-mono text-ink-3 mt-1 flex gap-3 flex-wrap">
      {paper.doi && <a class="hover:text-accent" href={`https://doi.org/${paper.doi}`}>doi:{paper.doi}</a>}
      {paper.arxiv_id && <a class="hover:text-accent" href={`https://arxiv.org/abs/${paper.arxiv_id}`}>arXiv:{paper.arxiv_id}</a>}
      <a class="hover:text-accent" href={`https://inspirehep.net/literature/${paper.inspire_id}`}>INSPIRE</a>
    </div>
  </div>
  <div class="text-right">
    <div class="font-mono text-[11px] text-accent">{venueLine}</div>
    <div class="font-mono text-[10px] text-ink-3 mt-1">{paper.citation_count} cites</div>
  </div>
</article>
```

- [ ] **Step 2: Write `site/src/components/ThemeCard.astro`**

```astro
---
import { renderInlineMath } from '../lib/math';

interface Props {
  title: string;
  bodyTex: string;     // may include $...$
  href: string;
}
const { title, bodyTex, href } = Astro.props;
---
<a href={href} class="block p-5 bg-paper border border-rule hover:bg-paper-2 transition-colors">
  <div class="text-[14px] font-medium text-ink mb-2">{title}</div>
  <p class="text-[13px] text-ink-2 leading-relaxed" set:html={renderInlineMath(bodyTex)}></p>
  <div class="mt-3 text-[11px] font-mono text-accent">→ Read more</div>
</a>
```

- [ ] **Step 3: Commit**

```bash
git add site/src/components/PaperRow.astro site/src/components/ThemeCard.astro
git commit -m "feat(site): PaperRow + ThemeCard components"
```

---

## Phase D · Static pages

### Task D1: Home page

**Files:**
- Create: `site/src/pages/index.astro`

- [ ] **Step 1: Write `site/src/pages/index.astro`**

```astro
---
import Base from '../layouts/Base.astro';
import { bundle } from '../lib/data';
import PaperRow from '../components/PaperRow.astro';
import ThemeCard from '../components/ThemeCard.astro';
import { renderInlineMath } from '../lib/math';

// Pick 5 highlight papers: 3 newest first-author + 2 most-cited first-author
const firstAuthorPapers = bundle.papers.filter((p) => p.author_position === 'first' || p.author_position === 'sole');
const newest = [...firstAuthorPapers].sort((a, b) => b.year - a.year).slice(0, 3);
const mostCited = [...firstAuthorPapers]
  .sort((a, b) => b.citation_count - a.citation_count)
  .filter((p) => !newest.includes(p))
  .slice(0, 2);
const highlights = [...newest, ...mostCited].sort((a, b) => b.year - a.year);

const totals = {
  papers: bundle.papers.length,
  citations: bundle.papers.reduce((s, p) => s + p.citation_count, 0),
  hIndex: Math.max(...Object.values(bundle.metrics.h_index_curve), 0),
  coauthors: bundle.metrics.coauthor_graph.nodes.length,
};

const latest = [...bundle.papers].sort((a, b) => b.year - a.year)[0];
---
<Base title="Yan-Ke Chen — academic homepage">

  <!-- § I · CURRENTLY -->
  <section class="pt-10 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§ I</span>CURRENTLY
    </div>
    <div>
      <div class="grid grid-cols-[1fr_0.42fr] gap-10 items-start">
        <div>
          <h1 class="text-[clamp(40px,5.4vw,60px)] font-semibold tracking-tightest leading-[1.02] text-ink mb-3.5">
            Yan-Ke Chen
          </h1>
          <p class="text-[17px] leading-relaxed text-ink-2 max-w-[48ch]">
            <span class="inline-block w-1.5 h-1.5 bg-mark rounded-full mr-1 align-middle pulse-dot"></span>
            Postdoctoral researcher at the <em class="not-italic font-medium text-mark">Center for High Energy Physics, Peking University</em>.
            I study hadron spectroscopy, exotic states, low-energy hadron interactions,
            and electromagnetic properties of hadrons via χPT and quark potential models.
          </p>
        </div>
        <div>
          <img src="/photo.png" alt="" class="w-full aspect-square object-cover rounded-sm" />
          <div class="font-mono text-[10px] uppercase tracking-wider text-ink-3 mt-2 flex justify-between">
            <span>CHEP · PKU</span><span>Jul 2025 →</span>
          </div>
        </div>
      </div>

      <!-- BY THE NUMBERS -->
      <div class="mt-7 grid grid-cols-4 border-t border-ink border-b border-rule">
        {[
          { v: totals.papers, l: 'Papers' },
          { v: totals.citations, l: 'Citations' },
          { v: totals.hIndex, l: 'h-index' },
          { v: totals.coauthors, l: 'Co-authors' },
        ].map((s, i) => (
          <div class:list={["py-3.5 px-4 pr-4", i < 3 && "border-r border-rule"]}>
            <b class="block text-[32px] font-medium tracking-tight text-ink tabular-nums">{s.v}</b>
            <span class="block font-mono text-[10px] tracking-widest text-ink-3 uppercase mt-0.5">{s.l}</span>
          </div>
        ))}
      </div>

      {latest && (
        <div class="mt-6 pt-3 border-t border-dashed border-rule font-mono text-[11px] text-ink-2">
          <strong class="text-mark">arXiv:{latest.arxiv_id}</strong>
          — <span class="italic" set:html={renderInlineMath(latest.title)}></span>
          · <i>{latest.year}</i>
        </div>
      )}
    </div>
  </section>

  <!-- § II · SELECTED PAPERS -->
  <section class="pt-12 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§ II</span>SELECTED
    </div>
    <div>
      <h2 class="text-[24px] font-medium tracking-tight mb-3">Recent work <em class="not-italic text-ink-3 font-normal ml-1">— five selected</em></h2>
      <div>
        {highlights.map((p) => <PaperRow paper={p} />)}
      </div>
    </div>
  </section>

  <!-- § III · THEMES -->
  <section class="pt-12 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§ III</span>THEMES
    </div>
    <div>
      <h2 class="text-[24px] font-medium tracking-tight mb-3">Research themes</h2>
      <div class="grid grid-cols-2 gap-px bg-rule border border-rule">
        <ThemeCard
          title="Spectrum from quark models"
          bodyTex="Tetraquark bound states and resonances using constituent quark models, complex scaling, and diffusion Monte Carlo — including fully heavy $QQ\bar{Q}\bar{Q}$ states."
          href="/research#spectrum"
        />
        <ThemeCard
          title="Hadron-hadron interaction"
          bodyTex="Coupled-channel dynamics for the $X(3872)$ pole structure, virtual states, and three-body molecular states like $DD^*\bar{K}^*$."
          href="/research#interaction"
        />
        <ThemeCard
          title="Electromagnetic properties"
          bodyTex="HBχPT calculations of polarizabilities for spin-$\tfrac{1}{2}$ and spin-$\tfrac{3}{2}$ singly heavy baryons and heavy triplet hadrons."
          href="/research#em"
        />
        <ThemeCard
          title="Production of exotic states"
          bodyTex="Branching fractions in $B^-\to D^- X_{0,1}(2900)$ and hidden-charm strange molecular states in $B$ and $B_s$ decays."
          href="/research#production"
        />
      </div>
    </div>
  </section>

</Base>

<style>
  .pulse-dot {
    box-shadow: 0 0 0 0 rgba(176, 73, 42, 0.6);
    animation: pulse 2.4s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(176,73,42,.6); }
    70% { box-shadow: 0 0 0 8px rgba(176,73,42,0); }
    100% { box-shadow: 0 0 0 0 rgba(176,73,42,0); }
  }
  @media (prefers-reduced-motion: reduce) {
    .pulse-dot { animation: none; }
  }
</style>
```

- [ ] **Step 2: Build + manually verify**

```bash
cd site && npm run build && npm run preview
```

Open the preview URL (default `http://localhost:4321`). Verify:
- Hero, photo, numbers strip render
- The arXiv ticker shows the latest paper title with KaTeX-rendered math
- 5 selected papers render with proper math in titles
- 4 theme cards show with their KaTeX bits

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/index.astro
git commit -m "feat(site): home page (hero, by-the-numbers, 5 selected, 4 themes)"
```

---

### Task D2: Research page

**Files:**
- Create: `site/src/pages/research.astro`
- Modify: `site/src/data/themes.yaml` (no change to data; only the page reads it)

- [ ] **Step 1: Write `site/src/pages/research.astro`**

```astro
---
import Base from '../layouts/Base.astro';
import { bundle } from '../lib/data';
import PaperRow from '../components/PaperRow.astro';
import { renderInlineMath } from '../lib/math';

interface Theme {
  slug: string;
  marker: string;
  title: string;
  introTex: string;
}

const themes: Theme[] = [
  { slug: 'spectrum', marker: '§ I',  title: 'Spectrum from quark models',
    introTex: 'TBD — write a 2-3 paragraph intro covering benchmark tetraquark calculations, the complex-scaling method, and the diffusion-Monte-Carlo work on $QQ\\bar{Q}\\bar{Q}$ states.' },
  { slug: 'interaction', marker: '§ II', title: 'Hadron-hadron interaction',
    introTex: 'TBD — write an intro on the coupled-channel work around the $X(3872)$ pole, virtual states, and the recent $DD^*\\bar{K}^*$ three-body molecular state prediction.' },
  { slug: 'em', marker: '§ III', title: 'Electromagnetic properties',
    introTex: 'TBD — describe the HBχPT polarizability program for spin-$\\tfrac{1}{2}$ and spin-$\\tfrac{3}{2}$ singly heavy baryons and heavy triplet hadrons.' },
  { slug: 'production', marker: '§ IV', title: 'Production of exotic states',
    introTex: 'TBD — describe the $B$- and $B_s$-decay branching-fraction work, including $B^-\\to D^- X_{0,1}(2900)$ and hidden-charm strange molecular candidates.' },
];

const themePapers: Record<string, typeof bundle.papers> = {};
for (const slug of Object.keys(bundle.themes)) {
  const ids = new Set(bundle.themes[slug]);
  themePapers[slug] = bundle.papers
    .filter((p) => ids.has(p.arxiv_id))
    .sort((a, b) => b.year - a.year);
}
---
<Base title="Research — Yan-Ke Chen">

  {themes.map((t) => (
    <section id={t.slug} class="pt-12 grid grid-cols-[90px_1fr] gap-6">
      <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
        <span class="block text-[11px] text-mark mb-1">{t.marker}</span>{t.title.split(' ')[0].toUpperCase()}
      </div>
      <div>
        <h2 class="text-[28px] font-medium tracking-tight text-ink mb-3">{t.title}</h2>
        <p class="text-[15px] text-ink-2 leading-relaxed max-w-[68ch]" set:html={renderInlineMath(t.introTex)}></p>
        <div class="mt-6">
          {(themePapers[t.slug.replace('em', 'em_chiPT').replace('interaction', 'exotic_interactions').replace('spectrum', 'spectrum_quark_models')] ?? [])
            .map((p) => <PaperRow paper={p} />)}
        </div>
      </div>
    </section>
  ))}

</Base>
```

> **Note:** The slug mapping in the `.map` call ties the page-section slug to the themes.yaml key. Keep them aligned — if you rename a slug in themes.yaml, update this file too. (A future cleanup could store the page-slug directly in themes.yaml.)

- [ ] **Step 2: Build + preview**

```bash
cd site && npm run build && npm run preview
```

Visit `/research`. Verify each of the four sections renders with its papers (KaTeX math present).

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/research.astro
git commit -m "feat(site): /research with four theme sections and per-theme papers"
```

---

### Task D3: Publications page (with client filter)

**Files:**
- Create: `site/src/pages/publications.astro`

- [ ] **Step 1: Write `site/src/pages/publications.astro`**

```astro
---
import Base from '../layouts/Base.astro';
import { bundle } from '../lib/data';
import PaperRow from '../components/PaperRow.astro';

const papers = [...bundle.papers].sort((a, b) => b.year - a.year);
const years = [...new Set(papers.map((p) => p.year))].sort((a, b) => b - a);
const journals = [...new Set(papers.map((p) => p.journal_ref?.name ?? 'arXiv only'))];
const themes = Object.keys(bundle.themes);
---
<Base title="Publications — Yan-Ke Chen">

  <section class="pt-10 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§</span>ALL
    </div>
    <div>
      <h1 class="text-[36px] font-semibold tracking-tightest text-ink mb-2">Publications</h1>
      <p class="text-[14px] text-ink-2 mb-6">{papers.length} papers · {papers.reduce((s,p)=>s+p.citation_count,0)} citations.</p>

      <!-- filter chips -->
      <div class="mb-6 flex flex-wrap gap-2 text-[11px] font-mono uppercase">
        <button class="filter-chip" data-filter-group="year"   data-filter-value="all"   data-active="true">All years</button>
        {years.map((y) => <button class="filter-chip" data-filter-group="year" data-filter-value={y}>{y}</button>)}
        <span class="mx-2 text-ink-3">·</span>
        <button class="filter-chip" data-filter-group="theme" data-filter-value="all" data-active="true">All themes</button>
        {themes.map((t) => <button class="filter-chip" data-filter-group="theme" data-filter-value={t}>{t.replace(/_/g,' ')}</button>)}
        <span class="mx-2 text-ink-3">·</span>
        <button class="filter-chip" data-filter-group="position" data-filter-value="all"   data-active="true">Any position</button>
        <button class="filter-chip" data-filter-group="position" data-filter-value="first">First author</button>
        <button class="filter-chip" data-filter-group="position" data-filter-value="middle">Middle</button>
        <button class="filter-chip" data-filter-group="position" data-filter-value="last">Last</button>
      </div>

      <div id="paper-list">
        {papers.map((p) => (
          <div class="paper-row"
               data-year={p.year}
               data-theme={p.theme_slug ?? 'untagged'}
               data-position={p.author_position}>
            <PaperRow paper={p} />
          </div>
        ))}
      </div>
    </div>
  </section>

</Base>

<style>
  .filter-chip {
    padding: 4px 10px; border: 1px solid theme('colors.rule'); border-radius: 4px;
    background: theme('colors.paper'); color: theme('colors.ink-2'); cursor: pointer;
    transition: all .15s ease; letter-spacing: 0.06em;
  }
  .filter-chip:hover { background: theme('colors.paper-2'); }
  .filter-chip[data-active="true"] { background: theme('colors.accent'); color: theme('colors.paper'); border-color: theme('colors.accent'); }
</style>

<script>
  const state: Record<string, string> = { year: 'all', theme: 'all', position: 'all' };
  const params = new URLSearchParams(window.location.search);
  for (const k of Object.keys(state)) {
    const v = params.get(k);
    if (v) state[k] = v;
  }
  function syncChips() {
    document.querySelectorAll<HTMLButtonElement>('.filter-chip').forEach((btn) => {
      const grp = btn.dataset.filterGroup!;
      const val = btn.dataset.filterValue!;
      btn.dataset.active = state[grp] === val ? 'true' : 'false';
    });
  }
  function applyFilter() {
    document.querySelectorAll<HTMLElement>('.paper-row').forEach((row) => {
      const okYear = state.year === 'all' || row.dataset.year === state.year;
      const okTheme = state.theme === 'all' || row.dataset.theme === state.theme;
      const okPos = state.position === 'all' || row.dataset.position === state.position;
      row.style.display = (okYear && okTheme && okPos) ? '' : 'none';
    });
    const next = new URLSearchParams();
    for (const [k, v] of Object.entries(state)) if (v !== 'all') next.set(k, v);
    const qs = next.toString();
    history.replaceState(null, '', qs ? '?' + qs : window.location.pathname);
  }
  document.querySelectorAll<HTMLButtonElement>('.filter-chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      const grp = btn.dataset.filterGroup!;
      state[grp] = btn.dataset.filterValue!;
      syncChips();
      applyFilter();
    });
  });
  syncChips();
  applyFilter();
</script>
```

- [ ] **Step 2: Build + preview**

```bash
cd site && npm run build && npm run preview
```

Visit `/publications`. Click a year and a position chip; verify rows hide. Verify URL updates with query params. Reload — filters should persist.

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/publications.astro
git commit -m "feat(site): /publications with year/theme/position filters in URL"
```

---

### Task D4: Talks page

**Files:**
- Create: `site/src/data/talks.yaml`
- Create: `site/src/pages/talks.astro`

- [ ] **Step 1: Write `site/src/data/talks.yaml` (from CV)**

```yaml
oral:
  - event: Frontiers in Multiquark-States Physics
    title: "Theoretical prediction of a $DD^*\\bar{K}^*$ three-body molecular state"
    location: "Beijing, China"
    date: "Jan 2026"
  - event: 9th XYZ Symposium
    title: "$Qs\\bar{n}\\bar{n}$ bound states and resonances in quark potential model"
    location: "Xi'an, China"
    date: "May 2024"
  - event: 7th Symposium on Symmetries and the Emergence of Structure in QCD
    title: "Doubly-heavy tetraquark bound states in quark potential models"
    location: "Rizhao, China"
    date: "Jul 2023"
poster:
  - event: 11th Five-University Alliance Doctoral Academic Forum
    title: "A unified description of the tetraquark states in the quark potential model"
    location: "Hefei, China"
    date: "Dec 2024"
```

- [ ] **Step 2: Write `site/src/pages/talks.astro`**

```astro
---
import Base from '../layouts/Base.astro';
import yaml from 'js-yaml';
import { renderInlineMath } from '../lib/math';

const raw = await Astro.glob('../data/talks.yaml');
// Astro.glob doesn't parse YAML; load it via Vite's raw import instead:
import talksFile from '../data/talks.yaml?raw';
const talks = yaml.load(talksFile) as { oral: Talk[]; poster: Talk[] };

interface Talk { event: string; title: string; location: string; date: string }
---
<Base title="Talks — Yan-Ke Chen">

  <section class="pt-10 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§ I</span>ORAL
    </div>
    <div>
      <h2 class="text-[24px] font-medium tracking-tight text-ink mb-3">Oral Presentations</h2>
      <div>
        {talks.oral.map((t) => (
          <article class="grid grid-cols-[1fr_180px] py-4 border-b border-rule-2 gap-4 items-baseline">
            <div>
              <div class="text-[15px] font-medium text-ink">{t.event}</div>
              <div class="italic text-[14px] text-ink-2 mt-1" set:html={renderInlineMath(t.title)}></div>
            </div>
            <div class="text-right font-mono text-[11px] text-ink-3 leading-relaxed">
              {t.location}<br>{t.date}
            </div>
          </article>
        ))}
      </div>
    </div>
  </section>

  <section class="pt-12 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§ II</span>POSTER
    </div>
    <div>
      <h2 class="text-[24px] font-medium tracking-tight text-ink mb-3">Poster Presentations</h2>
      <div>
        {talks.poster.map((t) => (
          <article class="grid grid-cols-[1fr_180px] py-4 border-b border-rule-2 gap-4 items-baseline">
            <div>
              <div class="text-[15px] font-medium text-ink">{t.event}</div>
              <div class="italic text-[14px] text-ink-2 mt-1" set:html={renderInlineMath(t.title)}></div>
            </div>
            <div class="text-right font-mono text-[11px] text-ink-3 leading-relaxed">
              {t.location}<br>{t.date}
            </div>
          </article>
        ))}
      </div>
    </div>
  </section>

</Base>
```

- [ ] **Step 3: Install js-yaml**

```bash
cd site && npm install js-yaml @types/js-yaml && cd ..
```

- [ ] **Step 4: Build + preview**

```bash
cd site && npm run build && npm run preview
```

Visit `/talks`. Verify 3 oral + 1 poster render with KaTeX-rendered titles.

- [ ] **Step 5: Commit**

```bash
git add site/src/data/talks.yaml site/src/pages/talks.astro site/package.json site/package-lock.json
git commit -m "feat(site): /talks page sourced from hand-curated talks.yaml"
```

---

### Task D5: CV page

**Files:**
- Create: `site/src/pages/cv.astro`

- [ ] **Step 1: Write `site/src/pages/cv.astro`**

```astro
---
import Base from '../layouts/Base.astro';
---
<Base title="CV — Yan-Ke Chen">

  <section class="pt-10 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§</span>CV
    </div>
    <div>
      <h1 class="text-[36px] font-semibold tracking-tightest text-ink">Curriculum Vitae</h1>
      <p class="text-[14px] text-ink-2 mt-2">Last updated to match the LaTeX source. PDF is authoritative.</p>

      <a href="/cv/CV_YKChen.pdf"
         class="inline-block mt-5 px-5 py-3 bg-accent text-paper font-mono text-[12px] uppercase tracking-wider hover:bg-ink transition-colors">
        ↓ Download PDF (CV_YKChen.pdf)
      </a>

      <h2 class="mt-10 text-[20px] font-medium tracking-tight">Personal Information</h2>
      <dl class="mt-3 grid grid-cols-[200px_1fr] gap-y-1.5 text-[14px] text-ink-2">
        <dt class="font-mono text-[11px] uppercase text-ink-3">Email</dt><dd><a class="text-accent" href="mailto:chenyanke@pku.edu.cn">chenyanke@pku.edu.cn</a></dd>
        <dt class="font-mono text-[11px] uppercase text-ink-3">Affiliation</dt><dd>Center for High Energy Physics, Peking University</dd>
        <dt class="font-mono text-[11px] uppercase text-ink-3">INSPIRE</dt><dd><a class="text-accent" href="https://inspirehep.net/authors/2182746">2182746</a></dd>
      </dl>

      <h2 class="mt-10 text-[20px] font-medium tracking-tight">Education</h2>
      <ul class="mt-3 space-y-3 text-[14px] text-ink-2">
        <li><strong class="text-ink">Peking University</strong> — PhD in Theoretical Physics · Sep 2020 – Jun 2025. Advisor: Prof. Shi-Lin Zhu.</li>
        <li><strong class="text-ink">Lanzhou University</strong> — BSc in Physics · Sep 2016 – Jul 2020.</li>
      </ul>

      <h2 class="mt-10 text-[20px] font-medium tracking-tight">Professional Experience</h2>
      <ul class="mt-3 space-y-3 text-[14px] text-ink-2">
        <li><strong class="text-ink">CHEP, Peking University</strong> — Postdoctoral Researcher · Jul 2025 – present. Supervisor: Prof. Shi-Lin Zhu.</li>
      </ul>

      <h2 class="mt-10 text-[20px] font-medium tracking-tight">Awards</h2>
      <ul class="mt-3 space-y-2 text-[14px] text-ink-2 list-disc list-inside">
        <li>President Scholarship (2024–2025)</li>
        <li>National Scholarship (2019–2020)</li>
        <li>Merit Student / Merit Student Pacesetter</li>
      </ul>

      <h2 class="mt-10 text-[20px] font-medium tracking-tight">Professional Service</h2>
      <ul class="mt-3 space-y-1 text-[14px] text-ink-2 list-disc list-inside">
        <li>Peer reviewer — Physical Review D</li>
        <li>Peer reviewer — Chinese Physics C</li>
        <li>Peer reviewer — European Physical Journal C</li>
      </ul>

      <h2 class="mt-10 text-[20px] font-medium tracking-tight">Skills</h2>
      <ul class="mt-3 space-y-1 text-[14px] text-ink-2 list-disc list-inside">
        <li>Scientific computing</li>
        <li>Mathematica, C/C++</li>
        <li>Linux</li>
        <li>CUDA GPU programming</li>
      </ul>

      <p class="mt-12 text-[12px] font-mono text-ink-3">
        For the complete list of publications, see <a class="text-accent" href="/publications">/publications</a>.
        For talks, see <a class="text-accent" href="/talks">/talks</a>.
      </p>
    </div>
  </section>

</Base>
```

- [ ] **Step 2: Build + preview**

```bash
cd site && npm run build && npm run preview
```

Visit `/cv`. Click "Download PDF" — should serve `/cv/CV_YKChen.pdf`.

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/cv.astro
git commit -m "feat(site): /cv HTML summary with prominent PDF download"
```

---

## Phase E · Analytics charts

### Task E1: Analytics page shell

**Files:**
- Create: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write the shell with eight chart placeholders**

```astro
---
import Base from '../layouts/Base.astro';
import { bundle, refreshedLabel } from '../lib/data';

// Charts will be imported and inserted in subsequent tasks E2–E9.
---
<Base title="Analytics — Yan-Ke Chen">

  <section class="pt-10 grid grid-cols-[90px_1fr] gap-6">
    <div class="font-mono text-[10px] tracking-[0.14em] uppercase text-ink-3 pt-1">
      <span class="block text-[11px] text-mark mb-1">§</span>ANALYTICS
    </div>
    <div>
      <h1 class="text-[36px] font-semibold tracking-tightest text-ink">Eight views of the work</h1>
      <p class="text-[14px] text-ink-2 mt-2 max-w-[68ch]">
        Data sourced from INSPIRE-HEP author <a class="text-accent" href="https://inspirehep.net/authors/2182746">2182746</a>.
        <span class="font-mono text-ink-3">Refreshed {refreshedLabel}.</span>
        <span class="font-mono text-ink-3">Citations are attributed to publication year ({bundle.metrics.citations_per_year_method}).</span>
      </p>
    </div>
  </section>

  <!-- Charts go here, inserted by tasks E2–E9 -->
  <div id="chart-grid" class="mt-10 space-y-6"></div>

</Base>
```

- [ ] **Step 2: Build to confirm**

```bash
cd site && npm run build
```

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/analytics.astro
git commit -m "feat(site): /analytics shell with intro and refresh timestamp"
```

---

### Task E2: Co-author network (D3 force)

**Files:**
- Create: `site/src/components/analytics/CoauthorNetwork.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `site/src/components/analytics/CoauthorNetwork.astro`**

```astro
---
import { bundle } from '../../lib/data';
const g = bundle.metrics.coauthor_graph;
const data = JSON.stringify({ nodes: g.nodes, edges: g.edges });
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Co-author network</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">{g.nodes.length} co-authors · drag nodes to explore</span>
  </figcaption>
  <div id="coauthor-network" class="w-full h-[480px]" data-graph={data}></div>
</figure>

<script>
  import * as d3 from 'd3';
  const root = document.getElementById('coauthor-network')!;
  const graph = JSON.parse(root.dataset.graph!);
  const width = root.clientWidth, height = root.clientHeight;
  const svg = d3.select(root).append('svg').attr('viewBox', `0 0 ${width} ${height}`).attr('class', 'w-full h-full');

  // YK self-node at center
  const nodes = [{ id: 'YK', name: 'Y. K. Chen', papers_with_yk: graph.nodes.reduce((s: number, n: any) => s + n.papers_with_yk, 0), isYk: true },
                 ...graph.nodes.map((n: any) => ({ id: n.name, name: n.name, papers_with_yk: n.papers_with_yk, isYk: false }))];
  const yk_links = graph.nodes.map((n: any) => ({ source: 'YK', target: n.name, weight: n.papers_with_yk }));
  const cross_links = graph.edges.map((e: any) => ({ source: e.source, target: e.target, weight: e.weight }));
  const links = [...yk_links, ...cross_links];

  const sim = d3.forceSimulation(nodes as any)
    .force('charge', d3.forceManyBody().strength(-80))
    .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(60).strength(0.4))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide().radius((d: any) => Math.sqrt(d.papers_with_yk) * 4 + 6));

  const link = svg.append('g').attr('stroke', '#DCD5C5').selectAll('line')
    .data(links).enter().append('line').attr('stroke-width', (d: any) => Math.sqrt(d.weight));

  const node = svg.append('g').selectAll('g').data(nodes).enter().append('g')
    .call(d3.drag<SVGGElement, any>()
      .on('start', (ev, d) => { if (!ev.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => { if (!ev.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
    );
  node.append('circle')
    .attr('r', (d: any) => d.isYk ? 12 : Math.sqrt(d.papers_with_yk) * 3 + 4)
    .attr('fill', (d: any) => d.isYk ? '#B0492A' : '#1B2E5E');
  node.append('title').text((d: any) => `${d.name} — ${d.papers_with_yk} papers with YK`);
  node.append('text')
    .text((d: any) => d.name.split(',')[0])
    .attr('font-family', 'IBM Plex Mono')
    .attr('font-size', 10)
    .attr('fill', '#4C463D')
    .attr('dx', 10)
    .attr('dy', 3);

  sim.on('tick', () => {
    link.attr('x1', (d: any) => d.source.x).attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x).attr('y2', (d: any) => d.target.y);
    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
  });

  const prefersReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduce) {
    sim.alpha(1).tick(300).stop();
    link.attr('x1', (d: any) => d.source.x).attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x).attr('y2', (d: any) => d.target.y);
    node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
  } else {
    setTimeout(() => sim.stop(), 800);
  }
</script>
```

- [ ] **Step 2: Add it to the analytics page**

Modify `site/src/pages/analytics.astro`. After the `<section>` block, before `<div id="chart-grid">`, add:

```astro
---
// add to the frontmatter import block at the top:
import CoauthorNetwork from '../components/analytics/CoauthorNetwork.astro';
---

<!-- replace the old <div id="chart-grid"> with: -->
<div class="mt-10 space-y-6">
  <CoauthorNetwork />
  <!-- (E3–E9 will append more chart components here) -->
</div>
```

- [ ] **Step 3: Build + preview**

```bash
cd site && npm run build && npm run preview
```

Visit `/analytics`. Verify the force graph renders, settles in ~1 s, and shows YK at center with co-author nodes.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/CoauthorNetwork.astro site/src/pages/analytics.astro
git commit -m "feat(site): co-author force-directed network on /analytics"
```

---

### Task E3: Papers per year (Chart.js stacked bar)

**Files:**
- Create: `site/src/components/analytics/PapersPerYear.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `PapersPerYear.astro`**

```astro
---
import { bundle } from '../../lib/data';
const ppy = bundle.metrics.papers_per_year;
const years = Object.keys(ppy).map(Number).sort((a, b) => a - b);
const data = {
  labels: years,
  first: years.map((y) => ppy[y].first + (ppy[y].sole ?? 0)),
  middle: years.map((y) => ppy[y].middle),
  last: years.map((y) => ppy[y].last),
};
const now = new Date().getUTCFullYear();
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Papers per year</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">stacked by author position</span>
  </figcaption>
  <div class="w-full h-[260px]"><canvas id="papers-per-year" data-payload={JSON.stringify({ data, currentYear: now })}></canvas></div>
</figure>

<script>
  import Chart from 'chart.js/auto';
  const canvas = document.getElementById('papers-per-year') as HTMLCanvasElement;
  const { data, currentYear } = JSON.parse(canvas.dataset.payload!);
  const firstColors = data.labels.map((y: number) => y === currentYear ? '#B0492A' : '#1B2E5E');
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [
        { label: 'First / sole', data: data.first, backgroundColor: firstColors, stack: 's' },
        { label: 'Middle',       data: data.middle, backgroundColor: '#DCD5C5', stack: 's' },
        { label: 'Last',         data: data.last,   backgroundColor: '#8C8579', stack: 's' },
      ],
    },
    options: {
      animation: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? false : { duration: 600 },
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font: { family: 'IBM Plex Mono', size: 10 } } } },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { font: { family: 'IBM Plex Mono', size: 10 } } },
        y: { stacked: true, beginAtZero: true, ticks: { font: { family: 'IBM Plex Mono', size: 10 }, precision: 0 } },
      },
    },
  });
</script>
```

- [ ] **Step 2: Add to `analytics.astro`**

```astro
import PapersPerYear from '../components/analytics/PapersPerYear.astro';
...
<!-- Inside the chart container, after <CoauthorNetwork />: -->
<div class="grid md:grid-cols-2 gap-6">
  <PapersPerYear />
  <!-- E4 will be appended next to this -->
</div>
```

- [ ] **Step 3: Build + preview**

```bash
cd site && npm run build && npm run preview
```

Verify the stacked bar renders, current year highlighted in sienna.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/PapersPerYear.astro site/src/pages/analytics.astro
git commit -m "feat(site): papers-per-year stacked-bar chart"
```

---

### Task E4: Cumulative citations + per-year (Chart.js combo)

**Files:**
- Create: `site/src/components/analytics/CitationsCumulative.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `CitationsCumulative.astro`**

```astro
---
import { bundle } from '../../lib/data';
const peryear = bundle.metrics.citations_per_year;
const cum = bundle.metrics.cumulative_citations;
const years = Object.keys(cum).map(Number).sort((a, b) => a - b);
const payload = {
  labels: years,
  perYear: years.map((y) => peryear[y] ?? 0),
  cumulative: years.map((y) => cum[y] ?? 0),
};
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Cumulative citations + per-year</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">approximation: attributed to publication year</span>
  </figcaption>
  <div class="w-full h-[260px]"><canvas id="citations-cumulative" data-payload={JSON.stringify(payload)}></canvas></div>
</figure>

<script>
  import Chart from 'chart.js/auto';
  const canvas = document.getElementById('citations-cumulative') as HTMLCanvasElement;
  const p = JSON.parse(canvas.dataset.payload!);
  new Chart(canvas, {
    data: {
      labels: p.labels,
      datasets: [
        { type: 'bar', label: 'Per year', data: p.perYear,
          backgroundColor: '#DCD5C5', yAxisID: 'y' },
        { type: 'line', label: 'Cumulative', data: p.cumulative,
          borderColor: '#1B2E5E', backgroundColor: '#1B2E5E',
          tension: 0.2, pointRadius: 3, yAxisID: 'y1' },
      ],
    },
    options: {
      animation: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? false : { duration: 600 },
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { font: { family: 'IBM Plex Mono', size: 10 } } } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: 'IBM Plex Mono', size: 10 } } },
        y:  { position: 'left',  beginAtZero: true, ticks: { font: { family: 'IBM Plex Mono', size: 10 } } },
        y1: { position: 'right', beginAtZero: true, grid: { display: false },
              ticks: { font: { family: 'IBM Plex Mono', size: 10 } } },
      },
    },
  });
</script>
```

- [ ] **Step 2: Add to `analytics.astro`** (inside the same `grid md:grid-cols-2` row as Task E3)

```astro
import CitationsCumulative from '../components/analytics/CitationsCumulative.astro';
...
<div class="grid md:grid-cols-2 gap-6">
  <PapersPerYear />
  <CitationsCumulative />
</div>
```

- [ ] **Step 3: Build + preview**, verify the dual-axis combo renders.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/CitationsCumulative.astro site/src/pages/analytics.astro
git commit -m "feat(site): cumulative citations + per-year combo chart"
```

---

### Task E5: h-index trajectory (plain SVG)

**Files:**
- Create: `site/src/components/analytics/HIndexCurve.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `HIndexCurve.astro`**

```astro
---
import { bundle } from '../../lib/data';
const curve = bundle.metrics.h_index_curve;
const years = Object.keys(curve).map(Number).sort((a, b) => a - b);
const points = years.map((y) => ({ x: y, h: curve[y] }));
const maxH = Math.max(...years.map((y) => curve[y]), 1);
const w = 480, h = 240, padX = 36, padY = 24;

const scaleX = (x: number) => padX + ((x - years[0]) / Math.max(years.length - 1, 1)) * (w - 2 * padX);
const scaleY = (val: number) => h - padY - (val / maxH) * (h - 2 * padY);

const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.x)} ${scaleY(p.h)}`).join(' ');
const stepPath = points.map((p, i) => {
  if (i === 0) return `M ${scaleX(p.x)} ${scaleY(p.h)}`;
  const prev = points[i - 1];
  return `L ${scaleX(p.x)} ${scaleY(prev.h)} L ${scaleX(p.x)} ${scaleY(p.h)}`;
}).join(' ');

const hirschEnd = scaleY(years.length);   // 1:1 reference line: y = (year - first_year + 1)
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">h-index trajectory</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">step curve · dashed = Hirsch 1:1 reference</span>
  </figcaption>
  <svg viewBox={`0 0 ${w} ${h}`} class="w-full h-[260px]" aria-labelledby="h-curve-title">
    <title id="h-curve-title">h-index trajectory across years</title>
    <line x1={padX} y1={h - padY} x2={w - padX} y2={h - padY} stroke="#DCD5C5"/>
    <line x1={padX} y1={padY}     x2={padX}     y2={h - padY} stroke="#DCD5C5"/>
    <line x1={padX} y1={h - padY} x2={w - padX} y2={hirschEnd} stroke="#DCD5C5" stroke-dasharray="4 4"/>
    <path d={stepPath} fill="none" stroke="#1B2E5E" stroke-width="1.6"/>
    {points.map((p) => (
      <circle cx={scaleX(p.x)} cy={scaleY(p.h)} r="3" fill={p.x === years[years.length - 1] ? '#B0492A' : '#1B2E5E'}>
        <title>{p.x} : h = {p.h}</title>
      </circle>
    ))}
    {years.map((y) => (
      <text x={scaleX(y)} y={h - 6} font-family="IBM Plex Mono" font-size="9" fill="#8C8579" text-anchor="middle">{y}</text>
    ))}
    <text x={w - padX} y={scaleY(curve[years[years.length - 1]]) - 6}
          font-family="IBM Plex Mono" font-size="10" fill="#B0492A" text-anchor="end">
      h = {curve[years[years.length - 1]]}
    </text>
  </svg>
  <table class="sr-only">
    <caption>h-index by year</caption>
    <tr><th>Year</th><th>h-index</th></tr>
    {years.map((y) => <tr><td>{y}</td><td>{curve[y]}</td></tr>)}
  </table>
</figure>
```

- [ ] **Step 2: Add to `analytics.astro`** in a new row:

```astro
import HIndexCurve from '../components/analytics/HIndexCurve.astro';
...
<div class="grid md:grid-cols-2 gap-6">
  <HIndexCurve />
  <!-- AuthorPosition will be added here in Task E6 -->
</div>
```

- [ ] **Step 3: Build + preview**

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/HIndexCurve.astro site/src/pages/analytics.astro
git commit -m "feat(site): h-index trajectory chart (plain SVG)"
```

---

### Task E6: Author position donut (Chart.js)

**Files:**
- Create: `site/src/components/analytics/AuthorPosition.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `AuthorPosition.astro`**

```astro
---
import { bundle } from '../../lib/data';
const t = bundle.metrics.author_position_total;
const total = Object.values(t).reduce((a, b) => a + b, 0);
const firstPct = total ? Math.round(((t.first + (t.sole ?? 0)) / total) * 100) : 0;
const payload = { first: t.first + (t.sole ?? 0), middle: t.middle, last: t.last, firstPct };
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Author position</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">n = {total}</span>
  </figcaption>
  <div class="grid grid-cols-[160px_1fr] items-center gap-4 h-[260px]">
    <div class="relative">
      <canvas id="author-position" data-payload={JSON.stringify(payload)}></canvas>
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <div class="text-[22px] font-medium tracking-tight tabular-nums">{payload.firstPct}%</div>
        <div class="font-mono text-[10px] tracking-widest text-ink-3 uppercase">first</div>
      </div>
    </div>
    <ul class="space-y-2 font-mono text-[12px]">
      <li><span class="inline-block w-2.5 h-2.5 bg-accent mr-2 align-middle"></span>First / sole — {payload.first}</li>
      <li><span class="inline-block w-2.5 h-2.5 bg-mark mr-2 align-middle"></span>Middle — {payload.middle}</li>
      <li><span class="inline-block w-2.5 h-2.5 bg-rule mr-2 align-middle"></span>Last — {payload.last}</li>
    </ul>
  </div>
</figure>

<script>
  import Chart from 'chart.js/auto';
  const canvas = document.getElementById('author-position') as HTMLCanvasElement;
  const p = JSON.parse(canvas.dataset.payload!);
  new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['First / sole', 'Middle', 'Last'],
      datasets: [{
        data: [p.first, p.middle, p.last],
        backgroundColor: ['#1B2E5E', '#B0492A', '#DCD5C5'],
        borderColor: '#F6F4EE', borderWidth: 2,
      }],
    },
    options: {
      cutout: '68%',
      animation: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? false : { duration: 700 },
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
    },
  });
</script>
```

- [ ] **Step 2: Wire into `analytics.astro`** alongside HIndexCurve (same row from Task E5).

- [ ] **Step 3: Build + preview**

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/AuthorPosition.astro site/src/pages/analytics.astro
git commit -m "feat(site): author-position donut chart"
```

---

### Task E7: Top-cited papers (plain SVG ranked bars)

**Files:**
- Create: `site/src/components/analytics/TopCited.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `TopCited.astro`**

```astro
---
import { bundle } from '../../lib/data';
import { renderInlineMath } from '../../lib/math';
const top = bundle.metrics.top_cited;
const maxCites = Math.max(...top.map((p) => p.citation_count), 1);
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Most-cited papers</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">top {top.length}</span>
  </figcaption>
  <ol class="space-y-3">
    {top.map((p, i) => (
      <li class="grid grid-cols-[18px_1fr_60px] gap-3 items-baseline">
        <span class="font-mono text-[11px] text-mark text-right">{i + 1}</span>
        <a class="block hover:text-accent" href={`https://inspirehep.net/literature/${p.inspire_id}`}>
          <div class="text-[13px] text-ink leading-snug truncate" set:html={renderInlineMath(p.title)}></div>
          <div class="h-1 mt-1 bg-rule-2 relative">
            <span class="absolute inset-y-0 left-0 bg-accent" style={`width: ${(p.citation_count / maxCites) * 100}%`}></span>
          </div>
        </a>
        <span class="font-mono text-[12px] text-ink text-right tabular-nums">{p.citation_count}</span>
      </li>
    ))}
  </ol>
</figure>
```

- [ ] **Step 2: Wire into `analytics.astro`** in a new row that will pair with JournalSplit (E8).

- [ ] **Step 3: Build + preview**

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/TopCited.astro site/src/pages/analytics.astro
git commit -m "feat(site): top-cited papers ranked bars"
```

---

### Task E8: Journal venue split (Chart.js horizontal bar)

**Files:**
- Create: `site/src/components/analytics/JournalSplit.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `JournalSplit.astro`**

```astro
---
import { bundle } from '../../lib/data';
const split = bundle.metrics.journal_split;
const sorted = Object.entries(split).sort(([, a], [, b]) => b - a);
const payload = {
  labels: sorted.map(([k]) => k),
  values: sorted.map(([, v]) => v),
};
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Journal / venue split</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">{Object.values(split).reduce((a, b) => a + b, 0)} papers</span>
  </figcaption>
  <div class="w-full h-[260px]"><canvas id="journal-split" data-payload={JSON.stringify(payload)}></canvas></div>
</figure>

<script>
  import Chart from 'chart.js/auto';
  const canvas = document.getElementById('journal-split') as HTMLCanvasElement;
  const p = JSON.parse(canvas.dataset.payload!);
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: p.labels,
      datasets: [{
        data: p.values,
        backgroundColor: p.labels.map((l: string) => l === 'arXiv only' ? '#B0492A' : '#1B2E5E'),
      }],
    },
    options: {
      indexAxis: 'y',
      animation: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? false : { duration: 600 },
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { font: { family: 'IBM Plex Mono', size: 10 }, precision: 0 } },
        y: { grid: { display: false }, ticks: { font: { family: 'IBM Plex Mono', size: 10 } } },
      },
    },
  });
</script>
```

- [ ] **Step 2: Wire into `analytics.astro`** alongside TopCited.

- [ ] **Step 3: Build + preview**

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/JournalSplit.astro site/src/pages/analytics.astro
git commit -m "feat(site): journal venue split horizontal bar"
```

---

### Task E9: Topic / keyword treemap (D3)

**Files:**
- Create: `site/src/components/analytics/TopicTreemap.astro`
- Modify: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `TopicTreemap.astro`**

```astro
---
import { bundle } from '../../lib/data';
const data = JSON.stringify(bundle.metrics.treemap);
---
<figure class="border border-rule bg-paper p-4">
  <figcaption class="flex justify-between items-baseline mb-2">
    <span class="text-[14px] font-medium text-ink">Topic / keyword map</span>
    <span class="font-mono text-[10px] tracking-wider text-ink-3">theme → arXiv category → paper</span>
  </figcaption>
  <div id="topic-treemap" class="w-full h-[360px]" data-tree={data}></div>
</figure>

<script>
  import * as d3 from 'd3';
  const root = document.getElementById('topic-treemap')!;
  const tree = JSON.parse(root.dataset.tree!);
  const w = root.clientWidth, h = root.clientHeight;
  const themeColor = d3.scaleOrdinal<string, string>()
    .domain(['spectrum_quark_models', 'exotic_interactions', 'em_chiPT', 'production'])
    .range(['#1B2E5E', '#3B4F7E', '#7787A8', '#B0492A']);

  const hierarchy = d3.hierarchy(tree)
    .sum((d: any) => d.value ?? 0)
    .sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
  d3.treemap<any>().size([w, h]).padding(2)(hierarchy);

  const svg = d3.select(root).append('svg').attr('viewBox', `0 0 ${w} ${h}`).attr('class', 'w-full h-full');
  const leaf = svg.selectAll('g').data(hierarchy.leaves()).enter().append('g')
    .attr('transform', (d: any) => `translate(${d.x0},${d.y0})`);
  leaf.append('rect')
    .attr('width', (d: any) => d.x1 - d.x0)
    .attr('height', (d: any) => d.y1 - d.y0)
    .attr('fill', (d: any) => {
      const theme = d.ancestors().find((a: any) => a.depth === 1)?.data.name;
      return theme ? themeColor(theme) : '#8C8579';
    })
    .attr('stroke', '#F6F4EE').attr('stroke-width', 1);
  leaf.append('title').text((d: any) => d.data.name);
  leaf.filter((d: any) => (d.x1 - d.x0) > 90 && (d.y1 - d.y0) > 22)
    .append('text')
    .attr('x', 6).attr('y', 14)
    .attr('font-family', 'IBM Plex Mono')
    .attr('font-size', 9).attr('fill', '#F6F4EE')
    .text((d: any) => d.data.name.length > 40 ? d.data.name.slice(0, 40) + '…' : d.data.name);

  // theme labels at depth 1
  hierarchy.descendants().filter((d: any) => d.depth === 1).forEach((d: any) => {
    svg.append('text')
      .attr('x', d.x0 + 6).attr('y', d.y0 + 18)
      .attr('font-family', 'IBM Plex Mono').attr('font-size', 10)
      .attr('fill', '#F6F4EE').attr('font-weight', 600)
      .text((d.data.name as string).replace(/_/g, ' '));
  });
</script>
```

- [ ] **Step 2: Wire into `analytics.astro`** as the final, full-width row:

```astro
import TopicTreemap from '../components/analytics/TopicTreemap.astro';
...
<TopicTreemap />
```

- [ ] **Step 3: Build + preview**, verify all eight figures render in the layout from spec §4.5.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/analytics/TopicTreemap.astro site/src/pages/analytics.astro
git commit -m "feat(site): topic/keyword D3 treemap"
```

---

## Phase F · Polish, mockup snapshot, and deploy

### Task F1: Commit the visual reference mockup

**Files:**
- Create: `mockups/home.html`

- [ ] **Step 1: Find the brainstorm mockup**

```bash
ls .superpowers/brainstorm/*/content/visual-style-v2.html | head -1
```

- [ ] **Step 2: Copy it into `mockups/`**

```bash
mkdir -p mockups
cp "$(ls .superpowers/brainstorm/*/content/visual-style-v2.html | head -1)" mockups/home.html
```

- [ ] **Step 3: Commit**

```bash
git add mockups/home.html
git commit -m "docs(mockups): commit the hybrid A+B home-hero reference"
```

---

### Task F2: GitHub Actions deploy workflow

**Files:**
- Create: `.github/workflows/deploy.yml`

- [ ] **Step 1: Write `.github/workflows/deploy.yml`**

```yaml
name: Deploy site to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: site } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: site/package-lock.json
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Verify with `act` (optional, if installed) or just push**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: deploy to GitHub Pages on push to main"
```

- [ ] **Step 3: Enable Pages in repo settings**

In the GitHub repo settings → Pages → set source to **GitHub Actions** (not a branch). This step is manual and must be done in the GitHub UI before pushing.

---

### Task F3: Full smoke test

- [ ] **Step 1: Clean build**

```bash
cd site && rm -rf dist .astro node_modules/.vite && npm ci && npm run build
```

Expected: build succeeds. `dist/` contains: `index.html`, `research/index.html`, `publications/index.html`, `talks/index.html`, `analytics/index.html`, `cv/index.html`, `sitemap-index.xml`, and the `cv/CV_YKChen.pdf` + `photo.png` assets.

- [ ] **Step 2: Preview, click every nav link, verify each page renders**

```bash
npm run preview
```

In the browser:
1. `/` — hero, photo, numbers strip, 5 papers (math in titles), 4 themes ✓
2. `/research` — 4 sections, papers per theme ✓
3. `/publications` — all 18 papers, filter chips work, URL updates ✓
4. `/talks` — 3 oral + 1 poster ✓
5. `/analytics` — all 8 charts render, force graph settles ✓
6. `/cv` — content + PDF download works ✓

- [ ] **Step 3: Lighthouse on `/analytics` (heaviest page)**

```bash
npx lighthouse http://localhost:4321/analytics/ --view --only-categories=performance,accessibility
```

Targets: Performance ≥ 95, Accessibility ≥ 95. If either fails, file follow-up tasks but do not block merge.

- [ ] **Step 4: Push and watch the deploy**

```bash
git push
```

In the GitHub UI, watch the **Deploy site to GitHub Pages** workflow run. When the green check appears, visit the printed `https://<owner>.github.io/<repo>/` URL and verify all pages render.

- [ ] **Step 5: Commit any tweaks discovered in QA, push again.**

---

### Task F4: Update README with the live URL

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace the `Live: TBD` line**

Find this in `README.md`:

```markdown
Live: TBD (default GitHub Pages URL until a custom domain is configured).
```

Replace with the actual deployed URL, e.g.:

```markdown
Live: https://<owner>.github.io/<repo>/
```

- [ ] **Step 2: Commit + push**

```bash
git add README.md
git commit -m "docs: point README at the live URL"
git push
```

---

## Self-review checklist (run after the plan is written, before handoff)

- [ ] **Spec § coverage:** §1 audience → no task, but no work required. §2 IA → all 6 pages exist as Tasks D1–D5 + E1. §3 visual system → Tasks A3 (tokens), C1 (layout), D1 (hero), F1 (mockup). §4 pages → Tasks D1–D5 + E1. §5 data pipeline → Tasks B1–B6. §6 8 charts → Tasks E2–E9. §7 tech stack → Tasks A2, A3. §8 deployment → Tasks F2, F3. §9 a11y → built into PaperRow/HIndexCurve (`<table class="sr-only">`), `prefers-reduced-motion` in charts and global.css.
- [ ] **Placeholder scan:** the only "TBD" strings are the four research-theme intro paragraphs in D2 (Spec §10 explicitly defers these to YK) and the `Live: TBD` line in README (resolved in F4). No other TBD/TODO/"implement later" left.
- [ ] **Type consistency:** `AuthorPosition` literal `'first' | 'middle' | 'last' | 'sole'` is used in B1 (models.py), B3 (parsers.py), B4 (derive_metrics.py), and C1 (data.ts). `is_yk_first` is defined as `position == 'first' or 'sole'` in B1 and that semantics is preserved in D1's filter and E6's donut computation (`t.first + t.sole`).
- [ ] **File-path consistency:** all chart components live at `site/src/components/analytics/*.astro`; all pages live at `site/src/pages/*.astro`; `inspire.json` is consistently at `site/src/data/inspire.json`. No drift.
- [ ] **Theme-slug consistency:** themes.yaml uses `em_chiPT / exotic_interactions / production / spectrum_quark_models`. The research page (D2) maps page-section slugs `em / interaction / production / spectrum` → these YAML keys with an inline `.replace()` chain; that mapping is the only place the page-slug ↔ data-slug coupling lives. Task D2 explicitly notes this so a later refactor stays bounded.
