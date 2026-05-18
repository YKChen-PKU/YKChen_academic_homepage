"""Translate raw INSPIRE literature JSON records into Paper instances."""
from __future__ import annotations

from typing import Any, Optional

from scripts.models import Author, AuthorPosition, JournalRef, Paper

YK_BAI = 'Yan.Ke.Chen.1'   # YK's INSPIRE BAI — used by tests; NOT a trust anchor


def _is_yk(raw_author: dict[str, Any]) -> bool:
    """Identify YK by name only.

    INSPIRE BAI assignments are occasionally swapped between similarly-named
    authors (observed on arXiv:2302.01696 where Chen, Yan-Ke and Chen, Dian-Yong
    have each other's BAIs). Names with 'Yan-Ke' are unique enough in hep-ph
    that name matching is more reliable than BAI matching.
    """
    name = raw_author.get('full_name', '')
    return 'Yan-Ke' in name or name in ('Y. K. Chen', 'Y.K. Chen')


def _pick_title(titles: list[dict[str, Any]]) -> str:
    """Prefer the arXiv-sourced title (raw LaTeX). Fall back to publisher.

    INSPIRE often stores multiple title entries — the arXiv submission uses
    LaTeX `$...$` while publisher entries (APS, Elsevier) use rendered MathML.
    KaTeX expects LaTeX, so arXiv-sourced is the right pick for our renderer.
    """
    arxiv_titles = [t for t in titles if t.get('source') == 'arXiv']
    chosen = arxiv_titles[0] if arxiv_titles else (titles[0] if titles else {})
    return chosen.get('title', '')


def _year_from_preprint_date(date: Optional[str]) -> Optional[int]:
    if not date:
        return None
    try:
        return int(date[:4])
    except ValueError:
        return None


def _year_from_arxiv_id(arxiv_id: str) -> Optional[int]:
    """arXiv IDs after 2007 are YYMM.NNNNN — first two digits → year."""
    if not arxiv_id or len(arxiv_id) < 4 or '.' not in arxiv_id:
        return None
    head = arxiv_id.split('.', 1)[0]
    if len(head) != 4 or not head.isdigit():
        return None
    yy = int(head[:2])
    return 2000 + yy


def parse_paper(raw: dict[str, Any]) -> Paper:
    meta = raw.get('metadata', {})
    arxiv = (meta.get('arxiv_eprints') or [{}])[0]
    arxiv_id = arxiv.get('value', '')
    categories: list[str] = list(arxiv.get('categories') or [])

    title = _pick_title(meta.get('titles') or [])

    authors_raw = meta.get('authors') or []
    authors: list[Author] = []
    yk_index: Optional[int] = None
    for i, a in enumerate(authors_raw):
        yk = _is_yk(a)
        if yk:
            yk_index = i
        bai = next(
            (x.get('value') for x in (a.get('ids') or [])
             if x.get('schema') == 'INSPIRE BAI'),
            None,
        )
        authors.append(Author(name=a.get('full_name', ''), is_yk=yk, inspire_id=bai))

    position: AuthorPosition
    if yk_index is None:
        position = 'middle'
    elif len(authors) == 1:
        position = 'sole'
    elif yk_index == 0:
        position = 'first'
    elif yk_index == len(authors) - 1:
        position = 'last'
    else:
        position = 'middle'

    pub = (meta.get('publication_info') or [{}])[0]
    year = pub.get('year') or _year_from_preprint_date(meta.get('preprint_date')) \
        or _year_from_arxiv_id(arxiv_id) or 0
    jref: Optional[JournalRef] = None
    if pub.get('journal_title'):
        jref = JournalRef(
            name=pub.get('journal_title'),
            volume=(str(pub.get('journal_volume'))
                    if pub.get('journal_volume') is not None else None),
            page=(str(pub.get('page_start'))
                  if pub.get('page_start') is not None else None),
            year=pub.get('year') or year,
        )

    doi: Optional[str] = None
    for d in meta.get('dois') or []:
        if d.get('value'):
            doi = d['value']
            break

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
