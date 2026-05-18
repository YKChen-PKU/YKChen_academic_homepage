"""Pydantic schema for the inspire.json bundle written by fetch_inspire.py."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Author(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    is_you: bool = False
    inspire_id: Optional[str] = None


class Venue(BaseModel):
    model_config = ConfigDict(extra="ignore")
    journal: Optional[str] = None
    volume: Optional[str] = None
    page: Optional[str] = None
    year: Optional[int] = None


class Paper(BaseModel):
    model_config = ConfigDict(extra="ignore")
    inspire_id: str
    title: str
    authors: List[Author]
    venue: Venue
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    citations: int = 0
    citations_no_self: int = 0
    year: Optional[int] = None
    topic_group: str = "uncategorised"


class Position(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rank: Optional[str] = None
    institution: Optional[str] = None
    start: Optional[str] = None


class AuthorProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    name_zh: Optional[str] = None
    current_position: Optional[Position] = None
    orcid: Optional[str] = None
    arxiv: Optional[str] = None


class YearRow(BaseModel):
    year: int
    papers: int
    cum_citations: int
    h_index: int


class TermCount(BaseModel):
    term: str
    count: int


class JournalCount(BaseModel):
    name: str
    count: int


class Coauthor(BaseModel):
    name: str
    joint_papers: int
    inspire_id: Optional[str] = None
    current_institution: Optional[str] = None


class Institution(BaseModel):
    name: str
    city: Optional[str] = None
    joint_papers: int


class Metrics(BaseModel):
    papers_total: int
    citations_total: int
    h_index: int
    first_author_count: int
    by_year: List[YearRow]
    top_papers: List[Paper]
    keywords: List[TermCount]
    journals: List[JournalCount]
    coauthors: List[Coauthor]
    institutions: List[Institution]


class InspireBundle(BaseModel):
    fetched_at: datetime
    author: AuthorProfile
    papers: List[Paper]
    metrics: Metrics
