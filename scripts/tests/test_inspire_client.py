import json
from pathlib import Path

import httpx
import pytest
import respx

from scripts.inspire_client import InspireClient, InspireError

FIXTURE_AUTHOR = json.loads(
    (Path(__file__).parent / 'fixtures' / 'author_2182746.json').read_text()
)


@respx.mock
def test_fetch_author_parses_name_and_affiliation():
    respx.get('https://inspirehep.net/api/authors/2182746').mock(
        return_value=httpx.Response(200, json=FIXTURE_AUTHOR)
    )
    client = InspireClient(cache_dir=None)
    profile = client.fetch_author('2182746')
    assert profile.recid == '2182746'
    assert profile.name == 'Yan-Ke Chen'
    assert profile.current_affiliation == 'Peking U.'


@respx.mock
def test_fetch_author_retries_on_502():
    route = respx.get('https://inspirehep.net/api/authors/2182746').mock(
        side_effect=[
            httpx.Response(502, json={}),
            httpx.Response(200, json=FIXTURE_AUTHOR),
        ]
    )
    client = InspireClient(cache_dir=None, retry_base_delay=0.0)
    profile = client.fetch_author('2182746')
    assert profile.name == 'Yan-Ke Chen'
    assert route.call_count == 2


@respx.mock
def test_fetch_author_raises_after_max_retries():
    respx.get('https://inspirehep.net/api/authors/2182746').mock(
        return_value=httpx.Response(503, json={})
    )
    client = InspireClient(cache_dir=None, max_retries=2, retry_base_delay=0.0)
    with pytest.raises(InspireError, match='5xx|503'):
        client.fetch_author('2182746')


@respx.mock
def test_fetch_author_works_paginates():
    base = 'https://inspirehep.net/api/literature'
    # page 1: 250 hits
    respx.get(base, params__contains={'page': '1'}).mock(
        return_value=httpx.Response(200, json={
            'hits': {
                'total': 251,
                'hits': [
                    {'metadata': {'arxiv_eprints': [{'value': str(i)}]}}
                    for i in range(250)
                ],
            },
        })
    )
    # page 2: 1 hit
    respx.get(base, params__contains={'page': '2'}).mock(
        return_value=httpx.Response(200, json={
            'hits': {
                'total': 251,
                'hits': [{'metadata': {'arxiv_eprints': [{'value': '999'}]}}],
            },
        })
    )
    client = InspireClient(cache_dir=None)
    raw = client.fetch_author_works('2182746')
    assert len(raw) == 251


def test_cache_round_trip(tmp_path):
    cache = tmp_path / 'cache'
    with respx.mock:
        respx.get('https://inspirehep.net/api/authors/2182746').mock(
            return_value=httpx.Response(200, json=FIXTURE_AUTHOR)
        )
        InspireClient(cache_dir=cache).fetch_author('2182746')
    # second call: no mock active — cache must serve it
    profile = InspireClient(cache_dir=cache).fetch_author('2182746')
    assert profile.name == 'Yan-Ke Chen'
