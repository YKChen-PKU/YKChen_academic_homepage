"""Thin INSPIRE-HEP REST client. Synchronous httpx. Used only at build time."""
from __future__ import annotations

import time
from typing import Any, Iterator, Optional

import httpx

from models import AuthorProfile, Position


INSPIRE_BASE = "https://inspirehep.net/api"
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
THROTTLE_SECONDS = 0.10


class InspireClient:
    """Wraps INSPIRE REST endpoints with simple retry + throttling."""

    def __init__(self, base_url: str = INSPIRE_BASE) -> None:
        self.base_url = base_url
        self._client = httpx.Client(timeout=DEFAULT_TIMEOUT, headers={"Accept": "application/json"})

    def __enter__(self) -> "InspireClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self._client.close()

    def _get(self, url: str, *, params: Optional[dict] = None, max_retries: int = 3) -> dict:
        last_exc: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                r = self._client.get(url, params=params)
                r.raise_for_status()
                time.sleep(THROTTLE_SECONDS)
                return r.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                time.sleep(2 ** attempt)
        assert last_exc is not None
        raise RuntimeError(f"INSPIRE GET failed after {max_retries} retries: {url}") from last_exc

    def fetch_author(self, author_id: str) -> AuthorProfile:
        raw = self._get(f"{self.base_url}/authors/{author_id}")
        md = raw.get("metadata", {})

        name = (md.get("name") or {}).get("value", "")
        # native names are an array of {value, source}
        native_names = (md.get("name") or {}).get("native_names") or []
        name_zh = native_names[0] if native_names else None

        # current position = first positions entry with `current: True`
        positions = md.get("positions") or []
        cur = next((p for p in positions if p.get("current")), None)
        position = None
        if cur:
            position = Position(
                rank=cur.get("rank"),
                institution=cur.get("institution"),
                start=cur.get("start_date"),
            )

        ids = md.get("ids") or []
        orcid = next((x.get("value") for x in ids if x.get("schema") == "ORCID"), None)
        arxiv = next((x.get("value") for x in ids if x.get("schema") == "ARXIV"), None)

        return AuthorProfile(
            id=author_id,
            name=name,
            name_zh=name_zh,
            current_position=position,
            orcid=orcid,
            arxiv=arxiv,
        )
