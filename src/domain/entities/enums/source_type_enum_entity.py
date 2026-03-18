from enum import Enum


class SourceType(Enum):
    """Enum for external sources."""

    YOUTUBE = "youtube"
    ARTICLE = "article"
    PDF = "pdf"
    WIKIPEDIA = "wikipedia"
