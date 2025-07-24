"""
Post processor for ranking, filtering, and enhancing social media posts.
"""

import asyncio
from typing import List, Dict, Any
try:
    from ..models.post import Post
    from ..providers.ai_provider import AIProvider
    from ..utils.logger import get_logger
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from models.post import Post
    from providers.ai_provider import AIProvider
    from utils.logger import get_logger

logger = get_logger(__name__)


class PostProcessor:
    """
    Processes and enhances posts with AI-powered analysis.
    """
    
    def __init__(self, ai_provider: AIProvider):
        """Initialize with AI provider for post analysis."""
        self.ai_provider = ai_provider
        logger.info("Initialized PostProcessor")
    
    async def process_posts(
        self,
        posts: List[Post],
        query: str,
        max_posts: int = 10
    ) -> List[Post]:
        """
        Process and rank posts for relevance to the query.
        
        Args:
            posts: List of posts to process
            query: Original user query
            max_posts: Maximum number of posts to return
            
        Returns:
            List of processed and ranked posts
        """
        if not posts:
            return []
        
        try:
            logger.info(f"Processing {len(posts)} posts for query: {query}")
            
            # Step 1: Remove duplicates
            unique_posts = self._remove_duplicates(posts)
            logger.info(f"After deduplication: {len(unique_posts)} posts")
            
            # Step 2: Filter out low-quality posts
            filtered_posts = self._filter_quality(unique_posts)
            logger.info(f"After quality filtering: {len(filtered_posts)} posts")
            
            if not filtered_posts:
                return []
            
            # Step 3: Analyze posts in parallel
            enhanced_posts = await self._enhance_posts_parallel(filtered_posts, query)
            logger.info(f"Enhanced {len(enhanced_posts)} posts")
            
            # Step 4: Rank by relevance and engagement
            ranked_posts = self._rank_posts(enhanced_posts)
            
            # Step 5: Return top posts
            result = ranked_posts[:max_posts]
            logger.info(f"Returning top {len(result)} posts")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing posts: {e}")
            # Return original posts if processing fails
            return posts[:max_posts]
    
    def _remove_duplicates(self, posts: List[Post]) -> List[Post]:
        """
        Remove duplicate posts based on content similarity.
        
        Args:
            posts: List of posts
            
        Returns:
            List of unique posts
        """
        unique_posts = []
        seen_content = set()
        
        for post in posts:
            # Create a normalized version of content for comparison
            normalized_content = self._normalize_content(post.content)
            
            # Skip if we've seen very similar content
            if normalized_content not in seen_content:
                seen_content.add(normalized_content)
                unique_posts.append(post)
        
        return unique_posts
    
    def _normalize_content(self, content: str) -> str:
        """
        Normalize content for duplicate detection.
        
        Args:
            content: Post content
            
        Returns:
            Normalized content string
        """
        # Remove URLs, mentions, hashtags, and extra whitespace
        import re
        
        # Remove URLs
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Remove mentions and hashtags
        content = re.sub(r'[@#]\w+', '', content)
        
        # Remove extra whitespace and convert to lowercase
        content = ' '.join(content.split()).lower()
        
        # Take first 100 characters for comparison
        return content[:100]
    
    def _filter_quality(self, posts: List[Post]) -> List[Post]:
        """
        Filter out low-quality posts.
        
        Args:
            posts: List of posts
            
        Returns:
            List of quality posts
        """
        filtered_posts = []
        
        for post in posts:
            # Skip very short posts
            if len(post.content.strip()) < 20:
                continue
            
            # Skip posts with very low engagement
            if post.engagement_score < 0:
                continue
            
            # Skip posts that are mostly URLs or mentions
            content_words = len([word for word in post.content.split() if not word.startswith(('http', '@', '#'))])
            if content_words < 5:
                continue
            
            filtered_posts.append(post)
        
        return filtered_posts
    
    async def _enhance_posts_parallel(self, posts: List[Post], query: str) -> List[Post]:
        """
        Enhance posts with AI analysis in parallel.
        
        Args:
            posts: List of posts to enhance
            query: Original query for context
            
        Returns:
            List of enhanced posts
        """
        # Create tasks for parallel processing
        tasks = []
        
        for post in posts:
            task = self._enhance_single_post(post, query)
            tasks.append(task)
        
        # Execute tasks in parallel with limited concurrency
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
        
        async def bounded_enhance(post_task):
            async with semaphore:
                return await post_task
        
        enhanced_posts = await asyncio.gather(
            *[bounded_enhance(task) for task in tasks],
            return_exceptions=True
        )
        
        # Filter out failed enhancements
        result = []
        for i, enhanced_post in enumerate(enhanced_posts):
            if isinstance(enhanced_post, Exception):
                logger.warning(f"Failed to enhance post {i}: {enhanced_post}")
                result.append(posts[i])  # Use original post
            else:
                result.append(enhanced_post)
        
        return result
    
    async def _enhance_single_post(self, post: Post, query: str) -> Post:
        """
        Enhance a single post with AI analysis.
        
        Args:
            post: Post to enhance
            query: Original query for context
            
        Returns:
            Enhanced post
        """
        try:
            # Create tasks for parallel AI analysis
            tasks = [
                self.ai_provider.summarize_post(post.content, query),
                self.ai_provider.analyze_sentiment(post.content)
            ]
            
            # Execute AI tasks in parallel
            summary, sentiment = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results
            if isinstance(summary, Exception):
                logger.warning(f"Failed to generate summary: {summary}")
                summary = None
            
            if isinstance(sentiment, Exception):
                logger.warning(f"Failed to analyze sentiment: {sentiment}")
                sentiment = "neutral"
            
            # Update post with enhancements
            post.summary = summary
            post.sentiment = sentiment
            
            return post
            
        except Exception as e:
            logger.error(f"Error enhancing post: {e}")
            return post
    
    def _rank_posts(self, posts: List[Post]) -> List[Post]:
        """
        Rank posts by relevance and engagement.
        
        Args:
            posts: List of posts to rank
            
        Returns:
            List of ranked posts
        """
        def calculate_score(post: Post) -> float:
            """Calculate ranking score for a post."""
            score = 0.0
            
            # Base engagement score (normalized)
            max_engagement = max(p.engagement_score for p in posts) if posts else 1
            engagement_factor = post.engagement_score / max_engagement if max_engagement > 0 else 0
            score += engagement_factor * 0.4
            
            # Recency factor (newer posts get higher scores)
            from datetime import datetime, timedelta
            now = datetime.now()
            age_hours = (now - post.created_at).total_seconds() / 3600
            recency_factor = max(0, 1 - (age_hours / (24 * 7)))  # Decay over a week
            score += recency_factor * 0.2
            
            # Content length factor (prefer substantial content)
            content_length = len(post.content)
            length_factor = min(1.0, content_length / 500)  # Optimal around 500 chars
            score += length_factor * 0.2
            
            # Sentiment factor (prefer positive content slightly)
            if post.sentiment == "positive":
                score += 0.1
            elif post.sentiment == "neutral":
                score += 0.05
            
            # Source diversity bonus
            if post.source == "Reddit":
                score += 0.05  # Slight preference for Reddit due to discussion quality
            
            return score
        
        # Calculate scores and sort
        for post in posts:
            post.relevance_score = calculate_score(post)
        
        # Sort by relevance score (descending)
        ranked_posts = sorted(posts, key=lambda p: p.relevance_score or 0, reverse=True)
        
        return ranked_posts
