"""CLI entry point: fetch INSPIRE → derive metrics → write inspire.json."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from scripts.derive_metrics import derive_metrics
from scripts.inspire_client import InspireClient, InspireError
from scripts.models import InspireBundle
from scripts.parsers import parse_paper

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / 'site' / 'src' / 'data' / 'inspire.json'
THEMES_PATH = ROOT / 'site' / 'src' / 'data' / 'themes.yaml'
DEFAULT_RECID = '2182746'


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Refresh INSPIRE data for the homepage.')
    ap.add_argument('--recid', default=DEFAULT_RECID, help='INSPIRE author recid')
    ap.add_argument('--no-cache', action='store_true', help='Bypass disk cache')
    args = ap.parse_args(argv)

    cache = None if args.no_cache else ROOT / 'scripts' / '.cache' / 'inspire'
    client = InspireClient(cache_dir=cache)

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

    total_cites = sum(p.citation_count for p in papers)
    print(f'Wrote {OUT_PATH} — {len(papers)} papers, {total_cites} citations.')
    if metrics.top_cited:
        print('Top cited:')
        for i, p in enumerate(metrics.top_cited[:5], 1):
            print(f'  {i}. ({p.citation_count}) {p.title[:70]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
