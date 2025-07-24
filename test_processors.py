#!/usr/bin/env python3
"""
Test script for processor functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.post import Post
from providers.ai_provider import AIProvider
from processors.query_processor import QueryProcessor
from processors.post_processor import PostProcessor


async def test_query_processor():
    """Test query processor functionality."""
    print("🔍 Testing Query Processor...")
    
    # Initialize AI provider
    api_key = "fw_3ZR6rssgw5u2XspeDZCDrWkC"
    model_id = "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"
    ai_provider = AIProvider(api_key=api_key, model_id=model_id)
    
    # Initialize query processor
    processor = QueryProcessor(ai_provider)
    
    try:
        # Test different types of queries
        test_queries = [
            "What do people think about Python programming?",
            "Latest discussions on r/MachineLearning about AI",
            "Twitter sentiment on cryptocurrency this week",
            "Trending topics in programming subreddits"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: {query}")
            
            result = await processor.process_query(query)
            
            print(f"   Keywords: {result.keywords}")
            print(f"   Search Reddit: {result.search_reddit}")
            print(f"   Search Twitter: {result.search_twitter}")
            print(f"   Filters: {result.filters}")
            print(f"   Intent: {result.intent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processor test failed: {e}")
        return False


async def test_post_processor():
    """Test post processor functionality."""
    print("\n📄 Testing Post Processor...")
    
    # Initialize AI provider
    api_key = "fw_3ZR6rssgw5u2XspeDZCDrWkC"
    model_id = "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"
    ai_provider = AIProvider(api_key=api_key, model_id=model_id)
    
    # Initialize post processor
    processor = PostProcessor(ai_provider)
    
    try:
        # Create test posts
        test_posts = [
            Post(
                id="1",
                source="Reddit",
                content="I've been learning Python for 6 months and it's amazing! The syntax is so clean and the community is very helpful. Highly recommend for beginners.",
                author="u/pythonlearner",
                created_at=datetime.now(),
                url="https://reddit.com/r/learnpython/post1",
                engagement_score=150,
                metadata={"score": 120, "num_comments": 30, "subreddit": "learnpython"}
            ),
            Post(
                id="2",
                source="Twitter",
                content="Just finished my first Python project! Built a web scraper that collects data from multiple APIs. #Python #Programming",
                author="@coder123",
                created_at=datetime.now(),
                url="https://twitter.com/coder123/status/123",
                engagement_score=85,
                metadata={"likes": 50, "retweets": 20, "replies": 15}
            ),
            Post(
                id="3",
                source="Reddit",
                content="Python vs JavaScript - which one should I learn first? I'm completely new to programming.",
                author="u/newbie",
                created_at=datetime.now(),
                url="https://reddit.com/r/programming/post3",
                engagement_score=200,
                metadata={"score": 180, "num_comments": 20, "subreddit": "programming"}
            ),
            Post(
                id="4",
                source="Twitter",
                content="Coffee is better than tea. Fight me.",
                author="@random",
                created_at=datetime.now(),
                url="https://twitter.com/random/status/456",
                engagement_score=10,
                metadata={"likes": 5, "retweets": 2, "replies": 3}
            )
        ]
        
        query = "What do people think about Python programming?"
        
        print(f"Processing {len(test_posts)} posts for query: '{query}'")
        
        # Process posts
        processed_posts = await processor.process_posts(
            posts=test_posts,
            query=query,
            max_posts=3
        )
        
        print(f"\n✅ Processed and ranked {len(processed_posts)} posts:")
        
        for i, post in enumerate(processed_posts, 1):
            print(f"\n🏆 Rank {i}:")
            print(f"   Source: {post.source}")
            print(f"   Author: {post.author}")
            print(f"   Content: {post.content[:100]}...")
            print(f"   Engagement: {post.engagement_score}")
            print(f"   Relevance: {post.relevance_score:.2f}")
            print(f"   Sentiment: {post.sentiment}")
            if post.summary:
                print(f"   Summary: {post.summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Post processor test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting SentientEcho Processors Test\n")
    
    success1 = await test_query_processor()
    success2 = await test_post_processor()
    
    if success1 and success2:
        print("\n✅ All processor tests passed!")
    else:
        print("\n❌ Some processor tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
