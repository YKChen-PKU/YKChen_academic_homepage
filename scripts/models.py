"""Pydantic schema for the INSPIRE bundle written to inspire.json."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AuthorPosition = Literal['first', 'middle', 'last', 'sole']


class Author(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    is_yk: bool = False
    inspire_id: Optional[str] = None


class AuthorProfile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    recid: str
    name: str
    current_affiliation: Optional[str] = None
    orcid: Optional[str] = None


class JournalRef(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    volume: Optional[str] = None
    page: Optional[str] = None
    year: int


class Paper(BaseModel):
    model_config = ConfigDict(extra='forbid')
    arxiv_id: str
    inspire_id: str
    title: str
    authors: list[Author]
    year: int
    journal_ref: Optional[JournalRef]
    doi: Optional[str]
    citation_count: int = 0
    arxiv_categories: list[str] = Field(default_factory=list)
    author_position: AuthorPosition
    theme_slug: Optional[str] = None

    @property
    def is_yk_first(self) -> bool:
        return self.author_position in ('first', 'sole')


class CoauthorNode(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    papers_with_yk: int
    inspire_id: Optional[str] = None


class CoauthorEdge(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: str
    target: str
    weight: int


class CoauthorGraph(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nodes: list[CoauthorNode]
    edges: list[CoauthorEdge]


class TreemapNode(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    value: Optional[int] = None
    children: Optional[list['TreemapNode']] = None


class PaperRef(BaseModel):
    model_config = ConfigDict(extra='forbid')
    arxiv_id: str
    inspire_id: str
    title: str
    citation_count: int


class DerivedMetrics(BaseModel):
    model_config = ConfigDict(extra='forbid')
    papers_per_year: dict[int, dict[AuthorPosition, int]]
    citations_per_year: dict[int, int]
    citations_per_year_method: Literal['exact', 'approximate']
    cumulative_citations: dict[int, int]
    h_index_curve: dict[int, int]
    author_position_total: dict[AuthorPosition, int]
    top_cited: list[PaperRef]
    journal_split: dict[str, int]
    coauthor_graph: CoauthorGraph
    treemap: TreemapNode

    @classmethod
    def empty(cls) -> 'DerivedMetrics':
        return cls(
            papers_per_year={},
            citations_per_year={},
            citations_per_year_method='approximate',
            cumulative_citations={},
            h_index_curve={},
            author_position_total={'first': 0, 'middle': 0, 'last': 0, 'sole': 0},
            top_cited=[],
            journal_split={},
            coauthor_graph=CoauthorGraph(nodes=[], edges=[]),
            treemap=TreemapNode(name='root', children=[]),
        )


class InspireBundle(BaseModel):
    model_config = ConfigDict(extra='forbid')
    fetched_at: datetime
    author: AuthorProfile
    papers: list[Paper]
    metrics: DerivedMetrics
    themes: dict[str, list[str]]
