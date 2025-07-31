#!/usr/bin/env python3
"""
Test script for AI provider functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from providers.ai_provider import AIProvider


async def test_ai_provider():
    """Test AI provider functionality."""
    print("🧠 Testing AI provider...")
    
    # Initialize with Fireworks credentials from environment
    from config import get_settings
    settings = get_settings()
    api_key = settings.fireworks_api_key
    model_id = settings.fireworks_model_id
    
    provider = AIProvider(api_key=api_key, model_id=model_id)
    
    try:
        # Test 1: Query processing
        print("\n📝 Test 1: Query Processing")
        query = "What do people think about Python programming on Reddit?"
        result = await provider.process_query(query)
        
        print(f"Original query: {query}")
        print(f"Keywords: {result.get('keywords', [])}")
        print(f"Search Reddit: {result.get('search_reddit', False)}")
        print(f"Search Twitter: {result.get('search_twitter', False)}")
        print(f"Intent: {result.get('intent', 'N/A')}")
        
        # Test 2: Post summarization
        print("\n📄 Test 2: Post Summarization")
        post_content = """
        I've been learning Python for 6 months now and I'm really enjoying it. 
        The syntax is so clean compared to Java. I started with basic scripts 
        and now I'm building web apps with Flask. The community is amazing and 
        there are so many resources available. Definitely recommend Python 
        for beginners!
        """
        
        summary = await provider.summarize_post(post_content, query)
        print(f"Post content: {post_content.strip()[:100]}...")
        print(f"Summary: {summary}")
        
        # Test 3: Sentiment analysis
        print("\n😊 Test 3: Sentiment Analysis")
        sentiment = await provider.analyze_sentiment(post_content)
        print(f"Sentiment: {sentiment}")
        
        # Test 4: Relevance ranking
        print("\n🎯 Test 4: Relevance Ranking")
        test_posts = [
            {"content": "Python is the best programming language for beginners"},
            {"content": "I love JavaScript for web development"},
            {"content": "Learning Python data science with pandas and numpy"},
            {"content": "Coffee is better than tea"}
        ]
        
        scores = await provider.rank_posts_relevance(test_posts, query)
        print("Relevance scores:")
        for i, (post, score) in enumerate(zip(test_posts, scores)):
            print(f"  {i+1}. {post['content'][:50]}... -> {score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI provider test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting SentientEcho AI Provider Test\n")
    
    success = await test_ai_provider()
    
    if success:
        print("\n✅ All AI tests passed!")
    else:
        print("\n❌ Some AI tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
