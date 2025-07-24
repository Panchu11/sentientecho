#!/usr/bin/env python3
"""
Test script for Reddit provider functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.post import Post
from providers.reddit_provider import RedditProvider


async def test_reddit_search():
    """Test Reddit search functionality."""
    print("🔍 Testing Reddit search...")
    
    provider = RedditProvider(max_results=5)
    
    try:
        # Test search
        posts = await provider.search_posts(
            keywords=["python", "programming"],
            time_range="week"
        )
        
        print(f"✅ Found {len(posts)} Reddit posts")
        
        for i, post in enumerate(posts, 1):
            print(f"\n📝 Post {i}:")
            print(f"   Title: {post.metadata.get('title', 'N/A')[:100]}...")
            print(f"   Author: {post.author}")
            print(f"   Score: {post.metadata.get('score', 0)}")
            print(f"   Comments: {post.metadata.get('num_comments', 0)}")
            print(f"   Subreddit: r/{post.metadata.get('subreddit', 'unknown')}")
            print(f"   URL: {post.url}")
        
        await provider.close()
        return True
        
    except Exception as e:
        print(f"❌ Reddit search failed: {e}")
        await provider.close()
        return False


async def main():
    """Main test function."""
    print("🚀 Starting SentientEcho Reddit Provider Test\n")
    
    success = await test_reddit_search()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
