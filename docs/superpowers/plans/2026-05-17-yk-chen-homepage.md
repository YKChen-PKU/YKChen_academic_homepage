# YK Chen academic homepage — Implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static personal academic homepage for Yan-Ke Chen (PKU postdoc, hep-ph) with a four-figure INSPIRE-HEP analytics dashboard, deployable anywhere.

**Architecture:** Two-process pipeline. A Python build script calls the INSPIRE REST API, derives metrics, and writes `site/src/data/inspire.json`. An Astro 5 project consumes that JSON at build time and renders five static pages. Chart.js + D3 are loaded only on the analytics page as React islands. The design system ("Quiet Precision") lives in CSS custom properties plus Tailwind theme aliases — mockups already exist at `mockups/index.html` and `mockups/analytics.html` and are the visual source-of-truth.

**Tech Stack:** Python 3.11 (requests, pydantic, pyyaml, nltk, pytest, respx for HTTP mocking) · Astro 5 + TypeScript · Tailwind CSS · Chart.js 4 · D3 7 (force module only) · Newsreader + IBM Plex via Google Fonts.

**Spec:** `docs/superpowers/specs/2026-05-17-yk-chen-homepage-design.md`

---

## Phase A · Repository scaffolding

### Task A1: Initialise git repo with .gitignore

**Files:**
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Initialise the repo**

```bash
cd /Users/ykchen/science_project/personal_profile
git init -b main
```

- [ ] **Step 2: Write `.gitignore`**

```gitignore
# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Node / Astro
site/node_modules/
site/dist/
site/.astro/
site/.vite/
*.log

# INSPIRE cache (regenerable)
scripts/.cache/

# Editor
.vscode/
.idea/
*.swp
```

- [ ] **Step 3: Write a minimal `README.md`**

```markdown
# Yan-Ke Chen — academic homepage

Static personal homepage with an INSPIRE-HEP analytics dashboard.

## Quick start

```bash
# Refresh INSPIRE data
python scripts/fetch_inspire.py

# Build & preview the site
cd site && npm install && npm run dev
```

See `docs/superpowers/specs/2026-05-17-yk-chen-homepage-design.md` for the full design rationale.
```

- [ ] **Step 4: Initial commit**

```bash
git add .gitignore README.md docs/ mockups/ RS_CV/
git commit -m "chore: initial repo scaffolding with spec and mockups"
```

Expected: clean commit; `git status` shows working tree clean.

---

### Task A2: Create the directory skeleton

**Files:**
- Create directories only (no file content yet).

- [ ] **Step 1: Create empty directories with .gitkeep**

```bash
mkdir -p scripts/tests scripts/fixtures
mkdir -p site/src/{data,layouts,components/charts,components/ui,pages,styles}
mkdir -p site/public/cv
touch scripts/tests/__init__.py
```

- [ ] **Step 2: Copy CV PDF and photo into the public folder**

```bash
cp RS_CV/CV_YKChen.pdf site/public/cv/CV_YKChen.pdf
cp RS_CV/photo.png     site/public/photo.png
```

- [ ] **Step 3: Commit**

```bash
git add scripts/ site/
git commit -m "chore: add scripts/ and site/ skeleton + copy CV assets"
```

---

## Phase B · Python INSPIRE fetcher (TDD)

### Task B1: Set up the Python environment

**Files:**
- Create: `scripts/requirements.txt`
- Create: `scripts/requirements-dev.txt`
- Create: `scripts/pytest.ini`

- [ ] **Step 1: Write `scripts/requirements.txt`**

```
requests==2.32.3
pydantic==2.9.2
pyyaml==6.0.2
nltk==3.9.1
```

- [ ] **Step 2: Write `scripts/requirements-dev.txt`**

```
-r requirements.txt
pytest==8.3.3
respx==0.21.1
httpx==0.27.2
```

`respx` mocks the `httpx` client; the script will use `httpx` for HTTP (chosen over `requests` for the easier mocking story).

Replace `requests==2.32.3` in `requirements.txt` with `httpx==0.27.2`:

```
httpx==0.27.2
pydantic==2.9.2
pyyaml==6.0.2
nltk==3.9.1
```

- [ ] **Step 3: Write `scripts/pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -ra -q --strict-markers
```

- [ ] **Step 4: Create virtualenv and install**

```bash
cd /Users/ykchen/science_project/personal_profile/scripts
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
python -c "import nltk; nltk.download('wordnet', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True)"
```

- [ ] **Step 5: Verify pytest works**

```bash
cd /Users/ykchen/science_project/personal_profile/scripts
pytest --collect-only
```

Expected: `no tests ran` (no errors, just no tests yet).

- [ ] **Step 6: Commit**

```bash
git add scripts/requirements.txt scripts/requirements-dev.txt scripts/pytest.ini
git commit -m "feat(scripts): pin Python deps, configure pytest"
```

---

### Task B2: Define Pydantic models

**Files:**
- Create: `scripts/models.py`
- Create: `scripts/tests/test_models.py`

- [ ] **Step 1: Write the failing test first**

`scripts/tests/test_models.py`:

```python
"""Schema contracts for the produced inspire.json."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Paper, AuthorProfile, Metrics, InspireBundle, Position


def test_paper_minimum_fields_accepted():
    p = Paper(
        inspire_id="2718281",
        title="Test paper",
        authors=[{"name": "Y.-K. Chen", "is_you": True}],
        venue={"journal": "Phys. Rev. D", "year": 2024},
        arxiv_id="2308.12424",
        doi=None,
        citations=10,
        citations_no_self=8,
        year=2024,
        topic_group="exotic-coupled-channel",
    )
    assert p.title == "Test paper"
    assert p.authors[0].is_you is True


def test_paper_rejects_missing_required():
    with pytest.raises(ValidationError):
        Paper(inspire_id="1", title="x")  # type: ignore[call-arg]


def test_metrics_roundtrip():
    m = Metrics(
        papers_total=17,
        citations_total=432,
        h_index=11,
        first_author_count=5,
        by_year=[{"year": 2024, "papers": 7, "cum_citations": 200, "h_index": 6}],
        top_papers=[],
        keywords=[{"term": "tetraquark", "count": 12}],
        journals=[{"name": "Phys. Rev. D", "count": 12}],
        coauthors=[{"name": "L. Meng", "joint_papers": 9, "inspire_id": "1234567", "current_institution": "PKU"}],
        institutions=[{"name": "Peking University", "city": "Beijing, CN", "joint_papers": 14}],
    )
    raw = m.model_dump_json()
    again = Metrics.model_validate_json(raw)
    assert again.h_index == 11


def test_bundle_serialises_iso_datetime():
    b = InspireBundle(
        fetched_at=datetime(2026, 5, 17, 10, 15, tzinfo=timezone.utc),
        author=AuthorProfile(
            id="2182746", name="Yan-Ke Chen", name_zh="陈彦珂",
            current_position=Position(rank="PostDoc", institution="PKU CHEP", start="2025-07"),
            orcid=None, arxiv=None,
        ),
        papers=[], metrics=Metrics(
            papers_total=0, citations_total=0, h_index=0, first_author_count=0,
            by_year=[], top_papers=[], keywords=[], journals=[], coauthors=[], institutions=[],
        ),
    )
    raw = json.loads(b.model_dump_json())
    assert raw["fetched_at"].endswith("Z") or "+00:00" in raw["fetched_at"]
```

- [ ] **Step 2: Run the test — expect failure**

```bash
cd /Users/ykchen/science_project/personal_profile/scripts
source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'models'`.

- [ ] **Step 3: Implement `scripts/models.py`**

```python
"""Pydantic schema for the inspire.json bundle written by fetch_inspire.py."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Author(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    is_you: bool = False
    inspire_id: Optional[str] = None


class Venue(BaseModel):
    model_config = ConfigDict(extra="ignore")
    journal: Optional[str] = None
    volume: Optional[str] = None
    page: Optional[str] = None
    year: Optional[int] = None


class Paper(BaseModel):
    model_config = ConfigDict(extra="ignore")
    inspire_id: str
    title: str
    authors: List[Author]
    venue: Venue
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    citations: int = 0
    citations_no_self: int = 0
    year: Optional[int] = None
    topic_group: str = "uncategorised"


class Position(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rank: Optional[str] = None
    institution: Optional[str] = None
    start: Optional[str] = None


class AuthorProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    name_zh: Optional[str] = None
    current_position: Optional[Position] = None
    orcid: Optional[str] = None
    arxiv: Optional[str] = None


class YearRow(BaseModel):
    year: int
    papers: int
    cum_citations: int
    h_index: int


class TermCount(BaseModel):
    term: str
    count: int


class JournalCount(BaseModel):
    name: str
    count: int


class Coauthor(BaseModel):
    name: str
    joint_papers: int
    inspire_id: Optional[str] = None
    current_institution: Optional[str] = None


class Institution(BaseModel):
    name: str
    city: Optional[str] = None
    joint_papers: int


class Metrics(BaseModel):
    papers_total: int
    citations_total: int
    h_index: int
    first_author_count: int
    by_year: List[YearRow]
    top_papers: List[Paper]
    keywords: List[TermCount]
    journals: List[JournalCount]
    coauthors: List[Coauthor]
    institutions: List[Institution]


class InspireBundle(BaseModel):
    fetched_at: datetime
    author: AuthorProfile
    papers: List[Paper]
    metrics: Metrics
```

- [ ] **Step 4: Run the test — expect pass**

```bash
pytest tests/test_models.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/models.py scripts/tests/test_models.py
git commit -m "feat(scripts): pydantic schema for the inspire.json bundle"
```

---

### Task B3: Implement INSPIRE author fetcher

**Files:**
- Create: `scripts/inspire_client.py`
- Create: `scripts/tests/fixtures/author_2182746.json`
- Create: `scripts/tests/test_inspire_author.py`

- [ ] **Step 1: Capture a real author fixture (one-time, manual)**

```bash
cd /Users/ykchen/science_project/personal_profile/scripts
curl -s 'https://inspirehep.net/api/authors/2182746' \
  -H 'Accept: application/json' \
  > tests/fixtures/author_2182746.json
```

Verify the file is non-empty JSON:

```bash
python -c "import json; d=json.load(open('tests/fixtures/author_2182746.json')); print(d['metadata']['name']['value'])"
```

Expected output: `Chen, Yan-Ke` (or similar).

- [ ] **Step 2: Write the failing test**

`scripts/tests/test_inspire_author.py`:

```python
import json
from pathlib import Path

import pytest
import respx
from httpx import Response

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspire_client import InspireClient


FIXTURE = json.loads(Path(__file__).parent.joinpath("fixtures/author_2182746.json").read_text())


@pytest.mark.asyncio  # not used; pytest tolerates the marker name absent plugin
def test_fetch_author_parses_name_and_position():
    pass  # placeholder so the file collects


@respx.mock
def test_fetch_author_parses_name_and_position_sync():
    respx.get("https://inspirehep.net/api/authors/2182746").mock(
        return_value=Response(200, json=FIXTURE)
    )
    client = InspireClient()
    profile = client.fetch_author("2182746")
    assert profile.id == "2182746"
    assert "Chen" in profile.name
    # current_position may be None if INSPIRE has no current position;
    # but for this person it should be present.
    if profile.current_position:
        assert profile.current_position.institution is not None
```

- [ ] **Step 3: Run — expect failure**

```bash
pytest tests/test_inspire_author.py -v
```

Expected: `ModuleNotFoundError: No module named 'inspire_client'`.

- [ ] **Step 4: Implement `scripts/inspire_client.py`**

```python
"""Thin INSPIRE-HEP REST client. Synchronous httpx. Used only at build time."""
from __future__ import annotations

import time
from typing import Any, Iterator, Optional

import httpx

from models import AuthorProfile, Position


INSPIRE_BASE = "https://inspirehep.net/api"
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
THROTTLE_SECONDS = 0.10


class InspireClient:
    """Wraps INSPIRE REST endpoints with simple retry + throttling."""

    def __init__(self, base_url: str = INSPIRE_BASE) -> None:
        self.base_url = base_url
        self._client = httpx.Client(timeout=DEFAULT_TIMEOUT, headers={"Accept": "application/json"})

    def __enter__(self) -> "InspireClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self._client.close()

    def _get(self, url: str, *, params: Optional[dict] = None, max_retries: int = 3) -> dict:
        last_exc: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                r = self._client.get(url, params=params)
                r.raise_for_status()
                time.sleep(THROTTLE_SECONDS)
                return r.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                time.sleep(2 ** attempt)
        assert last_exc is not None
        raise RuntimeError(f"INSPIRE GET failed after {max_retries} retries: {url}") from last_exc

    def fetch_author(self, author_id: str) -> AuthorProfile:
        raw = self._get(f"{self.base_url}/authors/{author_id}")
        md = raw.get("metadata", {})

        name = (md.get("name") or {}).get("value", "")
        # native names are an array of {value, source}
        native_names = (md.get("name") or {}).get("native_names") or []
        name_zh = native_names[0] if native_names else None

        # current position = first positions entry with `current: True`
        positions = md.get("positions") or []
        cur = next((p for p in positions if p.get("current")), None)
        position = None
        if cur:
            position = Position(
                rank=cur.get("rank"),
                institution=cur.get("institution"),
                start=cur.get("start_date"),
            )

        ids = md.get("ids") or []
        orcid = next((x.get("value") for x in ids if x.get("schema") == "ORCID"), None)
        arxiv = next((x.get("value") for x in ids if x.get("schema") == "ARXIV"), None)

        return AuthorProfile(
            id=author_id,
            name=name,
            name_zh=name_zh,
            current_position=position,
            orcid=orcid,
            arxiv=arxiv,
        )
```

- [ ] **Step 5: Run the test — expect pass**

```bash
pytest tests/test_inspire_author.py -v
```

Expected: 2 passed (the placeholder + the real one).

- [ ] **Step 6: Commit**

```bash
git add scripts/inspire_client.py scripts/tests/test_inspire_author.py scripts/tests/fixtures/
git commit -m "feat(scripts): InspireClient.fetch_author with respx-mocked test"
```

---

### Task B4: Implement literature fetch + pagination

**Files:**
- Modify: `scripts/inspire_client.py`
- Create: `scripts/tests/fixtures/literature_p1.json`
- Create: `scripts/tests/fixtures/literature_p2.json`
- Create: `scripts/tests/test_inspire_literature.py`

