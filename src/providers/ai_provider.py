"""
AI Provider for Sentient Dobby integration via Fireworks API.
"""

import asyncio
from typing import AsyncIterator, Dict, Any, List, Optional
import httpx
from openai import AsyncOpenAI
import json
import logging

try:
    from ..utils.logger import get_logger
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.logger import get_logger

logger = get_logger(__name__)


class AIProvider:
    """
    AI Provider for Sentient Dobby Llama 3 70B model via Fireworks API.
    
    Handles query preprocessing, summarization, and content analysis.
    """
    
    def __init__(self, api_key: str, model_id: str):
        """Initialize the AI provider with Fireworks credentials."""
        self.api_key = api_key
        self.model_id = model_id
        
        # Initialize OpenAI client for Fireworks compatibility
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1"
        )
        
        logger.info(f"Initialized AI provider with model: {model_id}")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query to extract search intent and keywords.
        
        Args:
            query: The user's natural language query
            
        Returns:
            Dict containing processed query information
        """
        prompt = f"""
        Analyze this user query and extract search information:
        Query: "{query}"
        
        Please respond with a JSON object containing:
        {{
            "keywords": ["list", "of", "search", "keywords"],
            "search_reddit": true/false,
            "search_twitter": true/false,
            "subreddit": "specific_subreddit_if_mentioned_or_null",
            "time_range": "day/week/month/year",
            "intent": "brief description of what user wants",
            "sentiment_filter": "positive/negative/neutral/any"
        }}
        
        Guidelines:
        - Extract 3-5 relevant keywords for searching
        - Default to searching both Reddit and Twitter unless specifically mentioned
        - Default time_range to "week" unless specified
        - Only include subreddit if specifically mentioned
        - Determine if user wants specific sentiment
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing search queries. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            result = json.loads(content)
            logger.info(f"Processed query: {query} -> {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback to basic processing
            return {
                "keywords": query.split()[:5],
                "search_reddit": True,
                "search_twitter": True,
                "subreddit": None,
                "time_range": "week",
                "intent": query,
                "sentiment_filter": "any"
            }
    
    async def summarize_post(self, post_content: str, query: str) -> str:
        """
        Generate a summary of a post in relation to the user's query.
        
        Args:
            post_content: The content of the post to summarize
            query: The original user query for context
            
        Returns:
            A concise summary of the post
        """
        prompt = f"""
        Summarize this social media post in relation to the user's query.
        
        User Query: "{query}"
        Post Content: "{post_content[:1000]}"
        
        Provide a 1-2 sentence summary that:
        1. Explains how this post relates to the query
        2. Captures the main sentiment/opinion
        3. Highlights key points
        
        Keep it concise and relevant.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing social media content. Be concise and relevant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=150
            )
            
            summary = response.choices[0].message.content.strip()
            logger.debug(f"Generated summary for post: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary unavailable"
    
    async def analyze_sentiment(self, content: str) -> str:
        """
        Analyze the sentiment of content.
        
        Args:
            content: The content to analyze
            
        Returns:
            Sentiment classification: "positive", "negative", or "neutral"
        """
        prompt = f"""
        Analyze the sentiment of this content and respond with only one word:
        
        Content: "{content[:500]}"
        
        Respond with exactly one of: positive, negative, neutral
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Respond with only one word."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return "neutral"
    
    async def rank_posts_relevance(self, posts: List[Dict], query: str) -> List[float]:
        """
        Rank posts by relevance to the query.
        
        Args:
            posts: List of post dictionaries
            query: The original query
            
        Returns:
            List of relevance scores (0.0 to 1.0)
        """
        if not posts:
            return []
        
        # Create a batch prompt for efficiency
        posts_text = "\n\n".join([
            f"Post {i+1}: {post.get('content', '')[:200]}"
            for i, post in enumerate(posts)
        ])
        
        prompt = f"""
        Rate the relevance of each post to the user's query on a scale of 0.0 to 1.0.
        
        Query: "{query}"
        
        Posts:
        {posts_text}
        
        Respond with only the scores separated by commas, like: 0.8, 0.6, 0.9, 0.3
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are an expert at rating content relevance. Respond only with comma-separated scores."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=100
            )
            
            scores_text = response.choices[0].message.content.strip()
            scores = [float(s.strip()) for s in scores_text.split(",")]
            
            # Ensure we have the right number of scores
            if len(scores) != len(posts):
                logger.warning(f"Score count mismatch: {len(scores)} vs {len(posts)}")
                return [0.5] * len(posts)  # Default scores
            
            return scores
            
        except Exception as e:
            logger.error(f"Error ranking posts: {e}")
            return [0.5] * len(posts)  # Default scores
