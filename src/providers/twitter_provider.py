"""
Twitter Provider for fetching tweets using multiple methods.
"""

import asyncio
import subprocess
import json
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import tempfile
import os

try:
    from ..models.post import Post
    from ..utils.logger import get_logger
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from models.post import Post
    from utils.logger import get_logger

logger = get_logger(__name__)


class TwitterProvider:
    """
    Twitter Provider using multiple methods for Twitter content fetching.

    Provides access to tweets with keyword and time filtering.
    """

    def __init__(self, max_results: int = 10, serper_api_key: Optional[str] = None):
        """Initialize the Twitter provider."""
        self.max_results = max_results
        self.serper_api_key = serper_api_key

        # HTTP client for Serper.dev API
        if serper_api_key:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "X-API-KEY": serper_api_key,
                    "Content-Type": "application/json"
                }
            )
        else:
            self.client = None

        logger.info(f"Initialized Twitter provider with max_results: {max_results}")
    
    async def search_posts(
        self,
        keywords: List[str],
        time_range: str = "week",
        min_likes: int = 1
    ) -> List[Post]:
        """
        Search Twitter posts using multiple methods.

        Args:
            keywords: List of keywords to search for
            time_range: Time range for search (day, week, month, year)
            min_likes: Minimum likes threshold

        Returns:
            List of Post objects
        """
        # Try Serper.dev first if available
        if self.client and self.serper_api_key:
            try:
                return await self._search_with_serper(keywords, time_range, min_likes)
            except Exception as e:
                logger.warning(f"Serper search failed, trying snscrape: {e}")

        # Fallback to snscrape
        return await self._search_with_snscrape(keywords, time_range, min_likes)

    async def _search_with_serper(
        self,
        keywords: List[str],
        time_range: str = "week",
        min_likes: int = 1
    ) -> List[Post]:
        """Search Twitter using Serper.dev API."""
        try:
            query = " ".join(keywords)

            # Build search request
            search_data = {
                "q": f"{query} site:twitter.com",
                "num": self.max_results,
                "gl": "us",
                "hl": "en"
            }

            logger.info(f"Searching Twitter via Serper with query: {query}")

            response = await self.client.post(
                "https://google.serper.dev/search",
                json=search_data
            )
            response.raise_for_status()

            data = response.json()
            posts = []

            # Parse search results
            if "organic" in data:
                for result in data["organic"][:self.max_results]:
                    try:
                        post = self._parse_serper_result(result)
                        if post:
                            posts.append(post)
                    except Exception as e:
                        logger.warning(f"Error parsing Serper result: {e}")
                        continue

            logger.info(f"Found {len(posts)} Twitter posts via Serper")
            return posts

        except Exception as e:
            logger.error(f"Error searching Twitter via Serper: {e}")
            return []

    async def _search_with_snscrape(
        self,
        keywords: List[str],
        time_range: str = "week",
        min_likes: int = 1
    ) -> List[Post]:
        """Search Twitter using snscrape (fallback method)."""
        try:
            # Build search query
            query = " ".join(keywords)

            # Add time filter
            since_date = self._get_since_date(time_range)

            # Build snscrape command
            search_query = f'"{query}" since:{since_date} min_faves:{min_likes}'

            cmd = [
                "snscrape",
                "--jsonl",
                "--max-results", str(self.max_results),
                "twitter-search",
                search_query
            ]

            logger.info(f"Searching Twitter with snscrape query: {search_query}")

            # Execute snscrape command
            result = await self._run_snscrape_command(cmd)

            if not result:
                logger.warning("No Twitter results returned from snscrape")
                return []

            # Parse results
            posts = []
            for line in result.strip().split('\n'):
                if line.strip():
                    try:
                        tweet_data = json.loads(line)
                        post = self._parse_twitter_post(tweet_data)
                        if post:
                            posts.append(post)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing Twitter JSON: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"Error processing Twitter post: {e}")
                        continue

            logger.info(f"Found {len(posts)} Twitter posts via snscrape")
            return posts

        except Exception as e:
            logger.error(f"Error searching Twitter via snscrape: {e}")
            return []
    
    async def _run_snscrape_command(self, cmd: List[str]) -> Optional[str]:
        """
        Run snscrape command asynchronously.
        
        Args:
            cmd: Command list to execute
            
        Returns:
            Command output or None if failed
        """
        try:
            # Run the command with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=60.0  # 60 second timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.error("snscrape command timed out")
                return None
            
            if process.returncode != 0:
                logger.error(f"snscrape command failed: {stderr.decode()}")
                return None
            
            return stdout.decode()
            
        except Exception as e:
            logger.error(f"Error running snscrape command: {e}")
            return None
    
    def _parse_twitter_post(self, tweet_data: Dict[str, Any]) -> Optional[Post]:
        """
        Parse a Twitter post from snscrape output.
        
        Args:
            tweet_data: Raw tweet data from snscrape
            
        Returns:
            Post object or None if parsing fails
        """
        try:
            content = tweet_data.get("rawContent", tweet_data.get("content", ""))
            
            # Skip if no meaningful content
            if len(content.strip()) < 10:
                return None
            
            # Skip retweets to avoid duplicates
            if content.startswith("RT @"):
                return None
            
            # Calculate engagement score
            likes = tweet_data.get("likeCount", 0)
            retweets = tweet_data.get("retweetCount", 0)
            replies = tweet_data.get("replyCount", 0)
            engagement_score = likes + (retweets * 2) + (replies * 1.5)
            
            # Parse date
            date_str = tweet_data.get("date", "")
            try:
                created_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except:
                created_at = datetime.now()
            
            # Create Post object
            post = Post(
                id=str(tweet_data.get("id", "")),
                source="Twitter",
                content=content,
                author=f"@{tweet_data.get('user', {}).get('username', 'unknown')}",
                created_at=created_at,
                url=tweet_data.get("url", ""),
                engagement_score=engagement_score,
                metadata={
                    "likes": likes,
                    "retweets": retweets,
                    "replies": replies,
                    "user_followers": tweet_data.get("user", {}).get("followersCount", 0),
                    "user_verified": tweet_data.get("user", {}).get("verified", False)
                }
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error parsing Twitter post: {e}")
            return None
    
    def _get_since_date(self, time_range: str) -> str:
        """
        Convert time range string to date string for snscrape.
        
        Args:
            time_range: Time range string (day, week, month, year)
            
        Returns:
            Date string in YYYY-MM-DD format
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
        
        since_date = now - delta
        return since_date.strftime("%Y-%m-%d")
    
    async def get_user_tweets(
        self, 
        username: str, 
        limit: int = 10
    ) -> List[Post]:
        """
        Get recent tweets from a specific user.
        
        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets to fetch
            
        Returns:
            List of Post objects
        """
        try:
            cmd = [
                "snscrape",
                "--jsonl",
                "--max-results", str(limit),
                "twitter-user",
                username
            ]
            
            result = await self._run_snscrape_command(cmd)
            
            if not result:
                return []
            
            posts = []
            for line in result.strip().split('\n'):
                if line.strip():
                    try:
                        tweet_data = json.loads(line)
                        post = self._parse_twitter_post(tweet_data)
                        if post:
                            posts.append(post)
                    except Exception as e:
                        logger.warning(f"Error processing user tweet: {e}")
                        continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching user tweets for {username}: {e}")
            return []

    def _parse_serper_result(self, result: Dict[str, Any]) -> Optional[Post]:
        """
        Parse a Twitter post from Serper search result.

        Args:
            result: Search result from Serper API

        Returns:
            Post object or None if parsing fails
        """
        try:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")

            # Extract content (combine title and snippet)
            content = f"{title}\n{snippet}".strip()

            # Skip if no meaningful content
            if len(content.strip()) < 10:
                return None

            # Extract username from link if possible
            author = "unknown"
            if "twitter.com/" in link:
                try:
                    username = link.split("twitter.com/")[1].split("/")[0]
                    author = f"@{username}"
                except:
                    pass

            # Create Post object with limited metadata
            post = Post(
                id=link.split("/")[-1] if "/" in link else "",
                source="Twitter",
                content=content,
                author=author,
                created_at=datetime.now(),  # Serper doesn't provide exact timestamps
                url=link,
                engagement_score=1.0,  # Default score since we don't have engagement data
                metadata={
                    "source_method": "serper",
                    "title": title,
                    "snippet": snippet
                }
            )

            return post

        except Exception as e:
            logger.error(f"Error parsing Serper result: {e}")
            return None
