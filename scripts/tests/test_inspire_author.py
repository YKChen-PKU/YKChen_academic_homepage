import json
from pathlib import Path

import respx
from httpx import Response

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspire_client import InspireClient


FIXTURE = json.loads(Path(__file__).parent.joinpath("fixtures/author_2182746.json").read_text())


@respx.mock
def test_fetch_author_parses_name_and_position():
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
