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
