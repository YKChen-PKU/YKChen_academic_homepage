import json
from pathlib import Path
from scripts.parsers import parse_paper, YK_BAI

FIXTURES = json.loads(
    (Path(__file__).parent / 'fixtures' / 'literature_sample.json').read_text()
)


def test_parse_yk_first_author():
    p = parse_paper(FIXTURES[0])
    assert p.arxiv_id == '2009.01182'
    assert p.inspire_id == '2761091'
    assert p.title.startswith('Branching fractions of $B^-')
    assert p.year == 2021
    assert p.author_position == 'first'
    assert p.is_yk_first
    assert p.journal_ref is not None and p.journal_ref.name == 'Eur. Phys. J. C'
    assert p.doi is not None and p.doi.startswith('10.1140')
    assert p.citation_count == 21
    yk = [a for a in p.authors if a.is_yk]
    assert len(yk) == 1 and yk[0].name == 'Chen, Yan-Ke'


def test_parse_yk_middle_author():
    p = parse_paper(FIXTURES[1])
    assert p.author_position == 'middle'
    assert not p.is_yk_first


def test_yk_bai_constant_matches_inspire():
    assert YK_BAI == 'Yan.Ke.Chen.1'


def test_parse_prefers_arxiv_sourced_title_over_mathml():
    raw = {
        'id': '999',
        'metadata': {
            'titles': [
                {'source': 'APS', 'title': 'Uncovering <math><mi>X</mi></math>'},
                {'source': 'arXiv', 'title': 'Uncovering $X(3872)$'},
            ],
            'authors': [{'full_name': 'Chen, Yan-Ke',
                         'ids': [{'schema': 'INSPIRE BAI', 'value': 'Yan.Ke.Chen.1'}]}],
            'arxiv_eprints': [{'value': '2404.16575', 'categories': ['hep-ph']}],
            'preprint_date': '2024-04-25',
        },
    }
    p = parse_paper(raw)
    assert p.title == 'Uncovering $X(3872)$'


def test_parse_falls_back_to_preprint_date_when_no_pub_info():
    raw = {
        'id': '999',
        'metadata': {
            'titles': [{'source': 'arXiv', 'title': 'Preprint title'}],
            'authors': [{'full_name': 'Chen, Yan-Ke',
                         'ids': [{'schema': 'INSPIRE BAI', 'value': 'Yan.Ke.Chen.1'}]}],
            'arxiv_eprints': [{'value': '2602.12010', 'categories': ['hep-ph']}],
            'preprint_date': '2026-02-15',
        },
    }
    p = parse_paper(raw)
    assert p.year == 2026
    assert p.journal_ref is None


def test_swapped_bai_does_not_misidentify_dian_yong_chen():
    """Real bug from arXiv:2302.01696 — INSPIRE has BAIs swapped between
    Chen, Yan-Ke and Chen, Dian-Yong. Name-only matching avoids the trap.
    """
    raw = {
        'id': '999',
        'metadata': {
            'titles': [{'source': 'arXiv', 'title': 'Hunting for hidden-charm'}],
            'authors': [
                {'full_name': 'Wu, Qi'},
                # Real Yan-Ke, but INSPIRE put Dian-Yong's BAI on him
                {'full_name': 'Chen, Yan-Ke',
                 'ids': [{'schema': 'INSPIRE BAI', 'value': 'Dian.Yong.Chen.1'}]},
                {'full_name': 'Li, Gang'},
                {'full_name': 'Liu, Shi-Dong'},
                # Real Dian-Yong, but INSPIRE put Yan-Ke's BAI on him
                {'full_name': 'Chen, Dian-Yong',
                 'ids': [{'schema': 'INSPIRE BAI', 'value': 'Yan.Ke.Chen.1'}]},
            ],
            'arxiv_eprints': [{'value': '2302.01696', 'categories': ['hep-ph']}],
            'publication_info': [{'journal_title': 'Phys. Rev. D', 'year': 2023}],
        },
    }
    p = parse_paper(raw)
    yks = [a for a in p.authors if a.is_yk]
    assert len(yks) == 1
    assert yks[0].name == 'Chen, Yan-Ke'
    # Position should be 'middle' (index 1 of 5), not 'last'
    assert p.author_position == 'middle'


def test_parse_year_from_arxiv_id_when_no_dates():
    raw = {
        'id': '999',
        'metadata': {
            'titles': [{'source': 'arXiv', 'title': 'T'}],
            'authors': [{'full_name': 'Chen, Yan-Ke',
                         'ids': [{'schema': 'INSPIRE BAI', 'value': 'Yan.Ke.Chen.1'}]}],
            'arxiv_eprints': [{'value': '2310.13354', 'categories': ['hep-ph']}],
        },
    }
    p = parse_paper(raw)
    assert p.year == 2023
