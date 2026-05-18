from scripts.models import Author, JournalRef, Paper
from scripts.derive_metrics import (
    derive_metrics, papers_per_year, h_index_curve,
    coauthor_graph, top_cited,
)


def _make_paper(year: int, position='first', cites=10, journal='Phys. Rev. D',
                arxiv='0000.00000', inspire_id='1', authors=None) -> Paper:
    if authors is None:
        authors = [
            Author(name='Y. K. Chen', is_yk=True),
            Author(name='L. Meng', is_yk=False),
        ]
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
    assert curve[max(years)] >= 2


def test_coauthor_graph_excludes_yk_self_loop():
    p = _make_paper(2024)
    g = coauthor_graph([p])
    names = {n.name for n in g.nodes}
    assert 'L. Meng' in names
    assert 'Y. K. Chen' not in names
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
