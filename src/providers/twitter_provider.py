"""
Twitter Provider for fetching tweets using snscrape library.
"""

import asyncio
import subprocess
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import tempfile
import os

from ..models.post import Post
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TwitterProvider:
    """
    Twitter Provider using snscrape for real-time Twitter content fetching.
    
    Provides access to tweets with keyword and time filtering.
    """
    
    def __init__(self, max_results: int = 10):
        """Initialize the Twitter provider."""
        self.max_results = max_results
        logger.info(f"Initialized Twitter provider with max_results: {max_results}")
    
    async def search_posts(
        self,
        keywords: List[str],
        time_range: str = "week",
        min_likes: int = 1
    ) -> List[Post]:
        """
        Search Twitter posts using snscrape.
        
        Args:
            keywords: List of keywords to search for
            time_range: Time range for search (day, week, month, year)
            min_likes: Minimum likes threshold
            
        Returns:
            List of Post objects
        """
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
            
            logger.info(f"Searching Twitter with query: {search_query}")
            
            # Execute snscrape command
            result = await self._run_snscrape_command(cmd)
            
            if not result:
                logger.warning("No Twitter results returned")
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
            
            logger.info(f"Found {len(posts)} Twitter posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
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
