#!/usr/bin/env python3
"""
Simple test for SentientEcho agent creation and basic functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sentient_echo_agent import SentientEchoAgent
from config import validate_config


async def test_agent_creation():
    """Test agent creation and initialization."""
    print("🔧 Testing Agent Creation...")
    
    try:
        # Validate configuration
        validate_config()
        print("✅ Configuration validated")
        
        # Create agent
        agent = SentientEchoAgent("SentientEcho")
        print("✅ Agent created successfully")
        
        # Test agent properties
        print(f"   Agent name: {agent.name}")
        print(f"   AI provider: {type(agent.ai_provider).__name__}")
        print(f"   Reddit provider: {type(agent.reddit_provider).__name__}")
        print(f"   Twitter provider: {type(agent.twitter_provider).__name__}")
        print(f"   Query processor: {type(agent.query_processor).__name__}")
        print(f"   Post processor: {type(agent.post_processor).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_individual_components():
    """Test individual components work together."""
    print("\n🧩 Testing Individual Components...")
    
    try:
        agent = SentientEchoAgent("SentientEcho")
        
        # Test query processing
        print("\n📝 Testing Query Processing...")
        query = "What do people think about Python programming?"
        processed_query = await agent.query_processor.process_query(query)
        print(f"   Original: {query}")
        print(f"   Keywords: {processed_query.keywords}")
        print(f"   Search Reddit: {processed_query.search_reddit}")
        print(f"   Search Twitter: {processed_query.search_twitter}")
        
        # Test Reddit search
        print("\n🔍 Testing Reddit Search...")
        reddit_posts = await agent.reddit_provider.search_posts(
            keywords=processed_query.keywords[:2],
            time_range="week"
        )
        print(f"   Found {len(reddit_posts)} Reddit posts")
        
        # Test Twitter search
        print("\n🐦 Testing Twitter Search...")
        twitter_posts = await agent.twitter_provider.search_posts(
            keywords=processed_query.keywords[:2],
            time_range="week"
        )
        print(f"   Found {len(twitter_posts)} Twitter posts")
        
        # Test post processing
        if reddit_posts or twitter_posts:
            print("\n⚡ Testing Post Processing...")
            all_posts = reddit_posts + twitter_posts
            processed_posts = await agent.post_processor.process_posts(
                posts=all_posts[:5],  # Limit to 5 for testing
                query=query,
                max_posts=3
            )
            print(f"   Processed {len(processed_posts)} posts")
            
            for i, post in enumerate(processed_posts, 1):
                print(f"   {i}. {post.source} - {post.author} - Score: {post.relevance_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_server_creation():
    """Test server creation."""
    print("\n🌐 Testing Server Creation...")
    
    try:
        from sentient_agent_framework import DefaultServer
        
        agent = SentientEchoAgent("SentientEcho")
        server = DefaultServer(agent)
        
        print("✅ Server created successfully")
        print(f"   Agent: {agent.name}")
        print(f"   Server type: {type(server).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server creation failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting SentientEcho Simple Integration Test\n")
    
    success1 = await test_agent_creation()
    success2 = await test_individual_components()
    success3 = await test_server_creation()
    
    if success1 and success2 and success3:
        print("\n🎉 All simple integration tests passed!")
        print("\n✨ SentientEcho agent is working correctly!")
        print("\n🚀 Ready for deployment to SentientChat!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
