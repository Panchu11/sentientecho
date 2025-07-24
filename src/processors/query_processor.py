"""
Query processor for analyzing and preprocessing user queries.
"""

from typing import Dict, Any, List
try:
    from ..models.post import ProcessedQuery
    from ..providers.ai_provider import AIProvider
    from ..utils.logger import get_logger
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from models.post import ProcessedQuery
    from providers.ai_provider import AIProvider
    from utils.logger import get_logger

logger = get_logger(__name__)


class QueryProcessor:
    """
    Processes user queries to extract search intent, keywords, and filters.
    """
    
    def __init__(self, ai_provider: AIProvider):
        """Initialize with AI provider for query analysis."""
        self.ai_provider = ai_provider
        logger.info("Initialized QueryProcessor")
    
    async def process_query(self, query: str) -> ProcessedQuery:
        """
        Process a natural language query into structured search parameters.
        
        Args:
            query: The user's natural language query
            
        Returns:
            ProcessedQuery object with extracted information
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # Use AI to analyze the query
            analysis = await self.ai_provider.process_query(query)
            
            # Extract and validate information
            keywords = self._extract_keywords(analysis.get("keywords", []), query)
            search_reddit = analysis.get("search_reddit", True)
            search_twitter = analysis.get("search_twitter", True)
            
            # Build filters
            filters = self._build_filters(analysis)
            
            processed_query = ProcessedQuery(
                original_query=query,
                keywords=keywords,
                search_reddit=search_reddit,
                search_twitter=search_twitter,
                filters=filters,
                intent=analysis.get("intent", query),
                sentiment_filter=analysis.get("sentiment_filter", "any")
            )
            
            logger.info(f"Processed query result: {processed_query.dict()}")
            return processed_query
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback to basic processing
            return self._fallback_processing(query)
    
    def _extract_keywords(self, ai_keywords: List[str], original_query: str) -> List[str]:
        """
        Extract and validate keywords from AI analysis.
        
        Args:
            ai_keywords: Keywords suggested by AI
            original_query: Original query for fallback
            
        Returns:
            List of validated keywords
        """
        # Use AI keywords if available and valid
        if ai_keywords and len(ai_keywords) > 0:
            # Filter out very short or common words
            filtered_keywords = [
                kw for kw in ai_keywords 
                if len(kw) > 2 and kw.lower() not in ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
            ]
            
            if filtered_keywords:
                return filtered_keywords[:5]  # Limit to 5 keywords
        
        # Fallback to simple word extraction
        words = original_query.split()
        return [word for word in words if len(word) > 2][:5]
    
    def _build_filters(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build search filters from AI analysis.
        
        Args:
            analysis: AI analysis results
            
        Returns:
            Dictionary of search filters
        """
        filters = {}
        
        # Subreddit filter
        subreddit = analysis.get("subreddit")
        if subreddit and isinstance(subreddit, str):
            # Clean subreddit name
            subreddit = subreddit.replace("r/", "").replace("/", "")
            if subreddit:
                filters["subreddit"] = subreddit
        
        # Time range filter
        time_range = analysis.get("time_range", "week")
        if time_range in ["day", "week", "month", "year"]:
            filters["time_range"] = time_range
        else:
            filters["time_range"] = "week"
        
        # Sentiment filter
        sentiment = analysis.get("sentiment_filter", "any")
        if sentiment in ["positive", "negative", "neutral", "any"]:
            filters["sentiment"] = sentiment
        else:
            filters["sentiment"] = "any"
        
        return filters
    
    def _fallback_processing(self, query: str) -> ProcessedQuery:
        """
        Fallback processing when AI analysis fails.
        
        Args:
            query: Original query
            
        Returns:
            ProcessedQuery with basic processing
        """
        logger.warning("Using fallback query processing")
        
        # Simple keyword extraction
        words = query.lower().split()
        keywords = [word for word in words if len(word) > 2][:5]
        
        # Detect platform preferences
        search_reddit = "reddit" in query.lower() or "subreddit" in query.lower() or not ("twitter" in query.lower() or "tweet" in query.lower())
        search_twitter = "twitter" in query.lower() or "tweet" in query.lower() or not ("reddit" in query.lower() or "subreddit" in query.lower())
        
        # If no platform specified, search both
        if not search_reddit and not search_twitter:
            search_reddit = search_twitter = True
        
        # Basic filters
        filters = {
            "time_range": "week",
            "sentiment": "any"
        }
        
        # Try to detect subreddit mentions
        for word in words:
            if word.startswith("r/"):
                filters["subreddit"] = word[2:]
                break
        
        return ProcessedQuery(
            original_query=query,
            keywords=keywords,
            search_reddit=search_reddit,
            search_twitter=search_twitter,
            filters=filters,
            intent=query,
            sentiment_filter="any"
        )
    
    def detect_query_type(self, query: str) -> str:
        """
        Detect the type of query for specialized handling.
        
        Args:
            query: User query
            
        Returns:
            Query type string
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["sentiment", "opinion", "think", "feel"]):
            return "sentiment_analysis"
        elif any(word in query_lower for word in ["trending", "popular", "viral", "hot"]):
            return "trending_content"
        elif any(word in query_lower for word in ["news", "latest", "recent", "update"]):
            return "news_search"
        elif any(word in query_lower for word in ["discussion", "debate", "conversation"]):
            return "discussion_search"
        else:
            return "general_search"
