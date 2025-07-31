#!/usr/bin/env python3
"""
Test script for Twitter provider functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.post import Post
from providers.twitter_provider import TwitterProvider


async def test_twitter_search():
    """Test Twitter search functionality."""
    print("🔍 Testing Twitter search...")

    # Use Serper API key from environment
    from config import get_settings
    settings = get_settings()
    serper_api_key = settings.serper_api_key
    provider = TwitterProvider(max_results=5, serper_api_key=serper_api_key)
    
    try:
        # Test search
        posts = await provider.search_posts(
            keywords=["python", "programming"],
            time_range="week"
        )
        
        print(f"✅ Found {len(posts)} Twitter posts")
        
        for i, post in enumerate(posts, 1):
            print(f"\n🐦 Tweet {i}:")
            print(f"   Content: {post.content[:100]}...")
            print(f"   Author: {post.author}")
            print(f"   Likes: {post.metadata.get('likes', 0)}")
            print(f"   Retweets: {post.metadata.get('retweets', 0)}")
            print(f"   Replies: {post.metadata.get('replies', 0)}")
            print(f"   URL: {post.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Twitter search failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting SentientEcho Twitter Provider Test\n")
    
    success = await test_twitter_search()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