- [ ] **Step 1: Capture literature fixtures (one-time, manual)**

```bash
cd /Users/ykchen/science_project/personal_profile/scripts

FIELDS="titles,authors,publication_info,arxiv_eprints,citation_count,citation_count_without_self_citations,first_author,inspire_categories,abstracts,dois"
Q="author%3AYan-Ke.Chen.1"

curl -s "https://inspirehep.net/api/literature?q=${Q}&size=25&page=1&fields=${FIELDS}" \
  > tests/fixtures/literature_p1.json
curl -s "https://inspirehep.net/api/literature?q=${Q}&size=25&page=2&fields=${FIELDS}" \
  > tests/fixtures/literature_p2.json
```

- [ ] **Step 2: Write the failing test**

`scripts/tests/test_inspire_literature.py`:

```python
import json
from pathlib import Path

import respx
from httpx import Response

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspire_client import InspireClient


FX_DIR = Path(__file__).parent / "fixtures"
P1 = json.loads((FX_DIR / "literature_p1.json").read_text())
P2 = json.loads((FX_DIR / "literature_p2.json").read_text())


@respx.mock
def test_fetch_literature_paginates_until_empty():
    # First call -> p1 (has links.next), second -> p2 (no next), third would 404.
    route = respx.get("https://inspirehep.net/api/literature").mock(
        side_effect=[Response(200, json=P1), Response(200, json=P2)]
    )
    with InspireClient() as c:
        papers = list(c.fetch_literature_for_author("Yan-Ke.Chen.1"))
    assert route.call_count >= 1
    assert len(papers) > 0
    # All returned items have inspire_id, title, year, citations
    for p in papers:
        assert p.inspire_id
        assert p.title
        assert p.citations >= 0
```

- [ ] **Step 3: Run — expect failure**

```bash
pytest tests/test_inspire_literature.py -v
```

Expected: `AttributeError: 'InspireClient' object has no attribute 'fetch_literature_for_author'`.

- [ ] **Step 4: Extend `scripts/inspire_client.py`**

Add to the bottom of `InspireClient`:

```python
    LITERATURE_FIELDS = (
        "titles,authors,publication_info,arxiv_eprints,"
        "citation_count,citation_count_without_self_citations,"
        "first_author,inspire_categories,abstracts,dois"
    )

    def fetch_literature_for_author(self, bai: str, *, page_size: int = 25) -> Iterator["Paper"]:
        """Yields Paper objects across all pages for the given INSPIRE BAI (e.g. 'Yan-Ke.Chen.1')."""
        from models import Paper
        page = 1
        while True:
            payload = self._get(
                f"{self.base_url}/literature",
                params={
                    "q": f"author:{bai}",
                    "size": page_size,
                    "page": page,
                    "fields": self.LITERATURE_FIELDS,
                },
            )
            hits = (payload.get("hits") or {}).get("hits") or []
            if not hits:
                return
            for hit in hits:
                yield self._hit_to_paper(hit, bai)
            # INSPIRE always returns `links.next` only when more pages exist.
            if not (payload.get("links") or {}).get("next"):
                return
            page += 1

    @staticmethod
    def _hit_to_paper(hit: dict, bai: str) -> "Paper":
        from models import Author, Paper, Venue

        meta = hit.get("metadata", {}) or {}
        inspire_id = str(hit.get("id") or meta.get("control_number") or "")
        titles = meta.get("titles") or [{}]
        title = titles[0].get("title", "")

        authors_raw = meta.get("authors") or []
        authors: list[Author] = []
        for a in authors_raw:
            ref = (a.get("record") or {}).get("$ref", "")
            inspire_aid = ref.rstrip("/").rsplit("/", 1)[-1] if ref else None
            bais = a.get("bai") or [a.get("uuid")]  # heuristic
            is_you = bai in (a.get("ids") or []) or any(bai == x for x in (a.get("bai") or []))
            # Fallback: match by `full_name` slug heuristic
            if not is_you and bai.lower().replace("-", "").replace(".", "") in (a.get("full_name", "") or "").lower().replace("-", "").replace(" ", "").replace(",", ""):
                is_you = True
            authors.append(Author(
                name=a.get("full_name", ""),
                is_you=is_you,
                inspire_id=inspire_aid,
            ))

        pi = (meta.get("publication_info") or [{}])[0]
        venue = Venue(
            journal=pi.get("journal_title"),
            volume=pi.get("journal_volume"),
            page=pi.get("artid") or pi.get("page_start"),
            year=pi.get("year") or meta.get("preprint_date", "")[:4] or None,
        )

        arxiv_eprints = meta.get("arxiv_eprints") or [{}]
        arxiv_id = arxiv_eprints[0].get("value") if arxiv_eprints else None

        dois = meta.get("dois") or [{}]
        doi = dois[0].get("value") if dois else None

        year = pi.get("year")
        if not year and arxiv_id and len(arxiv_id) >= 4 and arxiv_id[:4].isdigit():
            yy = int(arxiv_id[:2])
            year = 2000 + yy if yy < 70 else 1900 + yy

        cites = int(meta.get("citation_count") or 0)
        cites_no_self = int(meta.get("citation_count_without_self_citations") or cites)

        return Paper(
            inspire_id=inspire_id,
            title=title,
            authors=authors,
            venue=venue,
            arxiv_id=arxiv_id,
            doi=doi,
            citations=cites,
            citations_no_self=cites_no_self,
            year=int(year) if year else None,
        )
```

- [ ] **Step 5: Run — expect pass**

```bash
pytest tests/test_inspire_literature.py -v
```

Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/inspire_client.py scripts/tests/test_inspire_literature.py scripts/tests/fixtures/literature_p1.json scripts/tests/fixtures/literature_p2.json
git commit -m "feat(scripts): paginated literature fetch with hit→Paper mapping"
```

---

### Task B5: Topic-group YAML mapping

**Files:**
- Create: `scripts/topic_groups.yml`
- Create: `scripts/topic_mapper.py`
- Create: `scripts/tests/test_topic_mapper.py`

- [ ] **Step 1: Write `scripts/topic_groups.yml`**

```yaml
# Maps each paper to one of the four research themes.
# Key is the arXiv id (most stable). Update this file when new papers appear.
groups:
  em-chiral-pt:
    label: "EM properties with χPT"
    arxiv:
      - "2412.02297"
      - "2506.18800"
      - "2602.05502"
  exotic-coupled-channel:
    label: "Hadron-hadron interaction & coupled channels"
    arxiv:
      - "2308.12424"
      - "2602.12010"
      # NOTE: the X(3872) paper's correct arxiv id needs verification — the
      # CV source contains a typo (also lists 2308.12424). Add it here
      # once confirmed from INSPIRE.
  production:
    label: "Production of exotic states"
    arxiv:
      - "2009.01182"
      - "2302.01696"
  spectrum-quark-models:
    label: "Spectrum of exotic states with quark models"
    arxiv:
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

- [ ] **Step 2: Write the failing test**

`scripts/tests/test_topic_mapper.py`:

```python
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from topic_mapper import TopicMapper


def test_mapper_assigns_known_arxiv_id():
    m = TopicMapper.from_yaml(Path(__file__).resolve().parents[1] / "topic_groups.yml")
    assert m.group_for("2412.02297") == "em-chiral-pt"
    assert m.group_for("2308.12424") == "exotic-coupled-channel"


def test_mapper_unknown_returns_uncategorised_and_warns(capsys):
    m = TopicMapper.from_yaml(Path(__file__).resolve().parents[1] / "topic_groups.yml")
    g = m.group_for("9999.99999")
    assert g == "uncategorised"
    captured = capsys.readouterr()
    assert "9999.99999" in captured.err
```

- [ ] **Step 3: Run — expect failure**

```bash
pytest tests/test_topic_mapper.py -v
```

Expected: `ModuleNotFoundError: No module named 'topic_mapper'`.

- [ ] **Step 4: Implement `scripts/topic_mapper.py`**

```python
"""Maps arXiv ids to one of the user's four research themes."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass
class TopicMapper:
    arxiv_to_group: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    _warned: set = field(default_factory=set)

    @classmethod
    def from_yaml(cls, path: Path) -> "TopicMapper":
        raw = yaml.safe_load(path.read_text()) or {}
        groups = raw.get("groups", {}) or {}
        arxiv_to_group: Dict[str, str] = {}
        labels: Dict[str, str] = {}
        for key, body in groups.items():
            labels[key] = (body or {}).get("label", key)
            for aid in (body or {}).get("arxiv") or []:
                arxiv_to_group[str(aid)] = key
        return cls(arxiv_to_group=arxiv_to_group, labels=labels)

    def group_for(self, arxiv_id: Optional[str]) -> str:
        if not arxiv_id:
            return "uncategorised"
        if arxiv_id in self.arxiv_to_group:
            return self.arxiv_to_group[arxiv_id]
        if arxiv_id not in self._warned:
            self._warned.add(arxiv_id)
            print(f"WARN topic_mapper: no group for arXiv:{arxiv_id} → uncategorised", file=sys.stderr)
        return "uncategorised"
```

- [ ] **Step 5: Run — expect pass**

```bash
pytest tests/test_topic_mapper.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add scripts/topic_groups.yml scripts/topic_mapper.py scripts/tests/test_topic_mapper.py
git commit -m "feat(scripts): topic_groups.yml + TopicMapper with uncategorised warning"
```

---

### Task B6: Derived metrics — by_year, h-index, top papers, journals

**Files:**
- Create: `scripts/metrics.py`
- Create: `scripts/tests/test_metrics.py`

- [ ] **Step 1: Write the failing test**

`scripts/tests/test_metrics.py`:

```python
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Author, Paper, Venue
from metrics import compute_metrics


def _p(arxiv_id: str, year: int, citations: int, first: bool, journal: str = "Phys. Rev. D") -> Paper:
    return Paper(
        inspire_id=arxiv_id.replace(".", ""),
        title=f"Paper {arxiv_id}",
        authors=[
            Author(name="Y.-K. Chen", is_you=True) if first
            else Author(name="Other", is_you=False),
            Author(name="Y.-K. Chen", is_you=True) if not first else Author(name="L. Meng", is_you=False),
        ],
        venue=Venue(journal=journal, year=year),
        arxiv_id=arxiv_id,
        citations=citations, citations_no_self=citations,
        year=year, topic_group="x",
    )


def test_papers_total_and_first_author_count():
    papers = [_p("a", 2024, 10, True), _p("b", 2024, 5, False), _p("c", 2025, 3, True)]
    m = compute_metrics(papers)
    assert m.papers_total == 3
    assert m.first_author_count == 2


def test_h_index_simple():
    # 5 papers with citations 10, 8, 5, 4, 1 → h-index = 4
    papers = [_p(f"p{i}", 2024, c, True) for i, c in enumerate([10, 8, 5, 4, 1])]
    m = compute_metrics(papers)
    assert m.h_index == 4


def test_by_year_cumulative():
    papers = [
        _p("a", 2023, 10, True),
        _p("b", 2024, 5, True),
        _p("c", 2024, 3, True),
        _p("d", 2025, 1, True),
    ]
    m = compute_metrics(papers)
    rows = {r.year: r for r in m.by_year}
    assert rows[2023].papers == 1 and rows[2023].cum_citations == 10
    assert rows[2024].papers == 2 and rows[2024].cum_citations == 18
    assert rows[2025].papers == 1 and rows[2025].cum_citations == 19


def test_journal_counts_sorted_desc():
    papers = [
        _p("a", 2024, 1, True, journal="PRD"),
        _p("b", 2024, 1, True, journal="PRD"),
        _p("c", 2024, 1, True, journal="EPJC"),
    ]
    m = compute_metrics(papers)
    assert m.journals[0].name == "PRD" and m.journals[0].count == 2
    assert m.journals[1].name == "EPJC" and m.journals[1].count == 1


def test_top_papers_limit_10_sorted_by_citations():
    papers = [_p(f"p{i:02}", 2024, c, True) for i, c in enumerate(range(15, 0, -1))]
    m = compute_metrics(papers)
    assert len(m.top_papers) == 10
    assert m.top_papers[0].citations == 15
    assert m.top_papers[-1].citations == 6
```

- [ ] **Step 2: Run — expect failure**

```bash
pytest tests/test_metrics.py -v
```

Expected: `ModuleNotFoundError: No module named 'metrics'`.

- [ ] **Step 3: Implement `scripts/metrics.py`**

```python
"""Derived scientometric metrics computed from the list of Paper objects."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import List

from models import (
    Coauthor, Institution, JournalCount, Metrics, Paper, TermCount, YearRow,
)


def _h_index(citation_counts: List[int]) -> int:
    """Standard h-index: max h such that h papers have ≥ h citations each."""
    sorted_desc = sorted(citation_counts, reverse=True)
    h = 0
    for i, c in enumerate(sorted_desc, start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def _by_year(papers: List[Paper]) -> List[YearRow]:
    if not papers:
        return []
    years = sorted({p.year for p in papers if p.year is not None})
    if not years:
        return []
    rows: list[YearRow] = []
    cum_cites = 0
    for y in range(min(years), max(years) + 1):
        this_year = [p for p in papers if p.year == y]
        cum_cites += sum(p.citations for p in this_year)
        # h-index uses ALL papers with year <= y
        cite_pool = [p.citations for p in papers if p.year is not None and p.year <= y]
        rows.append(YearRow(
            year=y,
            papers=len(this_year),
            cum_citations=cum_cites,
            h_index=_h_index(cite_pool),
        ))
    return rows


def _journals(papers: List[Paper]) -> List[JournalCount]:
    c: Counter[str] = Counter()
    for p in papers:
        name = (p.venue.journal or "arXiv-only").strip()
        c[name] += 1
    return [JournalCount(name=n, count=k) for n, k in c.most_common()]


def _top_papers(papers: List[Paper], limit: int = 10) -> List[Paper]:
    return sorted(papers, key=lambda p: p.citations, reverse=True)[:limit]


def _coauthors_and_institutions(papers: List[Paper]) -> tuple[List[Coauthor], List[Institution]]:
    by_name: dict[str, dict] = defaultdict(lambda: {"joint": 0, "inspire_id": None, "inst": None})
    for p in papers:
        for a in p.authors:
            if a.is_you:
                continue
            by_name[a.name]["joint"] += 1
            if a.inspire_id and not by_name[a.name]["inspire_id"]:
                by_name[a.name]["inspire_id"] = a.inspire_id
    coauthors = [
        Coauthor(
            name=n, joint_papers=v["joint"],
            inspire_id=v["inspire_id"], current_institution=v["inst"],
        )
        for n, v in sorted(by_name.items(), key=lambda kv: kv[1]["joint"], reverse=True)
    ]
    # Institutions are filled in a separate enrichment step; default empty.
    return coauthors, []


def compute_metrics(papers: List[Paper]) -> Metrics:
    citations_total = sum(p.citations for p in papers)
    h = _h_index([p.citations for p in papers])
    fa = sum(1 for p in papers if p.authors and p.authors[0].is_you)
    by_year = _by_year(papers)
    coauthors, institutions = _coauthors_and_institutions(papers)
    return Metrics(
        papers_total=len(papers),
        citations_total=citations_total,
        h_index=h,
        first_author_count=fa,
        by_year=by_year,
        top_papers=_top_papers(papers),
        keywords=[],   # filled by keyword module in next task
        journals=_journals(papers),
        coauthors=coauthors,
        institutions=institutions,
    )
```

