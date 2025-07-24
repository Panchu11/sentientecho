"""
Reddit Provider for fetching posts using Pushshift.io API.
"""

import asyncio
from typing import List, Optional, Dict, Any
import httpx
from datetime import datetime, timedelta
import json

from ..models.post import Post
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RedditProvider:
    """
    Reddit Provider using Pushshift.io API for comprehensive Reddit search.
    
    Provides access to Reddit posts and comments with filtering capabilities.
    """
    
    def __init__(self, max_results: int = 10):
        """Initialize the Reddit provider."""
        self.max_results = max_results
        self.base_url = "https://api.pushshift.io/reddit/search/submission"
        
        # HTTP client with timeout and retries
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        logger.info(f"Initialized Reddit provider with max_results: {max_results}")
    
    async def search_posts(
        self,
        keywords: List[str],
        subreddit: Optional[str] = None,
        time_range: str = "week",
        min_score: int = 1
    ) -> List[Post]:
        """
        Search Reddit posts using Pushshift API.
        
        Args:
            keywords: List of keywords to search for
            subreddit: Specific subreddit to search (optional)
            time_range: Time range for search (day, week, month, year)
            min_score: Minimum score threshold
            
        Returns:
            List of Post objects
        """
        try:
            # Calculate time range
            time_filter = self._get_time_filter(time_range)
            
            # Build search query
            query = " ".join(keywords)
            
            params = {
                "q": query,
                "size": self.max_results,
                "sort": "score",
                "sort_type": "desc",
                "after": time_filter,
                "score": f">{min_score}",
                "fields": "id,title,selftext,author,created_utc,score,num_comments,subreddit,url,permalink"
            }
            
            if subreddit:
                params["subreddit"] = subreddit
            
            logger.info(f"Searching Reddit with query: {query}, subreddit: {subreddit}")
            
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            if "data" in data:
                for item in data["data"]:
                    try:
                        post = self._parse_reddit_post(item)
                        if post:
                            posts.append(post)
                    except Exception as e:
                        logger.warning(f"Error parsing Reddit post: {e}")
                        continue
            
            logger.info(f"Found {len(posts)} Reddit posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []
    
    def _parse_reddit_post(self, item: Dict[str, Any]) -> Optional[Post]:
        """
        Parse a Reddit post from Pushshift API response.
        
        Args:
            item: Raw post data from API
            
        Returns:
            Post object or None if parsing fails
        """
        try:
            # Combine title and selftext for content
            title = item.get("title", "")
            selftext = item.get("selftext", "")
            content = f"{title}\n\n{selftext}".strip()
            
            # Skip if no meaningful content
            if len(content.strip()) < 10:
                return None
            
            # Calculate engagement score
            score = item.get("score", 0)
            num_comments = item.get("num_comments", 0)
            engagement_score = score + (num_comments * 0.5)  # Weight comments less than upvotes
            
            # Create Post object
            post = Post(
                id=item.get("id", ""),
                source="Reddit",
                content=content,
                author=f"u/{item.get('author', 'unknown')}",
                created_at=datetime.fromtimestamp(item.get("created_utc", 0)),
                url=f"https://reddit.com{item.get('permalink', '')}",
                engagement_score=engagement_score,
                metadata={
                    "subreddit": item.get("subreddit", ""),
                    "score": score,
                    "num_comments": num_comments,
                    "title": title
                }
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error parsing Reddit post: {e}")
            return None
    
    def _get_time_filter(self, time_range: str) -> int:
        """
        Convert time range string to Unix timestamp.
        
        Args:
            time_range: Time range string (day, week, month, year)
            
        Returns:
            Unix timestamp for the start of the time range
        """
        now = datetime.now()
        
        if time_range == "day":
            delta = timedelta(days=1)
        elif time_range == "week":
            delta = timedelta(weeks=1)
        elif time_range == "month":
            delta = timedelta(days=30)
        elif time_range == "year":
            delta = timedelta(days=365)
        else:
            delta = timedelta(weeks=1)  # Default to week
        
        start_time = now - delta
        return int(start_time.timestamp())
    
    async def get_post_comments(self, post_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get comments for a specific Reddit post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries
        """
        try:
            url = "https://api.pushshift.io/reddit/search/comment"
            params = {
                "link_id": post_id,
                "size": limit,
                "sort": "score",
                "sort_type": "desc",
                "fields": "id,body,author,created_utc,score"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            comments = []
            
            if "data" in data:
                for comment in data["data"]:
                    if comment.get("body") and len(comment["body"]) > 10:
                        comments.append({
                            "id": comment.get("id", ""),
                            "content": comment.get("body", ""),
                            "author": f"u/{comment.get('author', 'unknown')}",
                            "score": comment.get("score", 0),
                            "created_at": datetime.fromtimestamp(comment.get("created_utc", 0))
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
