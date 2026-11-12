"""Synchronous INSPIRE-HEP REST client with retry, throttle, and disk cache."""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import httpx

from scripts.models import AuthorProfile

log = logging.getLogger(__name__)

INSPIRE_BASE = 'https://inspirehep.net/api'
USER_AGENT = 'yan-ke-chen-homepage/0.1 (+mailto:chenyanke@pku.edu.cn)'


class InspireError(RuntimeError):
    """Raised when INSPIRE returns an unrecoverable error."""


class InspireClient:
    """Thin synchronous client over the INSPIRE REST API."""

    def __init__(
        self,
        cache_dir: Optional[Path | str] = Path('scripts/.cache/inspire'),
        max_retries: int = 5,
        retry_base_delay: float = 2.0,
        throttle_seconds: float = 1.0,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.throttle_seconds = throttle_seconds
        self._last_call_at = 0.0
        self._http = httpx.Client(
            headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'},
            timeout=httpx.Timeout(30.0, connect=10.0),
        )

    # ----- public API --------------------------------------------------------

    def fetch_author(self, recid: str) -> AuthorProfile:
        data = self._get_json(f'/authors/{recid}')
        meta = data.get('metadata', {})
        name = (meta.get('name', {}).get('preferred_name')
                or meta.get('name', {}).get('value', ''))
        affil = None
        for pos in meta.get('positions') or []:
            if pos.get('current'):
                affil = pos.get('institution')
                break
        orcid = None
        for ident in meta.get('ids') or []:
            if ident.get('schema') == 'ORCID':
                orcid = ident.get('value')
        return AuthorProfile(recid=recid, name=name, current_affiliation=affil, orcid=orcid)

    def fetch_author_works(self, recid: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        page = 1
        page_size = 250
        while True:
            data = self._get_json(
                '/literature',
                params={
                    'q': f'authors.recid:{recid}',
                    'sort': 'mostrecent',
                    'size': page_size,
                    'page': page,
                    'fields': ','.join([
                        'titles', 'authors', 'arxiv_eprints', 'publication_info',
                        'dois', 'citation_count', 'first_author', 'collaborations',
                        'preprint_date', 'inspire_categories',
                    ]),
                },
            )
            hits = (data.get('hits') or {}).get('hits') or []
            out.extend(hits)
            total = (data.get('hits') or {}).get('total') or 0
            if page * page_size >= total or not hits:
                return out
            page += 1

    # ----- internals ---------------------------------------------------------

    def _get_json(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        cache_key = self._cache_key(path, params)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached
        body = self._request_with_retries(path, params)
        self._write_cache(cache_key, body)
        return body

    def _request_with_retries(self, path: str, params: Optional[dict]) -> dict[str, Any]:
        url = f'{INSPIRE_BASE}{path}'
        last_status = 0
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            r = self._http.get(url, params=params)
            last_status = r.status_code
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429 or 500 <= r.status_code < 600:
                delay = self.retry_base_delay * (2 ** (attempt - 1))
                log.warning('INSPIRE %s on %s — retry %d/%d in %.1fs',
                            r.status_code, url, attempt, self.max_retries, delay)
                time.sleep(delay)
                continue
            raise InspireError(f'INSPIRE {r.status_code} on {url}: {r.text[:200]}')
        raise InspireError(
            f'INSPIRE {last_status} (5xx/429) on {url} after {self.max_retries} attempts')

    def _throttle(self) -> None:
        delta = time.monotonic() - self._last_call_at
        if delta < self.throttle_seconds:
            time.sleep(self.throttle_seconds - delta)
        self._last_call_at = time.monotonic()

    def _cache_key(self, path: str, params: Optional[dict]) -> Optional[Path]:
        if not self.cache_dir:
            return None
        raw = json.dumps({'p': path, 'q': params}, sort_keys=True)
        digest = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return self.cache_dir / f'{digest}.json'

    def _read_cache(self, key: Optional[Path]) -> Optional[dict[str, Any]]:
        if key and key.is_file():
            return json.loads(key.read_text())
        return None

    def _write_cache(self, key: Optional[Path], body: dict[str, Any]) -> None:
        if key:
            key.write_text(json.dumps(body))