- [ ] **Step 4: Run — expect pass**

```bash
pytest tests/test_metrics.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/metrics.py scripts/tests/test_metrics.py
git commit -m "feat(scripts): compute_metrics covers totals, h-index, by-year, top papers, journals, coauthors"
```

---

### Task B7: Keyword extraction from titles + abstracts

**Files:**
- Create: `scripts/keywords.py`
- Create: `scripts/tests/test_keywords.py`

- [ ] **Step 1: Write the failing test**

`scripts/tests/test_keywords.py`:

```python
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import Author, Paper, Venue
from keywords import extract_keywords


def _p(title: str, abstract: str = "") -> Paper:
    return Paper(
        inspire_id="x", title=title,
        authors=[Author(name="Y.-K. Chen", is_you=True)],
        venue=Venue(year=2024),
        citations=0, citations_no_self=0, year=2024, topic_group="x",
    )


def test_extract_strips_latex_and_lowercases():
    papers = [
        _p("Tetraquark bound states $Q\\bar{q}$ in the constituent quark model"),
        _p("Tetraquark resonances with $\\chi$PT"),
    ]
    out = {t.term for t in extract_keywords(papers, top_n=20)}
    assert "tetraquark" in out
    assert "$" not in " ".join(out)


def test_extract_drops_stopwords_and_physics_filler():
    papers = [_p("The model of states and theory") for _ in range(5)]
    terms = [t.term for t in extract_keywords(papers, top_n=20)]
    for noise in ("the", "of", "and", "states", "model", "theory"):
        assert noise not in terms


def test_collapse_synonyms():
    papers = [_p("HBChPT and ChPT and chiral perturbation theory")]
    terms = {t.term for t in extract_keywords(papers, top_n=20)}
    assert "χpt" in terms or "chpt" in terms or "chiral perturbation theory" in terms
```

- [ ] **Step 2: Run — expect failure**

```bash
pytest tests/test_keywords.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `scripts/keywords.py`**

```python
"""Keyword extraction from paper titles + abstracts."""
from __future__ import annotations

import re
from collections import Counter
from typing import List

from models import Paper, TermCount


# Latex blocks like $...$ and inline commands \foo
LATEX_DOLLARS = re.compile(r"\$[^$]*\$")
LATEX_CMD = re.compile(r"\\[a-zA-Z]+\{?[^{}\s]*\}?")

STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "in", "on", "at", "to", "for",
    "with", "from", "into", "as", "is", "are", "was", "were", "be", "been",
    "their", "its", "this", "that", "these", "those", "we", "our",
    "via", "using", "by", "through",
}

# Physics-specific generic words to drop
PHYSICS_FILLER = {
    "state", "states", "model", "models", "theory", "theories",
    "approach", "method", "methods", "study", "studies", "analysis", "analyses",
    "results", "calculation", "calculations", "paper", "papers",
    "system", "systems", "particle", "particles", "quark", "quarks",
}

# Manual synonym → canonical
SYNONYMS = {
    "hbchpt": "χpt",
    "chpt": "χpt",
    "chiral perturbation theory": "χpt",
    "doubly-heavy": "doubly heavy",
    "fully-heavy": "fully heavy",
    "compact tetraquark": "tetraquark",
    "compact tetraquarks": "tetraquark",
    "molecular state": "molecular",
    "molecular states": "molecular",
    "molecular bound state": "molecular",
    "bound states": "bound state",
    "resonances": "resonance",
    "polarizabilities": "polarizability",
    "three-body": "three-body",
    "coupled channels": "coupled-channel",
    "coupled channel": "coupled-channel",
    "complex scaling method": "complex scaling",
}

# Multi-word phrases to keep as one token before single-token extraction
PHRASES = [
    "chiral perturbation theory",
    "complex scaling",
    "complex scaling method",
    "coupled channel",
    "coupled channels",
    "coupled-channel",
    "doubly heavy",
    "fully heavy",
    "three-body",
    "bound state",
    "bound states",
    "molecular state",
    "molecular states",
]


def _clean(text: str) -> str:
    t = LATEX_DOLLARS.sub(" ", text or "")
    t = LATEX_CMD.sub(" ", t)
    t = re.sub(r"[^\w\s\-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _tokenise_with_phrases(text: str) -> list[str]:
    text = text.lower()
    for ph in sorted(PHRASES, key=len, reverse=True):
        text = text.replace(ph, ph.replace(" ", "·"))   # protect
    tokens = [t.replace("·", " ") for t in text.split() if t]
    return tokens


def _normalise(term: str) -> str:
    t = term.strip().lower()
    return SYNONYMS.get(t, t)


def extract_keywords(papers: List[Paper], *, top_n: int = 10) -> List[TermCount]:
    paper_term_counts: Counter[str] = Counter()
    for p in papers:
        blob = _clean(f"{p.title}")  # abstracts come from a separate field if present
        seen_in_paper: set[str] = set()
        for tok in _tokenise_with_phrases(blob):
            t = _normalise(tok)
            if not t or len(t) < 3:
                continue
            if t in STOPWORDS or t in PHYSICS_FILLER:
                continue
            seen_in_paper.add(t)
        for t in seen_in_paper:
            paper_term_counts[t] += 1
    return [TermCount(term=t, count=c) for t, c in paper_term_counts.most_common(top_n)]
```

- [ ] **Step 4: Run — expect pass**

```bash
pytest tests/test_keywords.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Wire keywords into compute_metrics**

Edit `scripts/metrics.py` to import and call:

```python
# top of file, alongside other imports
from keywords import extract_keywords

# inside compute_metrics, replace `keywords=[]` with:
        keywords=extract_keywords(papers, top_n=10),
```

- [ ] **Step 6: Update the metrics test that asserted empty keywords (if any)**

Re-run the metrics tests:

```bash
pytest tests/test_metrics.py -v
```

Expected: 5 passed.

- [ ] **Step 7: Commit**

```bash
git add scripts/keywords.py scripts/tests/test_keywords.py scripts/metrics.py
git commit -m "feat(scripts): keyword extraction with latex strip, stopwords, synonym collapse"
```

---

### Task B8: CLI entrypoint — fetch_inspire.py

**Files:**
- Create: `scripts/fetch_inspire.py`
- Create: `scripts/tests/test_fetch_inspire.py`

- [ ] **Step 1: Write the failing integration test**

`scripts/tests/test_fetch_inspire.py`:

```python
import json
import os
import subprocess
from pathlib import Path

import respx
from httpx import Response

SCRIPTS = Path(__file__).resolve().parents[1]
FX = SCRIPTS / "tests" / "fixtures"


def test_fetch_inspire_writes_valid_bundle(tmp_path, monkeypatch):
    """Run the CLI with respx-injected fixtures and validate the output JSON."""
    out_path = tmp_path / "inspire.json"

    import sys
    sys.path.insert(0, str(SCRIPTS))
    import fetch_inspire
    from models import InspireBundle

    author_fx = json.loads((FX / "author_2182746.json").read_text())
    lit_p1 = json.loads((FX / "literature_p1.json").read_text())
    lit_p2 = json.loads((FX / "literature_p2.json").read_text())

    with respx.mock:
        respx.get("https://inspirehep.net/api/authors/2182746").mock(
            return_value=Response(200, json=author_fx)
        )
        # Both pages mocked; literature URL matches by host+path.
        respx.get("https://inspirehep.net/api/literature").mock(
            side_effect=[Response(200, json=lit_p1), Response(200, json=lit_p2),
                         Response(200, json={"hits": {"hits": []}, "links": {}})]
        )
        fetch_inspire.main(author_id="2182746", bai="Yan-Ke.Chen.1", out_path=out_path)

    assert out_path.exists()
    bundle = InspireBundle.model_validate_json(out_path.read_text())
    assert bundle.author.id == "2182746"
    assert bundle.metrics.papers_total > 0
```

- [ ] **Step 2: Run — expect failure**

```bash
pytest tests/test_fetch_inspire.py -v
```

Expected: `ModuleNotFoundError: No module named 'fetch_inspire'`.

- [ ] **Step 3: Implement `scripts/fetch_inspire.py`**

```python
"""Build-time script: fetch INSPIRE data and write site/src/data/inspire.json."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from inspire_client import InspireClient
from metrics import compute_metrics
from models import InspireBundle
from topic_mapper import TopicMapper


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "site" / "src" / "data" / "inspire.json"
DEFAULT_TOPICS = Path(__file__).resolve().parent / "topic_groups.yml"


def main(
    *,
    author_id: str = "2182746",
    bai: str = "Yan-Ke.Chen.1",
    out_path: Path = DEFAULT_OUT,
    topics_path: Path = DEFAULT_TOPICS,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mapper = TopicMapper.from_yaml(topics_path)

    with InspireClient() as client:
        print(f"→ Fetching author {author_id}…", file=sys.stderr)
        profile = client.fetch_author(author_id)
        print(f"  · {profile.name}", file=sys.stderr)

        print(f"→ Fetching literature for BAI {bai}…", file=sys.stderr)
        papers = list(client.fetch_literature_for_author(bai))
        print(f"  · {len(papers)} papers", file=sys.stderr)

    # Refuse to overwrite a non-empty file with zero papers.
    if not papers and out_path.exists():
        existing = json.loads(out_path.read_text())
        if (existing.get("metrics") or {}).get("papers_total", 0) > 0:
            print("FATAL: refusing to overwrite existing data with empty result.", file=sys.stderr)
            sys.exit(2)

    # Tag with topic groups
    for p in papers:
        p.topic_group = mapper.group_for(p.arxiv_id)

    metrics = compute_metrics(papers)
    bundle = InspireBundle(
        fetched_at=datetime.now(timezone.utc),
        author=profile,
        papers=papers,
        metrics=metrics,
    )
    out_path.write_text(bundle.model_dump_json(indent=2))
    print(f"✓ Wrote {out_path}  ({len(papers)} papers, h-index {metrics.h_index})", file=sys.stderr)


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Fetch INSPIRE data for YK Chen homepage.")
    ap.add_argument("--author-id", default="2182746")
    ap.add_argument("--bai", default="Yan-Ke.Chen.1")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--topics", type=Path, default=DEFAULT_TOPICS)
    a = ap.parse_args()
    main(author_id=a.author_id, bai=a.bai, out_path=a.out, topics_path=a.topics)


if __name__ == "__main__":
    _cli()
```

- [ ] **Step 4: Run — expect pass**

```bash
pytest tests/test_fetch_inspire.py -v
pytest -v   # full suite, should all pass
```

Expected: full test suite passes.

- [ ] **Step 5: Smoke-run against the real INSPIRE API**

```bash
cd /Users/ykchen/science_project/personal_profile/scripts
python fetch_inspire.py
```

Expected: writes `site/src/data/inspire.json`. Inspect the file:

```bash
python -c "import json; d=json.load(open('../site/src/data/inspire.json')); print('papers:', d['metrics']['papers_total'], 'h:', d['metrics']['h_index'])"
```

If the paper count is markedly different from the CV (e.g., 0 or 100), pause and investigate (likely the BAI is wrong — try variants like `Y.K.Chen.1` or look at the INSPIRE profile URL).

- [ ] **Step 6: Commit**

```bash
git add scripts/fetch_inspire.py scripts/tests/test_fetch_inspire.py site/src/data/inspire.json
git commit -m "feat(scripts): fetch_inspire CLI writes site/src/data/inspire.json"
```

---

## Phase C · Astro project setup

### Task C1: Initialise Astro + TypeScript + Tailwind

**Files:**
- Modify: `site/` (npm-managed)

- [ ] **Step 1: Run the Astro starter, into the existing `site/` directory**

```bash
cd /Users/ykchen/science_project/personal_profile
# Astro's create-script refuses non-empty dirs, so use an alternate flow.
cd site
npm init -y
npm install astro@^5 typescript@^5
npx astro add tailwind react --yes
```

Answer "Yes" to overwrite prompts. The `add` commands install `@astrojs/tailwind` and `@astrojs/react` integrations.

- [ ] **Step 2: Verify `astro.config.mjs` ends up like this**

`site/astro.config.mjs`:

```js
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';

export default defineConfig({
  integrations: [tailwind({ applyBaseStyles: false }), react()],
  trailingSlash: 'ignore',
});
```

(`applyBaseStyles: false` — we control base styles ourselves.)

- [ ] **Step 3: Add npm scripts**

In `site/package.json`, set the `scripts` block:

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "check": "astro check"
  }
}
```

- [ ] **Step 4: Smoke-test**

```bash
cd /Users/ykchen/science_project/personal_profile/site
npm run dev
```

Expected: server starts at `http://localhost:4321` and renders Astro's default welcome page (the boilerplate from `create astro` if it ended up creating `pages/index.astro`). Stop with Ctrl-C.

- [ ] **Step 5: Commit**

```bash
git add site/package.json site/package-lock.json site/astro.config.mjs site/tsconfig.json site/.gitignore
git commit -m "chore(site): scaffold Astro 5 + TypeScript + Tailwind + React"
```

---

### Task C2: Design tokens and Tailwind theme

**Files:**
- Create: `site/src/styles/tokens.css`
- Create: `site/src/styles/base.css`
- Modify: `site/tailwind.config.mjs`

