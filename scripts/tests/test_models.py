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
