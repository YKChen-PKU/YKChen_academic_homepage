"""Translate raw INSPIRE literature JSON records into Paper instances."""
from __future__ import annotations

from typing import Any, Optional

from scripts.models import Author, AuthorPosition, JournalRef, Paper

YK_BAI = 'Yan.Ke.Chen.1'   # INSPIRE BAI identifier — primary lookup key
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
    year = pub.get('year') or 0
    jref: Optional[JournalRef] = None
    if pub.get('journal_title'):
        jref = JournalRef(
            name=pub.get('journal_title'),
            volume=(str(pub.get('journal_volume'))
                    if pub.get('journal_volume') is not None else None),
            page=(str(pub.get('page_start'))
                  if pub.get('page_start') is not None else None),
            year=year,
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
