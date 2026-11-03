"""Pure functions that turn a list[Paper] into DerivedMetrics."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, cast

from scripts.models import (
    AuthorPosition, CoauthorEdge, CoauthorGraph, CoauthorNode,
    DerivedMetrics, Paper, PaperRef, TreemapNode,
)


# -------- per-chart helpers --------------------------------------------------

def papers_per_year(papers: Iterable[Paper]) -> dict[int, dict[AuthorPosition, int]]:
    out: dict[int, dict[AuthorPosition, int]] = defaultdict(
        lambda: {'first': 0, 'middle': 0, 'last': 0, 'sole': 0}
    )
    for p in papers:
        out[p.year][p.author_position] += 1
    return dict(out)


def author_position_total(papers: Iterable[Paper]) -> dict[AuthorPosition, int]:
    out: dict[AuthorPosition, int] = {'first': 0, 'middle': 0, 'last': 0, 'sole': 0}
    for p in papers:
        out[p.author_position] += 1
    return out


def cumulative_citations(papers: Iterable[Paper]) -> dict[int, int]:
    """Cumulative citation total at end of each year.

    Approximation: citations attributed to the paper's publication year.
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
    """h-index calculated at the end of each year given today's citation counts."""
    plist = sorted(papers, key=lambda p: p.year)
    if not plist:
        return {}
    out: dict[int, int] = {}
    last_year = plist[-1].year
    first_year = plist[0].year
    for y in range(first_year, last_year + 1):
        through_year = sorted(
            (p.citation_count for p in plist if p.year <= y), reverse=True
        )
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
                key = cast(tuple[str, str], tuple(sorted((a.name, b.name))))
                cross_pairs[key] += 1
    nodes = [
        CoauthorNode(name=name, papers_with_yk=count, inspire_id=bai.get(name))
        for name, count in sorted(yk_pairs.items(), key=lambda kv: -kv[1])
    ]
    edges = [CoauthorEdge(source=a, target=b, weight=w)
             for (a, b), w in cross_pairs.items()]
    return CoauthorGraph(nodes=nodes, edges=edges)


def treemap(papers: Iterable[Paper]) -> TreemapNode:
    """Group by theme_slug → arxiv category → individual paper."""
    grouped: dict[str, dict[str, list[Paper]]] = defaultdict(lambda: defaultdict(list))
    for p in papers:
        theme = p.theme_slug or 'untagged'
        cat = (p.arxiv_categories or ['hep-ph'])[0]
        grouped[theme][cat].append(p)
    return TreemapNode(name='root', children=[
        TreemapNode(name=theme, children=[
            TreemapNode(name=cat, children=[
                TreemapNode(name=p.title[:48], value=1) for p in paps
            ]) for cat, paps in cats.items()
        ]) for theme, cats in grouped.items()
    ])


# -------- top-level ---------------------------------------------------------

def derive_metrics(papers: list[Paper]) -> DerivedMetrics:
    return DerivedMetrics(
        papers_per_year=papers_per_year(papers),
        citations_per_year=citations_per_year(papers),
        citations_per_year_method='approximate',
        cumulative_citations=cumulative_citations(papers),
        h_index_curve=h_index_curve(papers),
        author_position_total=author_position_total(papers),
        top_cited=top_cited(papers, n=8),
        journal_split=journal_split(papers),
        coauthor_graph=coauthor_graph(papers),
        treemap=treemap(papers),
    )
