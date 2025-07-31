"""
SentientEcho Agent - Main agent implementation for Reddit/Twitter query processing.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from sentient_agent_framework import (
    AbstractAgent,
    Session,
    Query,
    ResponseHandler
)

try:
    from .config import get_settings
    from .providers.ai_provider import AIProvider
    from .providers.reddit_provider import RedditProvider
    from .providers.twitter_provider import TwitterProvider
    from .providers.jina_provider import JinaProvider
    from .processors.query_processor import QueryProcessor
    from .processors.post_processor import PostProcessor
    from .utils.logger import get_logger
    from .utils.cache import get_cached_query_result, cache_query_result
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import get_settings
    from providers.ai_provider import AIProvider
    from providers.reddit_provider import RedditProvider
    from providers.twitter_provider import TwitterProvider
    from providers.jina_provider import JinaProvider
    from processors.query_processor import QueryProcessor
    from processors.post_processor import PostProcessor
    from utils.logger import get_logger
    from utils.cache import get_cached_query_result, cache_query_result

logger = get_logger(__name__)


class SentientEchoAgent(AbstractAgent):
    """
    SentientEcho Agent - Responds to queries with real Reddit and Twitter posts.
    
    This agent processes natural language queries, searches Reddit and Twitter
    for relevant content, and returns actual posts with optional AI summaries.
    """
    
    def __init__(self, name: str = "SentientEcho"):
        """Initialize the SentientEcho agent with all required providers."""
        super().__init__(name)
        self.settings = get_settings()
        
        # Initialize providers
        self.ai_provider = AIProvider(
            api_key=self.settings.fireworks_api_key,
            model_id=self.settings.fireworks_model_id
        )
        
        self.reddit_provider = RedditProvider(
            max_results=self.settings.max_reddit_results
        )
        
        self.twitter_provider = TwitterProvider(
            max_results=self.settings.max_twitter_results,
            serper_api_key=self.settings.serper_api_key
        )

        self.jina_provider = JinaProvider(
            api_key=self.settings.jina_ai_api_key
        )

        # Initialize processors
        self.query_processor = QueryProcessor(self.ai_provider)
        self.post_processor = PostProcessor(self.ai_provider, self.jina_provider)
        
        logger.info(f"Initialized {name} agent with all providers")
    
    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ):
        """
        Main assist method that processes queries and returns Reddit/Twitter posts.
        
        Args:
            session: The current session context
            query: The user's query
            response_handler: Handler for emitting events to SentientChat
        """
        try:
            logger.info(f"Processing query: {query.prompt}")

            # Check cache first
            cached_result = await get_cached_query_result(query.prompt)
            if cached_result:
                logger.info(f"Returning cached result for query: {query.prompt[:50]}...")

                # Stream cached response
                await response_handler.emit_text_block("CACHE_HIT", "⚡ Found cached result!")

                # Emit cached events
                for event in cached_result.get("events", []):
                    if event["type"] == "text_block":
                        await response_handler.emit_text_block(event["event_type"], event["content"])
                    elif event["type"] == "json":
                        await response_handler.emit_json(event["event_type"], event["data"])

                # Stream final response
                final_response = cached_result.get("final_response", "")
                if final_response:
                    stream = response_handler.create_text_stream("FINAL_RESPONSE")
                    await stream.emit_chunk(final_response)
                    await stream.complete()

                await response_handler.complete()
                return

            # Step 1: Process and understand the query
            await response_handler.emit_text_block(
                "QUERY_ANALYSIS", "🧠 Analyzing your query..."
            )
            
            processed_query = await self.query_processor.process_query(query.prompt)
            
            await response_handler.emit_json(
                "QUERY_INTENT", {
                    "original_query": query.prompt,
                    "processed_keywords": processed_query.keywords,
                    "search_reddit": processed_query.search_reddit,
                    "search_twitter": processed_query.search_twitter,
                    "filters": processed_query.filters
                }
            )
            
            # Step 2: Search for content
            await response_handler.emit_text_block(
                "SEARCH", "🔍 Searching Reddit and Twitter for relevant posts..."
            )
            
            # Parallel search execution
            search_tasks = []
            
            if processed_query.search_reddit:
                search_tasks.append(
                    self.reddit_provider.search_posts(
                        keywords=processed_query.keywords,
                        subreddit=processed_query.filters.get("subreddit"),
                        time_range=processed_query.filters.get("time_range", "week")
                    )
                )
            
            if processed_query.search_twitter:
                search_tasks.append(
                    self.twitter_provider.search_posts(
                        keywords=processed_query.keywords,
                        time_range=processed_query.filters.get("time_range", "week")
                    )
                )
            
            # Execute searches in parallel
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine and process results
            all_posts = []
            reddit_posts = []
            twitter_posts = []
            
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    logger.error(f"Search task {i} failed: {result}")
                    continue
                
                if processed_query.search_reddit and i == 0:
                    reddit_posts = result
                    all_posts.extend(result)
                elif processed_query.search_twitter:
                    twitter_posts = result
                    all_posts.extend(result)
            
            if not all_posts:
                await response_handler.emit_text_block(
                    "NO_RESULTS", "❌ No relevant posts found for your query."
                )
                await response_handler.complete()
                return
            
            # Step 3: Process and rank posts
            await response_handler.emit_text_block(
                "PROCESSING", "⚡ Processing and ranking posts..."
            )
            
            processed_posts = await self.post_processor.process_posts(
                posts=all_posts,
                query=query.prompt,
                max_posts=10
            )
            
            # Step 4: Emit results
            if reddit_posts:
                await response_handler.emit_json(
                    "REDDIT_POSTS", {
                        "source": "Reddit",
                        "count": len(reddit_posts),
                        "posts": [post.to_dict() for post in reddit_posts[:5]]
                    }
                )
            
            if twitter_posts:
                await response_handler.emit_json(
                    "TWITTER_POSTS", {
                        "source": "Twitter", 
                        "count": len(twitter_posts),
                        "posts": [post.to_dict() for post in twitter_posts[:5]]
                    }
                )
            
            # Step 5: Generate final response with summaries
            final_response_stream = response_handler.create_text_stream(
                "FINAL_RESPONSE"
            )
            
            await final_response_stream.emit_chunk(
                f"## 📊 Found {len(all_posts)} relevant posts\n\n"
            )
            
            # Stream the top posts with summaries
            for i, post in enumerate(processed_posts[:5], 1):
                await final_response_stream.emit_chunk(
                    f"### {i}. {post.source} Post\n"
                )
                await final_response_stream.emit_chunk(
                    f"**Author**: {post.author}\n"
                )
                await final_response_stream.emit_chunk(
                    f"**Posted**: {post.created_at}\n"
                )
                await final_response_stream.emit_chunk(
                    f"**Engagement**: {post.engagement_score}\n\n"
                )
                await final_response_stream.emit_chunk(
                    f"**Content**: {post.content[:500]}{'...' if len(post.content) > 500 else ''}\n\n"
                )
                
                if self.settings.enable_summaries and post.summary:
                    await final_response_stream.emit_chunk(
                        f"**AI Summary**: {post.summary}\n\n"
                    )
                
                await final_response_stream.emit_chunk(
                    f"**Link**: {post.url}\n\n---\n\n"
                )
            
            # Complete the response
            await final_response_stream.complete()
            await response_handler.complete()

            # Cache the result for future queries
            try:
                # Collect response data for caching
                cache_data = {
                    "events": [],  # Would need to collect events during processing
                    "final_response": getattr(final_response_stream, 'content', ''),
                    "processed_posts_count": len(processed_posts),
                    "timestamp": time.time()
                }
                await cache_query_result(query.prompt, cache_data)
                logger.debug(f"Cached result for query: {query.prompt[:50]}...")
            except Exception as cache_error:
                logger.warning(f"Failed to cache result: {cache_error}")

            logger.info(f"Successfully processed query with {len(processed_posts)} posts")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            await response_handler.emit_error(
                "PROCESSING_ERROR",
                error_code="INTERNAL_ERROR",
                details={"message": str(e)}
            )
            await response_handler.complete()
