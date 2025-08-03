"""
Vienna and Austrian context Pydantic models for PlexMCP.

This module contains models related to Vienna-specific content and recommendations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class WienerRecommendation(BaseModel):
    """Vienna-context content recommendation"""
    media_key: str = Field(description="Media key/ID")
    title: str = Field(description="Media title")
    type: str = Field(description="Media type (movie, show, episode)")
    year: Optional[int] = Field(description="Release year")
    duration: Optional[int] = Field(description="Duration in minutes")
    rating: Optional[float] = Field(description="Rating if available")
    vienna_score: float = Field(description="Vienna context relevance score")
    mood_match: str = Field(description="Mood category match")
    austrian_context: Optional[str] = Field(
        description="Austrian cultural relevance"
    )
    recommendation_reason: str = Field(
        description="Why this content fits Vienna context"
    )
    best_time: str = Field(description="Optimal viewing time context")


class EuropeanContent(BaseModel):
    """European content discovery result"""
    media_key: str = Field(description="Media key/ID")
    title: str = Field(description="Original title")
    local_title: Optional[str] = Field(description="Local/translated title")
    country: str = Field(description="Country of origin")
    language: str = Field(description="Primary language")
    subtitles: List[str] = Field(description="Available subtitle languages")
    genre: str = Field(description="Genre category")
    year: Optional[int] = Field(description="Release year")
    rating: Optional[float] = Field(description="Rating if available")
    cultural_significance: Optional[str] = Field(
        description="Cultural or historical importance"
    )
    eu_funding: bool = Field(description="EU co-production or funding")
    awards: List[str] = Field(description="European film awards received")
    availability_score: float = Field(
        description="How easily available in Austria"
    )


class AnimeSeasonInfo(BaseModel):
    """Anime season information for weebs"""
    title: str = Field(description="Anime title")
    year: int = Field(description="Release year")
    season: Optional[str] = Field(description="Season (Winter, Spring, Summer, Fall)")
    episodes_available: int = Field(description="Episodes available in library")
    rating: Optional[float] = Field(description="Rating if available")
    summary: Optional[str] = Field(description="Brief summary")
    status: str = Field(description="Airing status (ongoing, completed, etc)")