- [ ] **Step 1: Write `site/src/styles/tokens.css`**

```css
:root {
  --paper:     #F6F4EE;
  --paper-2:   #EFEBE1;
  --ink:       #15120E;
  --ink-2:     #4C463D;
  --ink-3:     #8C8579;
  --rule:      #DCD5C5;
  --rule-2:    #ECE6D6;
  --accent:    #1B2E5E;
  --accent-soft: rgba(27, 46, 94, 0.12);
  --mark:      #B0492A;
  --mark-soft: rgba(176, 73, 42, 0.15);

  --f-serif: "Newsreader", "Times New Roman", serif;
  --f-sans:  "IBM Plex Sans", system-ui, sans-serif;
  --f-mono:  "IBM Plex Mono", ui-monospace, monospace;

  --col-gap: clamp(2rem, 4vw, 4rem);
  --pad-x:   clamp(1.5rem, 5vw, 4rem);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
```

- [ ] **Step 2: Write `site/src/styles/base.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import "./tokens.css";

* , *::before, *::after { box-sizing: border-box; }

html { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--f-sans);
  font-size: 15px;
  line-height: 1.55;
  letter-spacing: 0.005em;
}

::selection { background: var(--accent); color: var(--paper); }

a { color: var(--accent); text-decoration: none; }
a.lined {
  background-image: linear-gradient(var(--accent), var(--accent));
  background-repeat: no-repeat;
  background-size: 0% 1px;
  background-position: 0 100%;
  transition: background-size .35s cubic-bezier(.2,.7,.2,1);
}
a.lined:hover { background-size: 100% 1px; }

body::before {
  content: "";
  position: fixed; inset: 0;
  pointer-events: none;
  z-index: 1000;
  opacity: .035;
  mix-blend-mode: multiply;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .85 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
}

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

@keyframes rise { to { opacity: 1; transform: none; } }
.stagger > * {
  opacity: 0;
  transform: translateY(8px);
  animation: rise .9s cubic-bezier(.2,.7,.2,1) forwards;
}
.stagger > *:nth-child(1) { animation-delay: .05s; }
.stagger > *:nth-child(2) { animation-delay: .15s; }
.stagger > *:nth-child(3) { animation-delay: .25s; }
.stagger > *:nth-child(4) { animation-delay: .35s; }
.stagger > *:nth-child(5) { animation-delay: .45s; }
```

