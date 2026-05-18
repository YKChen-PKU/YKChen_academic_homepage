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
            author_position='last_first',
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
