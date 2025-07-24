"""
Data models for social media posts.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class Post:
    """
    Unified data model for social media posts from Reddit and Twitter.
    """
    id: str
    source: str  # "Reddit" or "Twitter"
    content: str
    author: str
    created_at: datetime
    url: str
    engagement_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    relevance_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Post to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source": self.source,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "url": self.url,
            "engagement_score": self.engagement_score,
            "metadata": self.metadata,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "relevance_score": self.relevance_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Post":
        """Create Post from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()
        
        return cls(
            id=data.get("id", ""),
            source=data.get("source", ""),
            content=data.get("content", ""),
            author=data.get("author", ""),
            created_at=created_at,
            url=data.get("url", ""),
            engagement_score=data.get("engagement_score", 0.0),
            metadata=data.get("metadata", {}),
            summary=data.get("summary"),
            sentiment=data.get("sentiment"),
            relevance_score=data.get("relevance_score")
        )
    
    def get_display_content(self, max_length: int = 500) -> str:
        """Get truncated content for display."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def get_engagement_display(self) -> str:
        """Get formatted engagement information."""
        if self.source == "Reddit":
            score = self.metadata.get("score", 0)
            comments = self.metadata.get("num_comments", 0)
            return f"↑ {score} • 💬 {comments}"
        elif self.source == "Twitter":
            likes = self.metadata.get("likes", 0)
            retweets = self.metadata.get("retweets", 0)
            replies = self.metadata.get("replies", 0)
            return f"❤️ {likes} • 🔄 {retweets} • 💬 {replies}"
        else:
            return f"Score: {self.engagement_score:.1f}"
    
    def get_time_display(self) -> str:
        """Get human-readable time display."""
        now = datetime.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"


class ProcessedQuery(BaseModel):
    """
    Model for processed query information.
    """
    original_query: str
    keywords: list[str]
    search_reddit: bool
    search_twitter: bool
    filters: Dict[str, Any]
    intent: str
    sentiment_filter: str = "any"
    
    class Config:
        extra = "allow"


class SearchResult(BaseModel):
    """
    Model for search results from providers.
    """
    posts: list[Post]
    total_found: int
    source: str
    query_time_ms: float
    
    class Config:
        arbitrary_types_allowed = True