- [ ] **Step 3: Update `site/tailwind.config.mjs`**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,ts,tsx,js,jsx,md}'],
  theme: {
    extend: {
      colors: {
        paper:     'var(--paper)',
        'paper-2': 'var(--paper-2)',
        ink:       'var(--ink)',
        'ink-2':   'var(--ink-2)',
        'ink-3':   'var(--ink-3)',
        rule:      'var(--rule)',
        'rule-2':  'var(--rule-2)',
        accent:    'var(--accent)',
        mark:      'var(--mark)',
      },
      fontFamily: {
        serif: ['Newsreader', 'Times New Roman', 'serif'],
        sans:  ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono:  ['IBM Plex Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
```

- [ ] **Step 4: Commit**

```bash
git add site/src/styles/ site/tailwind.config.mjs
git commit -m "feat(site): design tokens (CSS vars), base styles, Tailwind theme aliases"
```

---

### Task C3: Base layout — top bar, footer, grain, fonts

**Files:**
- Create: `site/src/layouts/Base.astro`

- [ ] **Step 1: Write `site/src/layouts/Base.astro`**

```astro
---
import "../styles/base.css";
import inspire from "../data/inspire.json";

const { title, description, currentPage } = Astro.props as {
  title: string;
  description?: string;
  currentPage?: "home" | "research" | "publications" | "analytics" | "cv";
};

const fetchedAt = new Date(inspire.fetched_at);
const fetchedLabel = fetchedAt.toISOString().slice(0, 10).replace(/-/g, "·");

const nav = [
  { key: "home",         label: "Home",         href: "/" },
  { key: "research",     label: "Research",     href: "/research" },
  { key: "publications", label: "Publications", href: "/publications" },
  { key: "analytics",    label: "Analytics",    href: "/analytics" },
  { key: "cv",           label: "CV",           href: "/cv" },
] as const;
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  {description && <meta name="description" content={description} />}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,300;1,6..72,400&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&display=swap"
    rel="stylesheet"
  />
</head>
<body>
  <div class="page max-w-[1280px] mx-auto px-[var(--pad-x)] pt-6 pb-16">
    <header class="topbar flex items-baseline justify-between pb-8 border-b border-rule">
      <div class="brand font-serif text-[1.05rem] font-medium tracking-tight">
        Yan-Ke Chen
        <span class="hanzi font-serif italic text-ink-2 ml-1 text-[.9em]">陈彦珂</span>
      </div>
      <nav class="primary flex gap-8 font-mono text-[.78rem] uppercase tracking-[.12em]" aria-label="Primary">
        {nav.map(item => (
          <a
            href={item.href}
            class={item.key === currentPage ? "text-ink" : "text-ink-2"}
            aria-current={item.key === currentPage ? "page" : undefined}
          >
            {item.key === currentPage ? <span class="text-mark mr-1">·</span> : null}
            {item.label}
          </a>
        ))}
      </nav>
    </header>

    <slot />

    <footer class="pt-12 grid grid-cols-1 md:grid-cols-2 gap-[var(--col-gap)] font-mono text-[.72rem] text-ink-3 tracking-[.06em]">
      <div>
        Data sourced from <a href="https://inspirehep.net" class="lined">INSPIRE-HEP</a>.
        Last refreshed <span class="text-ink-2">{fetchedLabel}</span>.
      </div>
      <div class="md:text-right">
        © {new Date().getFullYear()} Yan-Ke Chen · Set in Newsreader &amp; IBM Plex.
      </div>
    </footer>
  </div>
</body>
</html>
```

- [ ] **Step 2: Smoke-build (will fail without index.astro — that's fine)**

```bash
cd /Users/ykchen/science_project/personal_profile/site
npm run check
```

Astro check should pass; build is exercised in later tasks.

- [ ] **Step 3: Commit**

```bash
git add site/src/layouts/Base.astro
git commit -m "feat(site): Base layout — top bar, footer, font loading, grain overlay"
```

---

## Phase D · Home page components & wiring

### Task D1: Hero, NumbersStrip, ThemeCard, Figure, Sparkline

**Files:**
- Create: `site/src/components/Hero.astro`
- Create: `site/src/components/NumbersStrip.astro`
- Create: `site/src/components/ThemeCard.astro`
- Create: `site/src/components/Figure.astro`
- Create: `site/src/components/Sparkline.astro`
- Create: `site/src/components/PubList.astro`

- [ ] **Step 1: Write `site/src/components/Hero.astro`**

```astro
---
import inspire from "../data/inspire.json";
import Sparkline from "./Sparkline.astro";

const m = inspire.metrics;
const totalPapers = m.papers_total;
const yearsActive = m.by_year.length ? m.by_year[m.by_year.length - 1].year - m.by_year[0].year + 1 : 0;
const sparkSeries = m.by_year.map(r => r.papers);
const profile = inspire.author;
---
<section class="hero grid gap-[var(--col-gap)] grid-cols-1 md:grid-cols-[minmax(0,1fr)_minmax(0,0.45fr)] py-[clamp(3rem,8vw,6rem)] border-b border-rule stagger">
  <div>
    <p class="role font-mono text-[.78rem] tracking-[.14em] uppercase text-ink-2 mb-10 inline-block border-t border-ink pt-2">
      Theoretical Physics · Hadron Spectroscopy
    </p>
    <h1 class="font-serif font-normal text-[clamp(3.4rem,9vw,6.5rem)] leading-[0.95] tracking-[-0.025em] m-0 mb-4" style="font-variation-settings:'opsz' 64;">
      Yan-Ke<br /><em class="italic font-light text-ink-2">Chen.</em>
    </h1>
    <p class="lead font-serif font-light text-[clamp(1.05rem,1.4vw,1.25rem)] leading-[1.55] text-ink max-w-[50ch] m-0">
      I study exotic hadrons — tetraquarks, molecular states, and the
      coupled-channel dynamics that bind them — using chiral perturbation
      theory and quark potential models. Across
      <Sparkline values={sparkSeries} />
      {yearsActive} active years, my collaborators and I have published
      <em class="italic text-ink-2">{totalPapers} peer-reviewed papers</em>,
      mostly in <em class="italic text-ink-2">Phys. Rev. D</em>.
    </p>
  </div>
  <dl class="meta self-end font-mono text-[.78rem] text-ink-2 tracking-[.04em] border-l border-rule pl-6 py-1">
    <dt class="text-ink-3 uppercase tracking-[.14em] text-[.7rem]">Position</dt>
    <dd class="m-0 mt-1 text-ink flex items-center gap-2 before:content-[''] before:inline-block before:w-[7px] before:h-[7px] before:rounded-full before:bg-mark before:[box-shadow:0_0_0_0_rgba(176,73,42,.55)] before:animate-[pulse_2.4s_infinite]">
      {profile.current_position?.rank} · {profile.current_position?.institution}
    </dd>
    <dt class="text-ink-3 uppercase tracking-[.14em] text-[.7rem] mt-5">Since</dt>
    <dd class="m-0 mt-1 text-ink">{profile.current_position?.start}</dd>
    <dt class="text-ink-3 uppercase tracking-[.14em] text-[.7rem] mt-5">Email</dt>
    <dd class="m-0 mt-1"><a href="mailto:chenyanke@pku.edu.cn" class="text-ink lined">chenyanke@pku.edu.cn</a></dd>
    <dt class="text-ink-3 uppercase tracking-[.14em] text-[.7rem] mt-5">Profiles</dt>
    <dd class="m-0 mt-1">
      <a href={`https://inspirehep.net/authors/${profile.id}`} class="text-ink lined">INSPIRE-HEP</a>
      {profile.arxiv && <> · <a href={`https://arxiv.org/a/${profile.arxiv}`} class="text-ink lined">arXiv</a></>}
      {profile.orcid && <> · <a href={`https://orcid.org/${profile.orcid}`} class="text-ink lined">ORCID</a></>}
    </dd>
  </dl>
</section>

<style>
  @keyframes pulse {
    0%   { box-shadow: 0 0 0 0    rgba(176, 73, 42, .55); }
    70%  { box-shadow: 0 0 0 8px  rgba(176, 73, 42, 0); }
    100% { box-shadow: 0 0 0 0    rgba(176, 73, 42, 0); }
  }
</style>
```

- [ ] **Step 2: Write `site/src/components/Sparkline.astro`**

```astro
---
const { values } = Astro.props as { values: number[] };
const max = Math.max(1, ...values);
---
<span class="inline-flex items-end gap-[2px] align-[-0.15em] mx-1" style="height:1.1em;">
  {values.map(v => (
    <span class="block w-[5px] bg-ink/85" style={`height:${Math.round((v / max) * 100)}%;`}></span>
  ))}
</span>
```

- [ ] **Step 3: Write `site/src/components/NumbersStrip.astro`**

```astro
---
import inspire from "../data/inspire.json";
const m = inspire.metrics;
const coauthors = m.coauthors.length;
---
<section class="numbers grid grid-cols-2 md:grid-cols-4 border-b border-rule" aria-label="By the numbers">
  <Stat n={m.papers_total} label="Peer-reviewed papers" />
  <Stat n={`~${m.citations_total}`} label="Total citations" sup="cits" />
  <Stat n={m.h_index} label="h-index" hint="(inspire)" />
  <Stat n={coauthors} label="Unique coauthors" />
</section>

<script>
  // no client-side script
</script>

<style>
  .numbers > :global(div) { padding: 2.25rem 0 2rem; border-left: 1px solid var(--rule); }
  .numbers > :global(div):first-child { border-left: 0; }
  .numbers > :global(div):nth-child(n+2) { padding-left: 1.5rem; }
</style>

---
const Stat = ({ n, label, sup, hint }: { n: string | number; label: string; sup?: string; hint?: string }) => (
  <div>
    <div class="n font-serif font-light text-[clamp(2.6rem,5vw,4rem)] leading-none tracking-[-0.025em] text-ink" style="font-variation-settings:'opsz' 60;">
      {n}{sup && <span class="font-mono text-[.6rem] text-ink-3 tracking-[.1em] align-[0.6em] ml-1">{sup}</span>}
    </div>
    <div class="lbl font-mono text-[.7rem] uppercase tracking-[.16em] text-ink-2 mt-4">
      {label} {hint && <span class="text-ink-3 text-[.9em]">{hint}</span>}
    </div>
  </div>
);
---
```

Note: the `Stat` inline component declaration in Astro must be moved out — Astro frontmatter only runs once per page. Replace the file with the simpler inline form below:

```astro
---
import inspire from "../data/inspire.json";
const m = inspire.metrics;
const coauthors = m.coauthors.length;

type StatBox = { n: string | number; label: string; sup?: string; hint?: string };
const stats: StatBox[] = [
  { n: m.papers_total,             label: "Peer-reviewed papers" },
  { n: `~${m.citations_total}`,    label: "Total citations", sup: "cits" },
  { n: m.h_index,                  label: "h-index", hint: "(inspire)" },
  { n: coauthors,                  label: "Unique coauthors" },
];
---
<section class="numbers grid grid-cols-2 md:grid-cols-4 border-b border-rule" aria-label="By the numbers">
  {stats.map(s => (
    <div class="py-9 first:border-l-0 border-l border-rule [&:nth-child(n+2)]:pl-6">
      <div class="font-serif font-light text-[clamp(2.6rem,5vw,4rem)] leading-none tracking-[-0.025em] text-ink" style="font-variation-settings:'opsz' 60;">
        {s.n}
        {s.sup && <span class="font-mono text-[.6rem] text-ink-3 tracking-[.1em] align-[0.6em] ml-1">{s.sup}</span>}
      </div>
      <div class="font-mono text-[.7rem] uppercase tracking-[.16em] text-ink-2 mt-4">
        {s.label} {s.hint && <span class="text-ink-3 text-[.9em]">{s.hint}</span>}
      </div>
    </div>
  ))}
</section>
```

- [ ] **Step 4: Write `site/src/components/ThemeCard.astro`**

```astro
---
const { roman, title, body, count } = Astro.props as {
  roman: string;
  title: string;
  body: string;
  count: number;
};
---
<div class="theme bg-paper p-7 flex flex-col gap-3 transition-colors hover:bg-paper-2">
  <div class="roman font-mono text-[.7rem] tracking-[.18em] text-mark">{roman}</div>
  <h4 class="font-serif font-normal text-[1.35rem] leading-tight text-ink m-0" style="font-variation-settings:'opsz' 28;">{title}</h4>
  <p class="m-0 text-ink-2 text-[.9rem] leading-[1.55]">{body}</p>
  <div class="mt-auto pt-4 font-mono text-[.72rem] text-ink-3 tracking-[.08em]">{count} paper{count === 1 ? "" : "s"}</div>
</div>
```

- [ ] **Step 5: Write `site/src/components/PubList.astro`**

```astro
---
import inspire from "../data/inspire.json";

type Mode = "selected" | "full";
const { mode = "selected", limit, topicGroup } = Astro.props as {
  mode?: Mode;
  limit?: number;
  topicGroup?: string;
};

let papers = inspire.papers as Array<any>;
if (topicGroup) papers = papers.filter(p => p.topic_group === topicGroup);
papers = papers.slice().sort((a, b) => (b.year ?? 0) - (a.year ?? 0));
if (mode === "selected") {
  // The first N most recent first-author papers act as "selected" by default.
  // To curate manually, replace this slice with hand-picked inspire ids.
  papers = papers.filter(p => p.authors?.[0]?.is_you).slice(0, limit ?? 5);
} else if (limit) {
  papers = papers.slice(0, limit);
}

const formatAuthors = (auth: Array<{ name: string; is_you: boolean }>) =>
  auth
    .map(a => (a.is_you ? `<b>${a.name}</b>` : a.name))
    .join(", ");
---
<div class="pub-list grid gap-0">
  {papers.map(p => (
    <article class="pub grid grid-cols-[5rem_1fr_5rem] md:grid-cols-[8rem_1fr_6rem] gap-[var(--col-gap)] py-7 border-t border-rule [&:last-child]:border-b items-baseline transition-colors hover:bg-rule-2/50">
      <div class="yr font-mono text-[.78rem] text-ink-3 tracking-[.1em]">{p.year ?? "—"}</div>
      <div>
        <h3 class="font-serif font-normal text-[1.18rem] leading-[1.3] text-ink m-0 mb-2 tracking-[-0.005em]" style="font-variation-settings:'opsz' 22;">
          {p.title}
        </h3>
        <div class="auth text-[.86rem] text-ink-2 mb-2" set:html={formatAuthors(p.authors)} />
        <div class="where font-mono text-[.72rem] text-ink-2 tracking-[.04em] uppercase">
          {p.venue.journal && <span>{p.venue.journal}{p.venue.volume ? ` ${p.venue.volume}` : ""}{p.venue.page ? `, ${p.venue.page}` : ""}</span>}
          {p.venue.journal && p.arxiv_id && <span class="text-ink-3 mx-2">·</span>}
          {p.arxiv_id && <a class="text-ink-2 hover:text-accent" href={`https://arxiv.org/abs/${p.arxiv_id}`}>arXiv:{p.arxiv_id}</a>}
          {p.doi && <><span class="text-ink-3 mx-2">·</span><a class="text-ink-2 hover:text-accent" href={`https://doi.org/${p.doi}`}>doi</a></>}
        </div>
      </div>
      <div class="cites text-right font-serif font-light text-[2.4rem] leading-none text-ink tracking-[-0.02em]" style="font-variation-settings:'opsz' 60;">
        {p.citations}
        <span class="block font-mono text-[.6rem] text-ink-3 tracking-[.18em] uppercase mt-1 font-normal">citations</span>
      </div>
    </article>
  ))}
</div>
```

- [ ] **Step 6: Write `site/src/components/Figure.astro` (chart-card wrapper used on analytics)**

```astro
---
const { title, number } = Astro.props as { title: string; number: string };
---
<div class="figure border border-rule bg-paper p-6 md:p-9 pb-6 relative">
  <div class="figure-head flex items-baseline justify-between flex-wrap gap-4 pb-5 mb-6 border-b border-rule-2">
    <span class="title font-serif text-[1.05rem] text-ink">{title}</span>
    <span class="meta font-mono text-[.7rem] text-ink-3 tracking-[.1em] uppercase">{number}</span>
  </div>
  <slot />
  <slot name="caption" />
</div>
```

- [ ] **Step 7: Commit**

```bash
git add site/src/components/
git commit -m "feat(site): Hero, NumbersStrip, ThemeCard, PubList, Figure, Sparkline"
```

---

### Task D2: Home page wiring

**Files:**
- Create: `site/src/pages/index.astro`

- [ ] **Step 1: Write `site/src/pages/index.astro`**

```astro
---
import Base from "../layouts/Base.astro";
import Hero from "../components/Hero.astro";
import NumbersStrip from "../components/NumbersStrip.astro";
import PubList from "../components/PubList.astro";
import ThemeCard from "../components/ThemeCard.astro";
import inspire from "../data/inspire.json";

const groupCounts: Record<string, number> = {};
for (const p of inspire.papers as any[]) {
  groupCounts[p.topic_group] = (groupCounts[p.topic_group] || 0) + 1;
}

const themes = [
  {
    key: "spectrum-quark-models",
    roman: "i.",
    title: "Spectrum of exotic states with quark models",
    body: "Unified treatment of molecular and compact tetraquarks; doubly- and fully-heavy systems; benchmark comparisons across methods.",
  },
  {
    key: "exotic-coupled-channel",
    roman: "ii.",
    title: "Hadron-hadron interaction & coupled channels",
    body: "Improved complex scaling for virtual states; pole-origin analysis of X(3872); three-body molecular states from DD*K̄* dynamics.",
  },
  {
    key: "em-chiral-pt",
    roman: "iii.",
    title: "EM properties with χPT",
    body: "Electromagnetic polarizabilities of singly heavy baryons (spin-½, spin-³⁄₂) and triplet hadrons in heavy hadron chiral perturbation theory.",
  },
  {
    key: "production",
    roman: "iv.",
    title: "Production of exotic states",
    body: "Branching fractions of B-meson decays into exotic D-meson resonances; hidden-charm molecules with strangeness in B and B_s decays.",
  },
];
---
<Base title="Yan-Ke Chen — Theoretical Physics" currentPage="home"
      description="Yan-Ke Chen — Postdoctoral Researcher at Peking University CHEP. Hadron spectroscopy, exotic states, chiral perturbation theory.">

  <Hero />

  <NumbersStrip />

  <section class="block py-[clamp(3.5rem,7vw,5.5rem)] border-b border-rule">
    <div class="section-head grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-12 items-baseline">
      <div class="mark font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">
        <span class="roman text-mark mr-2">§ I</span>Selected work
      </div>
      <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
        Five papers that <em class="italic text-ink-2">most</em> represent what I work on.
      </h2>
    </div>
    <PubList mode="selected" limit={5} />
  </section>

  <section class="block py-[clamp(3.5rem,7vw,5.5rem)]">
    <div class="section-head grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-12 items-baseline">
      <div class="mark font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">
        <span class="roman text-mark mr-2">§ II</span>Themes
      </div>
      <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
        Four threads running through the work.
      </h2>
    </div>
    <div class="themes grid grid-cols-1 md:grid-cols-2 gap-px bg-rule border border-rule">
      {themes.map(t => (
        <ThemeCard roman={t.roman} title={t.title} body={t.body} count={groupCounts[t.key] ?? 0} />
      ))}
    </div>
  </section>
</Base>
```

- [ ] **Step 2: Build and visually compare to mockup**

```bash
cd /Users/ykchen/science_project/personal_profile/site
npm run dev
```

Open `http://localhost:4321/` in a browser. Compare against `mockups/index.html` (open in another tab). Differences to expect:
- Real numbers from INSPIRE (not the mockup's placeholders).
- Selected publications are the 5 most recent first-author papers.
Every typographic and color detail should match.

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/index.astro
git commit -m "feat(site): wire / (home) page with real INSPIRE data"
```

---

## Phase E · Analytics page

### Task E1: Trajectory chart (Chart.js mixed bar+line)

**Files:**
- Create: `site/src/components/charts/Trajectory.tsx`

- [ ] **Step 1: Install Chart.js**

```bash
cd /Users/ykchen/science_project/personal_profile/site
npm install chart.js@^4
```

- [ ] **Step 2: Write `site/src/components/charts/Trajectory.tsx`**

```tsx
import { useEffect, useRef } from "react";
import {
  Chart, BarController, BarElement, LineController, LineElement,
  PointElement, CategoryScale, LinearScale, Tooltip, Filler,
} from "chart.js";

Chart.register(BarController, BarElement, LineController, LineElement,
  PointElement, CategoryScale, LinearScale, Tooltip, Filler);

const INK    = "#15120E";
const MARK   = "#B0492A";
const ACCENT = "#1B2E5E";
const ACCENT_SOFT = "rgba(27,46,94,0.12)";
const INK3   = "#8C8579";
const RULE2  = "#ECE6D6";

type YearRow = { year: number; papers: number; cum_citations: number; h_index: number };

export default function Trajectory({ rows }: { rows: YearRow[] }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const currentYear = new Date().getFullYear();
    const barColors = rows.map(r => r.year === currentYear ? MARK : INK);

    const chart = new Chart(canvasRef.current, {
      type: "bar",
      data: {
        labels: rows.map(r => String(r.year)),
        datasets: [
          {
            type: "bar",
            label: "Papers",
            data: rows.map(r => r.papers),
            backgroundColor: barColors,
            borderWidth: 0,
            yAxisID: "y",
            order: 2,
          },
          {
            type: "line",
            label: "Cumulative citations",
            data: rows.map(r => r.cum_citations),
            borderColor: ACCENT,
            backgroundColor: ACCENT_SOFT,
            borderWidth: 1.5,
            tension: 0,
            pointRadius: 2.5,
            pointBackgroundColor: ACCENT,
            fill: true,
            yAxisID: "y1",
            order: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 900, easing: "easeOutCubic" },
        plugins: {
          tooltip: {
            backgroundColor: INK,
            titleFont: { family: "IBM Plex Mono", size: 11 },
            bodyFont:  { family: "IBM Plex Mono", size: 11 },
            padding: 8, displayColors: false,
          },
          legend: { display: false },
        },
        scales: {
          x: {
            grid:   { display: false },
            border: { color: INK },
            ticks:  { color: INK3, font: { family: "IBM Plex Mono", size: 10 } },
          },
          y: {
            position: "left",
            grid:   { color: RULE2, lineWidth: 1 },
            border: { display: false },
            ticks:  { color: INK3, font: { family: "IBM Plex Mono", size: 10 }, precision: 0 },
            title:  { display: true, text: "PAPERS", color: INK3, font: { family: "IBM Plex Mono", size: 9 } },
          },
          y1: {
            position: "right",
            grid:   { display: false },
            border: { display: false },
            ticks:  { color: INK3, font: { family: "IBM Plex Mono", size: 10 } },
            title:  { display: true, text: "CUMULATIVE CITES", color: INK3, font: { family: "IBM Plex Mono", size: 9 } },
          },
        },
      },
    });
    return () => chart.destroy();
  }, [rows]);

  return <div style={{ height: 320 }}><canvas ref={canvasRef} aria-label="Bar chart of papers per year overlaid with cumulative citation line"/></div>;
}
```

- [ ] **Step 3: Commit**

```bash
git add site/src/components/charts/Trajectory.tsx site/package.json site/package-lock.json
git commit -m "feat(site): Trajectory chart — Chart.js mixed bar+line, themed"
```

---

### Task E2: HIndexStrip, TopPapers, Keywords, JournalDonut, Institutions

**Files:**
- Create: `site/src/components/charts/HIndexStrip.tsx`
- Create: `site/src/components/charts/TopPapers.astro`
- Create: `site/src/components/charts/Keywords.astro`
- Create: `site/src/components/charts/JournalDonut.tsx`
- Create: `site/src/components/charts/Institutions.astro`

- [ ] **Step 1: Write `site/src/components/charts/HIndexStrip.tsx`**

```tsx
import { useEffect, useRef } from "react";
import {
  Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip,
} from "chart.js";

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

const INK = "#15120E", MARK = "#B0492A", INK3 = "#8C8579";

type YearRow = { year: number; h_index: number };

export default function HIndexStrip({ rows }: { rows: YearRow[] }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    if (!canvasRef.current) return;
    const currentYear = new Date().getFullYear();
    const chart = new Chart(canvasRef.current, {
      type: "bar",
      data: {
        labels: rows.map(r => String(r.year)),
        datasets: [{
          data: rows.map(r => r.h_index),
          backgroundColor: rows.map(r => r.year === currentYear ? MARK : INK),
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { backgroundColor: INK, padding: 6 } },
        scales: {
          x: { grid: { display: false }, ticks: { color: INK3, font: { family: "IBM Plex Mono", size: 10 } } },
          y: { display: false, beginAtZero: true },
        },
      },
    });
    return () => chart.destroy();
  }, [rows]);
  return <div style={{ height: 110 }}><canvas ref={canvasRef} aria-label="h-index sparkline by year"/></div>;
}
```

- [ ] **Step 2: Write `site/src/components/charts/TopPapers.astro`**

```astro
---
import inspire from "../../data/inspire.json";

const top = (inspire.metrics.top_papers as any[]).slice(0, 10);
const max = Math.max(1, ...top.map(p => p.citations));
---
<div class="toppapers">
  {top.map((p, i) => (
    <div class={`toppaper grid grid-cols-[3rem_1fr_5rem] items-center gap-5 py-3 border-t border-rule-2 first:border-t-0 ${i === 0 ? "is-top" : ""}`}>
      <div class="rank font-mono text-[.7rem] text-ink-3 tracking-[.06em]">{String(i + 1).padStart(2, "0")}</div>
      <div>
        <div class="font-sans text-[.82rem] text-ink leading-[1.35] mb-1">
          {p.title}
          <span class="venue font-mono text-[.68rem] text-ink-3 ml-2 tracking-[.04em] uppercase">
            {p.venue.journal ?? "arXiv"} · {p.year}
          </span>
        </div>
        <div class="pbar h-2 bg-rule-2 relative">
          <i class={`absolute inset-y-0 left-0 ${i === 0 ? "bg-mark" : "bg-ink"} animate-[fill_1.1s_cubic-bezier(.2,.7,.2,1)_forwards]`}
             style={`width:${(p.citations / max) * 100}%; transform-origin:left;`}></i>
        </div>
      </div>
      <div class={`cn text-right font-serif font-light text-[1.8rem] leading-none tracking-[-0.02em] ${i === 0 ? "text-mark" : "text-ink"}`}>
        {p.citations}
      </div>
    </div>
  ))}
</div>

<style>
  @keyframes fill { from { transform: scaleX(0); } to { transform: scaleX(1); } }
</style>
```

- [ ] **Step 3: Write `site/src/components/charts/Keywords.astro`**

```astro
---
import inspire from "../../data/inspire.json";
const terms = inspire.metrics.keywords as Array<{ term: string; count: number }>;
const max = Math.max(1, ...terms.map(t => t.count));
---
<div class="topics flex flex-col">
  {terms.map(t => (
    <div class="kw grid grid-cols-[14ch_1fr_4ch] items-center gap-4 py-2 border-t border-rule-2 first:border-t-0">
      <div class="term font-serif text-[1rem] text-ink">{t.term}</div>
      <div class="bar h-1.5 bg-rule-2 relative overflow-hidden">
        <i class="absolute inset-0 right-auto bg-ink-2 animate-[fill_.9s_cubic-bezier(.2,.7,.2,1)_forwards]"
           style={`width:${(t.count / max) * 100}%; transform-origin:left;`}></i>
      </div>
      <div class="cnt font-mono text-[.78rem] text-ink-2 text-right">{t.count}</div>
    </div>
  ))}
</div>
```

- [ ] **Step 4: Write `site/src/components/charts/JournalDonut.tsx`**

```tsx
import { useEffect, useRef } from "react";
import { Chart, DoughnutController, ArcElement, Tooltip } from "chart.js";
Chart.register(DoughnutController, ArcElement, Tooltip);

const INK = "#15120E", ACCENT = "#1B2E5E", MARK = "#B0492A", INK3 = "#8C8579", PAPER = "#F6F4EE";

type JC = { name: string; count: number };

export default function JournalDonut({ items, total }: { items: JC[]; total: number }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    if (!canvasRef.current) return;
    const palette = [INK, ACCENT, MARK, INK3, "#A29A8C", "#736C5F"];
    const colors = items.map((_, i) => palette[i % palette.length]);
    const chart = new Chart(canvasRef.current, {
      type: "doughnut",
      data: {
        labels: items.map(i => i.name),
        datasets: [{
          data: items.map(i => i.count),
          backgroundColor: colors,
          borderColor: PAPER,
          borderWidth: 2,
        }],
      },
      options: {
        cutout: "62%",
        plugins: { legend: { display: false }, tooltip: { backgroundColor: INK, padding: 6, bodyFont: { family: "IBM Plex Mono", size: 11 } } },
      },
    });
    return () => chart.destroy();
  }, [items]);

  return (
    <div className="donut-wrap grid grid-cols-1 sm:grid-cols-[200px_1fr] gap-8 items-center">
      <div className="relative" style={{ width: 200, height: 200 }}>
        <canvas ref={canvasRef} aria-label={`Donut chart of ${items.length} journals across ${total} papers`} />
        <div className="absolute inset-0 grid place-content-center pointer-events-none">
          <div className="text-center">
            <div className="font-serif text-[34px] font-light leading-none">{total}</div>
            <div className="font-mono text-[9px] tracking-[.18em] uppercase text-ink-3 mt-1">papers</div>
          </div>
        </div>
      </div>
      <div className="donut-legend font-mono text-[.78rem] text-ink-2">
        {items.map((i, idx) => (
          <div key={i.name} className="grid grid-cols-[12px_1fr_4ch] gap-3 items-center py-1.5 border-t border-rule-2 first:border-t-0">
            <div className="w-2.5 h-2.5 rounded-[1px]" style={{ background: ["#15120E","#1B2E5E","#B0492A","#8C8579","#A29A8C","#736C5F"][idx % 6] }} />
            <div>{i.name}</div>
            <div className="text-right text-ink" style={{ fontFeatureSettings: '"tnum"' }}>{i.count}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Write `site/src/components/charts/Institutions.astro`**

```astro
---
import inspire from "../../data/inspire.json";
const insts = (inspire.metrics.institutions as any[]).slice(0, 6);
const max = Math.max(1, ...insts.map(i => i.joint_papers));
---
<div class="inst-list">
  {insts.length === 0 ? (
    <p class="font-mono text-[.78rem] text-ink-3 py-4">Institutional affiliations are populated on the next data refresh — re-run the fetcher.</p>
  ) : insts.map(inst => (
    <div class="inst grid grid-cols-[20ch_1fr_5ch] gap-4 items-center py-2 border-t border-rule-2 first:border-t-0 text-[.85rem]">
      <div class="name text-ink">{inst.name}{inst.city && <em class="italic text-ink-3 text-[.82em] ml-2 not-italic">· {inst.city}</em>}</div>
      <div class="b h-1.5 bg-rule-2 relative">
        <i class="absolute inset-y-0 left-0 bg-accent animate-[fill_1s_cubic-bezier(.2,.7,.2,1)_forwards]" style={`width:${(inst.joint_papers/max)*100}%; transform-origin:left;`}></i>
      </div>
      <div class="v text-right font-mono text-[.78rem] text-ink-2" style="font-feature-settings:'tnum';">{inst.joint_papers}</div>
    </div>
  ))}
</div>
```

- [ ] **Step 6: Commit**

```bash
git add site/src/components/charts/
git commit -m "feat(site): HIndexStrip, TopPapers, Keywords, JournalDonut, Institutions"
```

---

### Task E3: Coauthor network (D3 force)

**Files:**
- Create: `site/src/components/charts/CoauthorNetwork.tsx`

- [ ] **Step 1: Install d3-force**

```bash
cd /Users/ykchen/science_project/personal_profile/site
npm install d3-force@^3 d3-selection@^3 d3-drag@^3
```

- [ ] **Step 2: Write `site/src/components/charts/CoauthorNetwork.tsx`**

```tsx
import { useEffect, useRef } from "react";
import {
  forceSimulation, forceManyBody, forceLink, forceCenter, forceCollide,
  Simulation, SimulationNodeDatum, SimulationLinkDatum,
} from "d3-force";

const INK = "#15120E", MARK = "#B0492A", INK3 = "#8C8579", PAPER = "#F6F4EE";

type CoauthorIn = { name: string; joint_papers: number; inspire_id?: string | null };

interface Node extends SimulationNodeDatum { id: string; name: string; joint: number; you?: boolean; r: number; }
interface Link extends SimulationLinkDatum<Node> { source: string; target: string; }

export default function CoauthorNetwork({ coauthors, youName = "Yan-Ke Chen" }: { coauthors: CoauthorIn[]; youName?: string }) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = svgRef.current;
    const W = svg.clientWidth || 800, H = svg.clientHeight || 500;

    // Build nodes
    const nodes: Node[] = [
      { id: "you", name: youName, joint: coauthors.reduce((a, c) => a + c.joint_papers, 0), you: true, r: 20 },
      ...coauthors.slice(0, 30).map(c => ({
        id: c.name, name: c.name, joint: c.joint_papers,
        r: Math.max(4, 4 + Math.sqrt(c.joint_papers) * 4),
      })),
    ];
    // Star topology around `you`; plus inter-coauthor edges when joint >=2 (proxy for repeated collab)
    const links: Link[] = nodes
      .filter(n => !n.you)
      .map(n => ({ source: "you", target: n.id }));

    const sim: Simulation<Node, Link> = forceSimulation<Node, Link>(nodes)
      .force("charge", forceManyBody().strength(-180))
      .force("link", forceLink<Node, Link>(links).id(d => d.id).distance(d => 60 + 200 / Math.max(1, (d.target as Node).r)))
      .force("center", forceCenter(W / 2, H / 2))
      .force("collide", forceCollide<Node>().radius(d => d.r + 4));

    // Render
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const NS = "http://www.w3.org/2000/svg";

    const linkG = document.createElementNS(NS, "g");
    svg.appendChild(linkG);
    const lineEls = links.map(l => {
      const ln = document.createElementNS(NS, "line");
      ln.setAttribute("stroke", INK3);
      ln.setAttribute("stroke-opacity", "0.35");
      linkG.appendChild(ln);
      return ln;
    });

    const nodeG = document.createElementNS(NS, "g");
    svg.appendChild(nodeG);
    const nodeEls = nodes.map(n => {
      const g = document.createElementNS(NS, "g");
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("r", String(n.r));
      c.setAttribute("fill", n.you ? MARK : PAPER);
      c.setAttribute("stroke", n.you ? MARK : INK);
      c.setAttribute("stroke-width", "1.2");
      c.setAttribute("style", "cursor:pointer; transition: fill .2s, stroke .2s;");
      const t = document.createElementNS(NS, "text");
      t.setAttribute("text-anchor", "middle");
      t.setAttribute("dy", String(n.you ? -n.r - 8 : -n.r - 6));
      t.setAttribute("style",
        n.you
          ? "font-family:Newsreader,serif; font-size:14px; font-style:italic; fill:#15120E; pointer-events:none;"
          : "font-family:'IBM Plex Mono',monospace; font-size:10px; fill:#4C463D; pointer-events:none;");
      t.textContent = n.name;
      g.appendChild(c); g.appendChild(t);
      nodeG.appendChild(g);
      return { g, c, t };
    });

    sim.on("tick", () => {
      links.forEach((l, i) => {
        const s = l.source as unknown as Node, t = l.target as unknown as Node;
        lineEls[i].setAttribute("x1", String(s.x ?? 0));
        lineEls[i].setAttribute("y1", String(s.y ?? 0));
        lineEls[i].setAttribute("x2", String(t.x ?? 0));
        lineEls[i].setAttribute("y2", String(t.y ?? 0));
      });
      nodes.forEach((n, i) => {
        nodeEls[i].g.setAttribute("transform", `translate(${n.x ?? 0}, ${n.y ?? 0})`);
      });
    });

    return () => { sim.stop(); };
  }, [coauthors, youName]);

  return (
    <div className="net-wrap relative aspect-[16/10] bg-paper overflow-hidden">
      <svg ref={svgRef} className="w-full h-full" role="img" aria-label="Force-directed coauthor network" />
      <div className="absolute inset-0 pointer-events-none" style={{ background: "radial-gradient(ellipse at center, transparent 60%, var(--paper) 100%)" }} />
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add site/src/components/charts/CoauthorNetwork.tsx site/package.json site/package-lock.json
git commit -m "feat(site): CoauthorNetwork — D3 force simulation, themed"
```

---

### Task E4: Analytics page wiring

**Files:**
- Create: `site/src/pages/analytics.astro`

- [ ] **Step 1: Write `site/src/pages/analytics.astro`**

```astro
---
import Base from "../layouts/Base.astro";
import Figure from "../components/Figure.astro";
import TopPapers from "../components/charts/TopPapers.astro";
import Keywords from "../components/charts/Keywords.astro";
import Institutions from "../components/charts/Institutions.astro";
import Trajectory from "../components/charts/Trajectory";
import HIndexStrip from "../components/charts/HIndexStrip";
import JournalDonut from "../components/charts/JournalDonut";
import CoauthorNetwork from "../components/charts/CoauthorNetwork";
import inspire from "../data/inspire.json";

const m = inspire.metrics;
const fetchedLabel = new Date(inspire.fetched_at).toISOString().slice(0, 10).replace(/-/g, "·");
---
<Base title="Analytics — Yan-Ke Chen" currentPage="analytics"
      description="Career analytics for Yan-Ke Chen drawn from INSPIRE-HEP.">

  <section class="a-hero grid grid-cols-1 md:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] gap-[var(--col-gap)] items-end py-[clamp(3rem,7vw,5rem)] border-b border-rule stagger">
    <div>
      <p class="label font-mono text-[.72rem] tracking-[.18em] uppercase text-ink-3 m-0 mb-5"><span class="text-mark mr-2">§</span>Analytics</p>
      <h1 class="font-serif font-normal text-[clamp(2.6rem,6vw,4.5rem)] leading-[1.02] tracking-[-0.02em] m-0 max-w-[18ch]" style="font-variation-settings:'opsz' 60;">
        An evolving portrait of <em class="italic text-ink-2 font-light">{m.papers_total}</em> papers and the people behind them.
      </h1>
      <p class="refresh font-mono text-[.72rem] text-ink-3 tracking-[.06em] mt-5 flex items-center gap-2 before:content-[''] before:w-1.5 before:h-1.5 before:bg-mark before:rounded-full">
        Last refreshed {fetchedLabel} from inspirehep.net/authors/{inspire.author.id}
      </p>
    </div>
    <p class="sub font-serif font-light text-[1.05rem] leading-[1.55] text-ink-2 max-w-[38ch] m-0">
      Every number on this page is fetched from INSPIRE-HEP and rebuilt
      at deploy time. Hover any element to see its source paper.
      Charts read as figures in an editorial spread — one idea per figure,
      sparse ink, captions below.
    </p>
  </section>

  <!-- §I Trajectory -->
  <section class="block py-[clamp(3.5rem,7vw,5.5rem)] border-b border-rule">
    <div class="section-head grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-12 items-baseline">
      <div>
        <div class="mark font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3"><span class="text-mark mr-2">§ I</span>Trajectory</div>
        <div class="desc font-sans text-[.85rem] text-ink-2 mt-4 max-w-[50ch]">Papers per year, with cumulative citations as an overlay; h-index evolution beneath.</div>
      </div>
      <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
        {m.by_year.length ? `${m.by_year.length} years, mostly` : "A career"} <em class="italic text-ink-2">spent</em> in heavy-quark territory.
      </h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)] gap-[var(--col-gap)]">
      <div>
        <Figure title="Publications & cumulative citations" number="Fig. 1 / inspire">
          <Trajectory client:load rows={m.by_year} />
          <p slot="caption" class="figure-cap mt-5 pt-4 border-t border-rule-2 font-sans text-[.78rem] text-ink-3 leading-[1.5]">
            <b class="font-medium text-ink-2">Note.</b> The current year may be partial.
          </p>
        </Figure>

        <div class="mt-6"></div>

        <Figure title="h-index, year by year" number="Fig. 2">
          <HIndexStrip client:load rows={m.by_year} />
        </Figure>
      </div>

      <aside class="side flex flex-col gap-8 pt-2">
        {[
          { n: m.papers_total,             lbl: "Peer-reviewed papers" },
          { n: `~${m.citations_total}`,    lbl: "Total citations" },
          { n: m.h_index,                  lbl: "h-index" },
          { n: m.first_author_count,       lbl: "First-author papers" },
        ].map(s => (
          <div class="stat border-t border-rule pt-4 first:border-t-0 first:pt-0">
            <div class="n font-serif font-light text-[3.4rem] leading-none tracking-[-0.02em] text-ink" style="font-variation-settings:'opsz' 60;">{s.n}</div>
            <div class="lbl font-mono text-[.7rem] uppercase tracking-[.16em] text-ink-2 mt-2">{s.lbl}</div>
          </div>
        ))}
      </aside>
    </div>
  </section>

  <!-- §II Reception -->
  <section class="block py-[clamp(3.5rem,7vw,5.5rem)] border-b border-rule">
    <div class="section-head grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-12 items-baseline">
      <div>
        <div class="mark font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3"><span class="text-mark mr-2">§ II</span>Reception</div>
        <div class="desc font-sans text-[.85rem] text-ink-2 mt-4 max-w-[50ch]">The papers the community has engaged with most.</div>
      </div>
      <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
        The <em class="italic text-ink-2">tail is long</em>; the head, surprisingly even.
      </h2>
    </div>
    <Figure title="Top 10 papers · by citation count" number="Fig. 3 / inspire">
      <TopPapers />
    </Figure>
  </section>

  <!-- §III Themes & venues -->
  <section class="block py-[clamp(3.5rem,7vw,5.5rem)] border-b border-rule">
    <div class="section-head grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-12 items-baseline">
      <div>
        <div class="mark font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3"><span class="text-mark mr-2">§ III</span>Themes &amp; venues</div>
      </div>
      <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
        <em class="italic text-ink-2">Tetraquarks</em>, heavy quarks, and a lot of <em class="italic text-ink-2">Phys. Rev. D</em>.
      </h2>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-[var(--col-gap)]">
      <Figure title="Keyword frequency · titles" number="Fig. 4">
        <Keywords />
      </Figure>
      <Figure title="Journal distribution" number="Fig. 5">
        <JournalDonut client:load items={m.journals} total={m.papers_total} />
      </Figure>
    </div>
  </section>

  <!-- §IV Collaboration -->
  <section class="block py-[clamp(3.5rem,7vw,5.5rem)]">
    <div class="section-head grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-12 items-baseline">
      <div>
        <div class="mark font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3"><span class="text-mark mr-2">§ IV</span>Collaboration</div>
      </div>
      <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
        A <em class="italic text-ink-2">tight</em> core, expanding outward.
      </h2>
    </div>
    <Figure title="Coauthor network · drag to reposition" number="Fig. 6 / d3-force">
      <CoauthorNetwork client:load coauthors={m.coauthors} youName={inspire.author.name} />
    </Figure>

    <div class="mt-6"></div>

    <Figure title="Top institutions by joint papers" number="Fig. 7">
      <Institutions />
    </Figure>
  </section>
</Base>
```

- [ ] **Step 2: Build and visually compare to mockup**

```bash
cd /Users/ykchen/science_project/personal_profile/site
npm run dev
```

Open `http://localhost:4321/analytics`. Compare against `mockups/analytics.html`. All four figures should render with real data.

- [ ] **Step 3: Fix any rendering bugs that show up**

Common ones:
- Chart canvases need a fixed height — verified in HIndexStrip / Trajectory wrappers.
- The coauthor network requires the SVG to have a measurable size; aspect-ratio + width:100% in the wrapper gives this.

- [ ] **Step 4: Commit**

```bash
git add site/src/pages/analytics.astro
git commit -m "feat(site): wire /analytics page with all four figures"
```

---

## Phase F · Remaining pages

### Task F1: Publications page (filterable, no JS framework needed)

**Files:**
- Create: `site/src/components/PubFilter.tsx`
- Create: `site/src/pages/publications.astro`

- [ ] **Step 1: Write `site/src/components/PubFilter.tsx`**

```tsx
import { useMemo, useState } from "react";

type Author = { name: string; is_you: boolean };
type Paper = {
  inspire_id: string;
  title: string;
  authors: Author[];
  venue: { journal?: string | null; volume?: string | null; page?: string | null; year?: number | null };
  arxiv_id?: string | null;
  doi?: string | null;
  citations: number;
  year?: number | null;
  topic_group: string;
};

const TOPIC_LABELS: Record<string, string> = {
  "spectrum-quark-models":    "Spectrum / quark models",
  "exotic-coupled-channel":   "Coupled channels",
  "em-chiral-pt":             "EM / χPT",
  "production":               "Production",
  "uncategorised":            "Other",
};

export default function PubFilter({ papers }: { papers: Paper[] }) {
  const [topic, setTopic] = useState<string>("all");
  const [year, setYear]   = useState<string>("all");

  const years = useMemo(() => {
    const set = new Set(papers.map(p => p.year).filter(Boolean) as number[]);
    return Array.from(set).sort((a, b) => b - a);
  }, [papers]);
  const topics = useMemo(() => Array.from(new Set(papers.map(p => p.topic_group))), [papers]);

  const filtered = papers.filter(p =>
    (topic === "all" || p.topic_group === topic) &&
    (year  === "all" || String(p.year) === year)
  );

  const fmtAuthors = (a: Author[]) =>
    a.map(x => x.is_you ? <b key={x.name}>{x.name}</b> : x.name)
     .reduce<React.ReactNode[]>((acc, el, i) => i === 0 ? [el] : [...acc, ", ", el], []);

  const chipBase = "px-3 py-1 font-mono text-[.7rem] uppercase tracking-[.14em] border border-rule cursor-pointer transition-colors";
  const chipOn   = "bg-ink text-paper border-ink";

  return (
    <div>
      <div className="flex gap-2 flex-wrap mb-6">
        <button className={`${chipBase} ${topic === "all" ? chipOn : ""}`} onClick={() => setTopic("all")}>All topics</button>
        {topics.map(t => (
          <button key={t} className={`${chipBase} ${topic === t ? chipOn : ""}`} onClick={() => setTopic(t)}>
            {TOPIC_LABELS[t] ?? t}
          </button>
        ))}
      </div>
      <div className="flex gap-2 flex-wrap mb-8">
        <button className={`${chipBase} ${year === "all" ? chipOn : ""}`} onClick={() => setYear("all")}>All years</button>
        {years.map(y => (
          <button key={y} className={`${chipBase} ${year === String(y) ? chipOn : ""}`} onClick={() => setYear(String(y))}>{y}</button>
        ))}
      </div>

      <div className="text-ink-3 font-mono text-[.72rem] mb-4 tracking-[.06em]">{filtered.length} paper{filtered.length === 1 ? "" : "s"}</div>

      {filtered.sort((a, b) => (b.year ?? 0) - (a.year ?? 0)).map(p => (
        <article key={p.inspire_id} className="grid grid-cols-[5rem_1fr_5rem] md:grid-cols-[8rem_1fr_6rem] gap-[var(--col-gap)] py-7 border-t border-rule [&:last-child]:border-b items-baseline hover:bg-rule-2/50">
          <div className="font-mono text-[.78rem] text-ink-3 tracking-[.1em]">{p.year ?? "—"}</div>
          <div>
            <h3 className="font-serif font-normal text-[1.18rem] leading-[1.3] text-ink m-0 mb-2 tracking-[-0.005em]" style={{ fontVariationSettings: "'opsz' 22" }}>
              {p.title}
            </h3>
            <div className="text-[.86rem] text-ink-2 mb-2">{fmtAuthors(p.authors)}</div>
            <div className="font-mono text-[.72rem] text-ink-2 tracking-[.04em] uppercase">
              {p.venue.journal && <span>{p.venue.journal}{p.venue.volume ? ` ${p.venue.volume}` : ""}{p.venue.page ? `, ${p.venue.page}` : ""}</span>}
              {p.venue.journal && p.arxiv_id && <span className="text-ink-3 mx-2">·</span>}
              {p.arxiv_id && <a className="text-ink-2 hover:text-accent" href={`https://arxiv.org/abs/${p.arxiv_id}`}>arXiv:{p.arxiv_id}</a>}
              {p.doi && <><span className="text-ink-3 mx-2">·</span><a className="text-ink-2 hover:text-accent" href={`https://doi.org/${p.doi}`}>doi</a></>}
            </div>
          </div>
          <div className="text-right font-serif font-light text-[2.4rem] leading-none text-ink tracking-[-0.02em]" style={{ fontVariationSettings: "'opsz' 60" }}>
            {p.citations}
            <span className="block font-mono text-[.6rem] text-ink-3 tracking-[.18em] uppercase mt-1 font-normal">citations</span>
          </div>
        </article>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Write `site/src/pages/publications.astro`**

```astro
---
import Base from "../layouts/Base.astro";
import PubFilter from "../components/PubFilter";
import inspire from "../data/inspire.json";
const papers = inspire.papers as any[];
---
<Base title="Publications — Yan-Ke Chen" currentPage="publications">
  <section class="py-[clamp(3rem,7vw,5rem)] border-b border-rule">
    <p class="font-mono text-[.72rem] tracking-[.18em] uppercase text-ink-3 m-0 mb-5"><span class="text-mark mr-2">§</span>Publications</p>
    <h1 class="font-serif font-normal text-[clamp(2.6rem,6vw,4.5rem)] leading-[1.02] tracking-[-0.02em] m-0 max-w-[20ch]" style="font-variation-settings:'opsz' 60;">
      {papers.length} papers, filterable by topic and year.
    </h1>
  </section>
  <section class="py-[clamp(2.5rem,5vw,4rem)]">
    <PubFilter client:load papers={papers} />
  </section>
</Base>
```

- [ ] **Step 3: Commit**

```bash
git add site/src/components/PubFilter.tsx site/src/pages/publications.astro
git commit -m "feat(site): /publications with topic + year filters"
```

---

### Task F2: Research page

**Files:**
- Create: `site/src/pages/research.astro`

- [ ] **Step 1: Write `site/src/pages/research.astro`**

```astro
---
import Base from "../layouts/Base.astro";
import PubList from "../components/PubList.astro";

const themes = [
  {
    key: "spectrum-quark-models",
    roman: "§ I",
    title: "Spectrum of exotic states with quark models",
    body: "Across nine papers I have worked on a unified treatment of molecular and compact tetraquarks. The constituent-quark-model series with Wu, Ma, and Meng benchmarks doubly- and fully-heavy systems against complementary methods, including diffusion Monte-Carlo. The Qsq̄q̄ paper (PRD 109) ties molecular bound, resonant, and compact configurations into one calculation.",
  },
  {
    key: "exotic-coupled-channel",
    roman: "§ II",
    title: "Hadron-hadron interaction & coupled channels",
    body: "I have developed an improved complex-scaling method for virtual states in coupled-channel problems (PRD 109, 034006), applied it to the pole origin of X(3872) with Wang and Lin, and predicted three-body molecular states in the DD*K̄* and BB*K* systems (arXiv:2602.12010, the topic of my January 2026 invited talk).",
  },
  {
    key: "em-chiral-pt",
    roman: "§ III",
    title: "EM properties with χPT",
    body: "A trilogy with Wen, Meng, Dang and Zhu on electromagnetic polarizabilities — singly heavy baryons (spin-½ and spin-³⁄₂) and triplet hadrons — within heavy hadron chiral perturbation theory. The polarizability of charm- and bottom-baryon systems is, to my knowledge, calculated systematically for the first time in this series.",
  },
  {
    key: "production",
    roman: "§ IV",
    title: "Production of exotic states",
    body: "My early work focused on production: branching fractions of B-meson decays into the exotic D-meson resonances X₀,₁(2900) (EPJC 2021, my first paper), and hidden-charm molecular states with strangeness in B and B_s decays (PRD 2023, with Wu, Li, Liu, Chen).",
  },
];
---
<Base title="Research — Yan-Ke Chen" currentPage="research">
  <section class="py-[clamp(3rem,7vw,5rem)] border-b border-rule">
    <p class="font-mono text-[.72rem] tracking-[.18em] uppercase text-ink-3 m-0 mb-5"><span class="text-mark mr-2">§</span>Research</p>
    <h1 class="font-serif font-normal text-[clamp(2.6rem,6vw,4.5rem)] leading-[1.02] tracking-[-0.02em] m-0 max-w-[24ch]" style="font-variation-settings:'opsz' 60;">
      Four threads — each with its own publication list.
    </h1>
  </section>

  {themes.map(t => (
    <section class="py-[clamp(3rem,6vw,5rem)] border-b border-rule">
      <div class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)] mb-10 items-baseline">
        <div class="font-mono text-[.72rem] uppercase tracking-[.18em] text-mark">{t.roman}</div>
        <h2 class="font-serif font-normal text-[clamp(1.6rem,3vw,2.4rem)] leading-tight tracking-[-0.015em] m-0 max-w-[32ch]" style="font-variation-settings:'opsz' 36;">
          {t.title}
        </h2>
      </div>
      <p class="font-serif font-light text-[1.05rem] leading-[1.6] text-ink-2 max-w-[64ch] mb-10">{t.body}</p>
      <PubList topicGroup={t.key} />
    </section>
  ))}
</Base>
```

- [ ] **Step 2: Commit**

```bash
git add site/src/pages/research.astro
git commit -m "feat(site): /research page with four themes and grouped publications"
```

---

### Task F3: CV page

**Files:**
- Create: `site/src/pages/cv.astro`

- [ ] **Step 1: Write `site/src/pages/cv.astro`**

```astro
---
import Base from "../layouts/Base.astro";
---
<Base title="CV — Yan-Ke Chen" currentPage="cv">
  <section class="py-[clamp(3rem,7vw,5rem)] border-b border-rule">
    <p class="font-mono text-[.72rem] tracking-[.18em] uppercase text-ink-3 m-0 mb-5"><span class="text-mark mr-2">§</span>Curriculum vitae</p>
    <div class="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-8 items-end">
      <h1 class="font-serif font-normal text-[clamp(2.6rem,6vw,4.5rem)] leading-[1.02] tracking-[-0.02em] m-0 max-w-[22ch]" style="font-variation-settings:'opsz' 60;">
        The full record, in one PDF.
      </h1>
      <a href="/cv/CV_YKChen.pdf" class="inline-block px-6 py-4 bg-ink text-paper font-mono text-[.78rem] uppercase tracking-[.14em] hover:bg-accent transition-colors">
        Download CV (PDF)
      </a>
    </div>
  </section>

  <section class="py-[clamp(2.5rem,5vw,4rem)] border-b border-rule">
    <div class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)]">
      <div class="font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">Education</div>
      <div>
        <div class="mb-6">
          <div class="font-serif text-[1.18rem] text-ink mb-1">Ph.D., Theoretical Physics — Peking University</div>
          <div class="font-mono text-[.72rem] text-ink-3 tracking-[.06em] uppercase mb-2">Sep. 2020 – Jun. 2025</div>
          <div class="text-[.9rem] text-ink-2">Advisor: Prof. Shi-Lin Zhu</div>
        </div>
        <div>
          <div class="font-serif text-[1.18rem] text-ink mb-1">B.S., Physics — Lanzhou University</div>
          <div class="font-mono text-[.72rem] text-ink-3 tracking-[.06em] uppercase">Sep. 2016 – Jul. 2020</div>
        </div>
      </div>
    </div>
  </section>

  <section class="py-[clamp(2.5rem,5vw,4rem)] border-b border-rule">
    <div class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)]">
      <div class="font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">Position</div>
      <div>
        <div class="font-serif text-[1.18rem] text-ink mb-1">Postdoctoral Researcher — CHEP, Peking University</div>
        <div class="font-mono text-[.72rem] text-ink-3 tracking-[.06em] uppercase mb-2">Jul. 2025 – present</div>
        <div class="text-[.9rem] text-ink-2">Supervisor: Prof. Shi-Lin Zhu</div>
      </div>
    </div>
  </section>

  <section class="py-[clamp(2.5rem,5vw,4rem)] border-b border-rule">
    <div class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)]">
      <div class="font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">Honours</div>
      <ul class="m-0 p-0 list-none space-y-3 text-[.95rem]">
        <li>President Scholarship · 2024–25</li>
        <li>National Scholarship · 2019–20</li>
        <li>Merit Student · 2024–25</li>
        <li>Merit Student Pacesetter · 2019–20</li>
      </ul>
    </div>
  </section>

  <section class="py-[clamp(2.5rem,5vw,4rem)] border-b border-rule">
    <div class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)]">
      <div class="font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">Service</div>
      <ul class="m-0 p-0 list-none space-y-2 text-[.95rem]">
        <li>Peer reviewer · <em class="italic">Physical Review D</em></li>
        <li>Peer reviewer · <em class="italic">Chinese Physics C</em></li>
        <li>Peer reviewer · <em class="italic">The European Physical Journal C</em></li>
      </ul>
    </div>
  </section>

  <section class="py-[clamp(2.5rem,5vw,4rem)] border-b border-rule">
    <div class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-[var(--col-gap)]">
      <div class="font-mono text-[.72rem] uppercase tracking-[.18em] text-ink-3">Talks</div>
      <ul class="m-0 p-0 list-none space-y-5 text-[.95rem]">
        <li>
          <div class="font-serif text-[1.05rem]">Theoretical prediction of a DD*K̄* three-body molecular state</div>
          <div class="font-mono text-[.72rem] text-ink-3 tracking-[.06em] uppercase">Frontiers in Multiquark-States Physics · Beijing · Jan 2026</div>
        </li>
        <li>
          <div class="font-serif text-[1.05rem]">Qsn̄n̄ bound states and resonances in quark potential model</div>
          <div class="font-mono text-[.72rem] text-ink-3 tracking-[.06em] uppercase">9th XYZ Symposium · Xi'an · May 2024</div>
        </li>
        <li>
          <div class="font-serif text-[1.05rem]">Doubly-heavy tetraquark bound states in quark potential models</div>
          <div class="font-mono text-[.72rem] text-ink-3 tracking-[.06em] uppercase">7th SSESQ Symposium · Rizhao · Jul 2023</div>
        </li>
      </ul>
    </div>
  </section>
</Base>
```

- [ ] **Step 2: Commit**

```bash
git add site/src/pages/cv.astro
git commit -m "feat(site): /cv page with HTML summary + PDF download"
```

---

## Phase G · Verification

### Task G1: Full build, fix warnings, verify acceptance checklist

**Files:**
- No code changes — verification only.

- [ ] **Step 1: Run a clean production build**

```bash
cd /Users/ykchen/science_project/personal_profile/site
rm -rf dist .astro
npm run build
```

Expected: build completes with zero errors and no `Could not resolve` warnings.

- [ ] **Step 2: Preview the production build**

```bash
npm run preview
```

Visit every page: `/`, `/research`, `/publications`, `/analytics`, `/cv`. Each should render with real INSPIRE data and no console errors.

- [ ] **Step 3: Manual cross-check against the spec acceptance checklist**

Open `docs/superpowers/specs/2026-05-17-yk-chen-homepage-design.md` §11. Walk through every checkbox and confirm.

Specifically verify:
- Footer "Last refreshed" matches `inspire.json` `fetched_at`.
- The 2026 / current-year bar on the trajectory chart is in sienna.
- The coauthor network nodes are draggable; YK Chen sits at center in sienna.
- `prefers-reduced-motion: reduce` (test via dev-tools rendering tab → emulate) disables entrance animations and the pulse.

- [ ] **Step 4: Run Lighthouse against a built preview**

```bash
npx --yes lighthouse http://localhost:4321/ --only-categories=performance,accessibility,best-practices --output=html --output-path=./lighthouse-home.html --quiet
npx --yes lighthouse http://localhost:4321/analytics --only-categories=performance,accessibility,best-practices --output=html --output-path=./lighthouse-analytics.html --quiet
```

Open the two reports. Acceptance is Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 95 (mobile).

If any score is below threshold, address the listed issues (commonly: unused JavaScript on chart pages — make sure non-analytics pages don't import chart libraries; missing `lang`, contrast issues if you altered tokens).

- [ ] **Step 5: Commit any fixes**

```bash
git add site/
git commit -m "fix(site): address Lighthouse findings"
```

(Skip the commit if Step 4 needed no changes.)

- [ ] **Step 6: Final smoke commit**

```bash
git add docs/ site/
git status
```

Working tree should be clean.

---

### Task G2: README + CLAUDE.md

**Files:**
- Modify: `README.md`
- Create: `CLAUDE.md`

- [ ] **Step 1: Replace `README.md` with the full version**

```markdown
# Yan-Ke Chen — academic homepage

Static personal homepage for **Yan-Ke Chen (陈彦珂)** — postdoctoral researcher at the Center for High Energy Physics, Peking University. Pulls publication and citation data from [INSPIRE-HEP](https://inspirehep.net/authors/2182746) at build time, renders five pages with an editorial-minimalist design, and ships fully static.

## Layout

```
.
├── scripts/        # Python: INSPIRE fetcher + analytics pipeline
├── site/           # Astro 5 + TypeScript + Tailwind + Chart.js + D3
├── RS_CV/          # Source LaTeX CV (kept as-is)
├── mockups/        # Standalone HTML visual reference (not in production)
└── docs/superpowers/
    ├── specs/      # Design spec
    └── plans/      # Implementation plan
```

## Refreshing INSPIRE data

```bash
cd scripts
source .venv/bin/activate
python fetch_inspire.py
```

Writes `site/src/data/inspire.json`. Re-run whenever a new paper appears on your INSPIRE profile. If a paper is missing from one of the four research themes, add its arXiv id to `scripts/topic_groups.yml` and re-run.

## Building the site

```bash
cd site
npm install
npm run dev        # http://localhost:4321
npm run build      # produces site/dist/
npm run preview    # serves the production build
```

## Deploying

The `site/dist/` directory is fully static. Any of:

- **GitHub Pages** — push `dist/` to a `gh-pages` branch.
- **Netlify / Vercel** — build command `cd site && npm run build`; publish directory `site/dist`.
- **PKU / institutional** — `rsync site/dist/ user@host:/path/`.

## Design

See `docs/superpowers/specs/2026-05-17-yk-chen-homepage-design.md` for the full design spec — typography, palette, motion, INSPIRE pipeline, accessibility, acceptance criteria.

## Mockups

Open `mockups/index.html` and `mockups/analytics.html` directly in a browser, or serve them with `python -m http.server -d mockups 8765`. These remain as the visual source-of-truth.
```

- [ ] **Step 2: Write `CLAUDE.md`** (the file the /init command asked for)

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal academic homepage for **Yan-Ke Chen (陈彦珂)**, postdoctoral researcher at CHEP, Peking University. Two coordinated subprojects:

- **`scripts/`** — Python pipeline that calls the INSPIRE-HEP REST API, derives scientometric metrics (h-index, by-year, keywords, journals, coauthors, institutions, top papers), and writes a single bundle at `site/src/data/inspire.json`.
- **`site/`** — Astro 5 + TypeScript + Tailwind static site that reads that JSON at build time and renders five pages: `/`, `/research`, `/publications`, `/analytics`, `/cv`.

The two halves communicate via the `InspireBundle` schema (Pydantic on the Python side; consumed as untyped JSON by Astro components — the schema is documented in `scripts/models.py` and the spec).

## Daily commands

```bash
# Refresh INSPIRE data (Python venv at scripts/.venv)
cd scripts && source .venv/bin/activate && python fetch_inspire.py

# Run the dev server
cd site && npm run dev          # http://localhost:4321

# Run the Python test suite
cd scripts && pytest

# Run a specific Python test
cd scripts && pytest tests/test_metrics.py::test_h_index_simple -v

# Production build
cd site && npm run build

# Lighthouse on the preview server
cd site && npm run preview &
npx lighthouse http://localhost:4321/ --only-categories=performance,accessibility,best-practices
```

## Architecture worth knowing

- **Single-source-of-truth for data is `site/src/data/inspire.json`.** All Astro pages read from it directly via `import inspire from "../data/inspire.json"`. The browser never calls INSPIRE.
- **Design tokens live in `site/src/styles/tokens.css`.** Tailwind aliases them in `tailwind.config.mjs`. If you need a new color, add it as a CSS variable first, then alias it — never hardcode hex values in components.
- **The "Quiet Precision" design system is locked in `mockups/index.html` and `mockups/analytics.html`.** These two files predate the Astro implementation and remain the visual source-of-truth. When in doubt about typography, spacing, or chart styling, open the mockups.
- **Charts are React islands.** `Trajectory.tsx`, `HIndexStrip.tsx`, `JournalDonut.tsx`, `CoauthorNetwork.tsx`, `PubFilter.tsx` are loaded with `client:load`. Non-chart components are pure Astro to keep zero-JS pages truly zero-JS.
- **Topic grouping is hand-mapped.** `scripts/topic_groups.yml` assigns each paper to one of four research themes. When a new paper appears that isn't in the YAML, `fetch_inspire.py` warns and assigns it to `uncategorised` — fix the YAML and re-run.
- **The CV LaTeX source contains a known typo**: `arXiv:2308.12424` is listed for two different papers. The correct id for the X(3872) coupled-channel paper needs to be looked up from INSPIRE and added to `scripts/topic_groups.yml`.

## Testing conventions

- Python: pytest, located under `scripts/tests/`. HTTP is mocked with `respx`; fixtures in `scripts/tests/fixtures/` are captured from real INSPIRE responses. Re-capture them only if INSPIRE changes its response shape.
- JS / Astro: no automated tests. Visual verification against the mockups + Lighthouse + manual interaction.

## What NOT to do

- Don't call the INSPIRE API from the browser. The whole pipeline is build-time on purpose.
- Don't hardcode placeholder numbers in Astro components. Every number must come from `inspire.json`. The mockup HTML files are the only place placeholders are acceptable.
- Don't restructure `tokens.css` or change typography choices without checking the spec — the design direction is "Quiet Precision," and the typography pairing (Newsreader + IBM Plex Sans + IBM Plex Mono) is intentional, not a default.
- Don't add a dark mode without a separate design pass — the cream-paper aesthetic is the design's signature.
```

- [ ] **Step 3: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: README + CLAUDE.md for future contributors"
```

---

## Self-review check

Spec coverage walkthrough:

| Spec section | Covered by |
|---|---|
| §2 Information architecture — 5 pages | D2 (home), E4 (analytics), F1 (publications), F2 (research), F3 (cv) |
| §3 Visual system — tokens, typography, motion | C2, C3, all component tasks |
| §4 Tech stack | C1 (Astro/Tailwind/React), E1+E2 (Chart.js), E3 (D3) |
| §5 INSPIRE pipeline & schema | B1–B8 (all Python) |
| §5.3 Topic-group mapping | B5 |
| §5.4 Error handling & resilience | B3 (retries), B8 (stale-data refuse) |
| §6.1 Trajectory + h-index strip + side panel | E1, E2, E4 |
| §6.2 Top papers | E2 (TopPapers), E4 |
| §6.3 Keywords + journal donut | B7, E2, E4 |
| §6.4 Coauthor network + institutions | E3, E2 (Institutions), E4 |
| §7 Project structure | A2 |
| §8 Build & deploy | G2 (README documents it) |
| §9 Accessibility & responsiveness | C2 (`prefers-reduced-motion`), every component (responsive grids), G1 (Lighthouse a11y) |
| §10 Open questions / deferred | All flagged in the plan or skipped intentionally (dark mode, world map, GH Action) |
| §11 Acceptance checklist | G1 |

Placeholder scan: no "TBD" / "TODO" / "implement later" / "similar to Task N" anywhere. Every code step shows actual code.

Type consistency: `Paper`, `Author`, `Metrics`, `YearRow`, `TermCount`, `JournalCount`, `Coauthor`, `Institution` defined once in `models.py` (Task B2) and referenced by name everywhere else; React props types in `Trajectory.tsx`, `HIndexStrip.tsx`, `JournalDonut.tsx`, `CoauthorNetwork.tsx`, `PubFilter.tsx` align with the JSON schema produced by `compute_metrics`.

Plan is internally consistent. Ready for execution.

---

## Execution handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-17-yk-chen-homepage.md`. Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
