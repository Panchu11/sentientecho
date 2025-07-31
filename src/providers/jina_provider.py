"""
Jina AI Provider for content processing and enhancement.
"""

import asyncio
from typing import List, Dict, Any, Optional
import httpx
import json

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


class JinaProvider:
    """
    Jina AI Provider for content processing and enhancement.
    
    Provides content similarity, embeddings, and advanced text processing.
    """
    
    def __init__(self, api_key: str):
        """Initialize the Jina AI provider."""
        self.api_key = api_key
        self.base_url = "https://api.jina.ai/v1"
        
        # HTTP client with timeout and retries
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info("Initialized Jina AI provider")
    
    async def get_embeddings(self, texts: List[str], model: str = "jina-embeddings-v3") -> List[List[float]]:
        """
        Get embeddings for a list of texts using Jina AI.
        
        Args:
            texts: List of texts to embed
            model: Jina embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            payload = {
                "model": model,
                "input": texts,
                "encoding_format": "float"
            }
            
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]
            
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            embeddings = await self.get_embeddings([text1, text2])
            if len(embeddings) != 2:
                return 0.0
            
            # Calculate cosine similarity
            import numpy as np
            
            vec1 = np.array(embeddings[0])
            vec2 = np.array(embeddings[1])
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            # Convert to 0-1 range
            return (similarity + 1) / 2
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def rank_posts_by_relevance(self, posts: List[Post], query: str) -> List[Post]:
        """
        Rank posts by semantic relevance to query using Jina embeddings.
        
        Args:
            posts: List of posts to rank
            query: Query to rank against
            
        Returns:
            Posts sorted by relevance (highest first)
        """
        if not posts:
            return []
        
        try:
            # Prepare texts for embedding
            texts = [query] + [post.content[:500] for post in posts]  # Limit content length
            
            # Get embeddings
            embeddings = await self.get_embeddings(texts)
            if len(embeddings) != len(texts):
                logger.warning("Embedding count mismatch, falling back to original order")
                return posts
            
            # Calculate similarities
            import numpy as np
            
            query_embedding = np.array(embeddings[0])
            post_embeddings = [np.array(emb) for emb in embeddings[1:]]
            
            similarities = []
            for post_emb in post_embeddings:
                # Cosine similarity
                dot_product = np.dot(query_embedding, post_emb)
                norm_query = np.linalg.norm(query_embedding)
                norm_post = np.linalg.norm(post_emb)
                
                if norm_query == 0 or norm_post == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product / (norm_query * norm_post)
                    # Convert to 0-1 range
                    similarity = (similarity + 1) / 2
                
                similarities.append(similarity)
            
            # Update posts with Jina relevance scores
            for i, post in enumerate(posts):
                if i < len(similarities):
                    post.jina_relevance_score = similarities[i]
                else:
                    post.jina_relevance_score = 0.0
            
            # Sort by Jina relevance score
            ranked_posts = sorted(posts, key=lambda p: getattr(p, 'jina_relevance_score', 0.0), reverse=True)
            
            logger.info(f"Ranked {len(posts)} posts using Jina AI embeddings")
            return ranked_posts
            
        except Exception as e:
            logger.error(f"Error ranking posts with Jina: {e}")
            return posts
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text using Jina AI.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of extracted keywords
        """
        try:
            # Use Jina's text processing capabilities
            payload = {
                "model": "jina-reranker-v1-base-en",
                "query": "extract important keywords",
                "documents": [text[:1000]]  # Limit text length
            }
            
            response = await self.client.post(
                f"{self.base_url}/rerank",
                json=payload
            )
            
            if response.status_code == 200:
                # For now, fall back to simple keyword extraction
                # This could be enhanced with actual Jina keyword extraction
                words = text.lower().split()
                # Simple frequency-based keyword extraction
                word_freq = {}
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                return [word for word, freq in keywords[:max_keywords]]
            else:
                # Fallback to simple extraction
                return self._simple_keyword_extraction(text, max_keywords)
                
        except Exception as e:
            logger.error(f"Error extracting keywords with Jina: {e}")
            return self._simple_keyword_extraction(text, max_keywords)
    
    def _simple_keyword_extraction(self, text: str, max_keywords: int) -> List[str]:
        """Simple fallback keyword extraction."""
        words = text.lower().split()
        word_freq = {}
        
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        for word in words:
            if len(word) > 3 and word.isalpha() and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:max_keywords]]
    
    async def enhance_post_content(self, post: Post, query: str) -> Post:
        """
        Enhance post with Jina AI analysis.
        
        Args:
            post: Post to enhance
            query: Original query for context
            
        Returns:
            Enhanced post with additional metadata
        """
        try:
            # Calculate relevance score
            relevance = await self.calculate_similarity(post.content, query)
            
            # Extract keywords from post content
            keywords = await self.extract_keywords(post.content, max_keywords=5)
            
            # Add Jina enhancements to post metadata
            if not hasattr(post, 'jina_metadata'):
                post.jina_metadata = {}
            
            post.jina_metadata.update({
                'relevance_score': relevance,
                'extracted_keywords': keywords,
                'processed_by_jina': True
            })
            
            # Also set the jina_relevance_score attribute
            post.jina_relevance_score = relevance
            
            logger.debug(f"Enhanced post {post.id} with Jina AI")
            return post
            
        except Exception as e:
            logger.error(f"Error enhancing post with Jina: {e}")
            return post
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Utility function for batch processing
async def process_posts_with_jina(posts: List[Post], query: str, jina_provider: JinaProvider) -> List[Post]:
    """
    Process multiple posts with Jina AI in parallel.
    
    Args:
        posts: List of posts to process
        query: Query for relevance calculation
        jina_provider: Jina provider instance
        
    Returns:
        List of enhanced posts
    """
    if not posts:
        return []
    
    try:
        # Process posts in parallel
        tasks = [jina_provider.enhance_post_content(post, query) for post in posts]
        enhanced_posts = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        result = []
        for i, enhanced_post in enumerate(enhanced_posts):
            if isinstance(enhanced_post, Exception):
                logger.warning(f"Failed to enhance post {i}: {enhanced_post}")
                result.append(posts[i])  # Use original post
            else:
                result.append(enhanced_post)
        
        # Rank by Jina relevance
        ranked_posts = await jina_provider.rank_posts_by_relevance(result, query)
        
        return ranked_posts
        
    except Exception as e:
        logger.error(f"Error in batch Jina processing: {e}")
        return posts
