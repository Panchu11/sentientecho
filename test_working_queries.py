#!/usr/bin/env python3
"""
Working query testing for SentientEcho agent components.
Test individual components to see what's actually working.
"""

import asyncio
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from providers.ai_provider import AIProvider
from providers.reddit_provider import RedditProvider
from providers.twitter_provider import TwitterProvider
from config import get_settings


async def test_ai_provider():
    """Test AI provider functionality."""
    print("🧠 Testing AI Provider (Sentient Dobby)...")
    
    try:
        settings = get_settings()
        ai_provider = AIProvider(
            api_key=settings.fireworks_api_key,
            model_id=settings.fireworks_model_id
        )
        
        # Test query processing
        query = "What do people think about Python programming?"
        result = await ai_provider.process_query(query)
        
        print(f"   ✅ Query processed successfully")
        print(f"   🎯 Keywords: {result.get('keywords', [])}")
        print(f"   🔍 Search Reddit: {result.get('search_reddit', False)}")
        print(f"   🐦 Search Twitter: {result.get('search_twitter', False)}")
        print(f"   📋 Intent: {result.get('intent', 'N/A')}")
        
        # Test summarization
        content = "I've been learning Python for 6 months and it's amazing! The syntax is clean and the community is helpful."
        summary = await ai_provider.summarize_post(content, query)
        print(f"   📄 Summary generated: {summary[:100]}...")
        
        # Test sentiment analysis
        sentiment = await ai_provider.analyze_sentiment(content)
        print(f"   😊 Sentiment: {sentiment}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AI Provider failed: {e}")
        return False


async def test_reddit_provider():
    """Test Reddit provider functionality."""
    print("\n📱 Testing Reddit Provider...")
    
    try:
        reddit_provider = RedditProvider(max_results=3)
        
        # Test search
        posts = await reddit_provider.search_posts(
            keywords=["python", "programming"],
            time_range="week"
        )
        
        print(f"   ✅ Found {len(posts)} Reddit posts")
        
        for i, post in enumerate(posts, 1):
            print(f"   {i}. r/{post.metadata.get('subreddit', 'unknown')} - {post.author}")
            print(f"      📝 {post.content[:80]}...")
            print(f"      👍 Score: {post.metadata.get('score', 0)}")
        
        return len(posts) > 0
        
    except Exception as e:
        print(f"   ❌ Reddit Provider failed: {e}")
        return False


async def test_twitter_provider():
    """Test Twitter provider functionality."""
    print("\n🐦 Testing Twitter Provider...")
    
    try:
        settings = get_settings()
        twitter_provider = TwitterProvider(
            max_results=3,
            serper_api_key=settings.serper_api_key
        )
        
        # Test search
        posts = await twitter_provider.search_posts(
            keywords=["python", "programming"],
            time_range="week"
        )
        
        print(f"   ✅ Found {len(posts)} Twitter posts")
        
        for i, post in enumerate(posts, 1):
            print(f"   {i}. {post.author}")
            print(f"      📝 {post.content[:80]}...")
            print(f"      💫 Engagement: {post.engagement_score}")
        
        return len(posts) > 0
        
    except Exception as e:
        print(f"   ❌ Twitter Provider failed: {e}")
        return False


async def test_combined_search():
    """Test combined search functionality."""
    print("\n🔍 Testing Combined Search...")
    
    try:
        settings = get_settings()
        
        # Initialize providers
        reddit_provider = RedditProvider(max_results=2)
        twitter_provider = TwitterProvider(
            max_results=2,
            serper_api_key=settings.serper_api_key
        )
        
        # Search both platforms
        print("   🔍 Searching both Reddit and Twitter...")
        
        reddit_task = reddit_provider.search_posts(
            keywords=["AI", "artificial intelligence"],
            time_range="week"
        )
        
        twitter_task = twitter_provider.search_posts(
            keywords=["AI", "artificial intelligence"],
            time_range="week"
        )
        
        # Run searches in parallel
        reddit_posts, twitter_posts = await asyncio.gather(
            reddit_task, twitter_task, return_exceptions=True
        )
        
        # Handle results
        reddit_count = len(reddit_posts) if not isinstance(reddit_posts, Exception) else 0
        twitter_count = len(twitter_posts) if not isinstance(twitter_posts, Exception) else 0
        
        print(f"   📱 Reddit: {reddit_count} posts")
        print(f"   🐦 Twitter: {twitter_count} posts")
        
        # Show combined results
        all_posts = []
        if not isinstance(reddit_posts, Exception):
            all_posts.extend(reddit_posts)
        if not isinstance(twitter_posts, Exception):
            all_posts.extend(twitter_posts)
        
        print(f"   📊 Total: {len(all_posts)} posts from both platforms")
        
        if all_posts:
            print("   🏆 Sample Results:")
            for i, post in enumerate(all_posts[:3], 1):
                print(f"   {i}. {post.source} - {post.author}")
                print(f"      📝 {post.content[:60]}...")
        
        return len(all_posts) > 0
        
    except Exception as e:
        print(f"   ❌ Combined search failed: {e}")
        return False


async def test_end_to_end_simple():
    """Test simple end-to-end functionality."""
    print("\n🚀 Testing Simple End-to-End Flow...")
    
    try:
        settings = get_settings()
        
        # Step 1: AI Query Processing
        print("   🧠 Step 1: AI Query Processing...")
        ai_provider = AIProvider(
            api_key=settings.fireworks_api_key,
            model_id=settings.fireworks_model_id
        )
        
        query = "What are people saying about electric cars?"
        ai_result = await ai_provider.process_query(query)
        keywords = ai_result.get('keywords', ['electric', 'cars'])
        search_reddit = ai_result.get('search_reddit', True)
        search_twitter = ai_result.get('search_twitter', True)
        
        print(f"      ✅ Keywords extracted: {keywords}")
        
        # Step 2: Content Search
        print("   🔍 Step 2: Content Search...")
        all_posts = []
        
        if search_reddit:
            reddit_provider = RedditProvider(max_results=2)
            try:
                reddit_posts = await reddit_provider.search_posts(
                    keywords=keywords[:2],  # Limit keywords
                    time_range="week"
                )
                all_posts.extend(reddit_posts)
                print(f"      📱 Reddit: {len(reddit_posts)} posts")
            except Exception as e:
                print(f"      ❌ Reddit search failed: {e}")
        
        if search_twitter:
            twitter_provider = TwitterProvider(
                max_results=2,
                serper_api_key=settings.serper_api_key
            )
            try:
                twitter_posts = await twitter_provider.search_posts(
                    keywords=keywords[:2],  # Limit keywords
                    time_range="week"
                )
                all_posts.extend(twitter_posts)
                print(f"      🐦 Twitter: {len(twitter_posts)} posts")
            except Exception as e:
                print(f"      ❌ Twitter search failed: {e}")
        
        # Step 3: AI Enhancement
        print("   ⚡ Step 3: AI Enhancement...")
        enhanced_posts = []
        
        for post in all_posts[:3]:  # Limit to 3 posts
            try:
                # Add AI summary
                summary = await ai_provider.summarize_post(post.content, query)
                post.summary = summary
                
                # Add sentiment analysis
                sentiment = await ai_provider.analyze_sentiment(post.content)
                post.sentiment = sentiment
                
                # Add relevance score
                relevance_scores = await ai_provider.rank_posts_relevance([{"content": post.content}], query)
                post.relevance_score = relevance_scores[0] if relevance_scores else 0.5
                
                enhanced_posts.append(post)
                
            except Exception as e:
                print(f"      ⚠️ Enhancement failed for one post: {e}")
                enhanced_posts.append(post)  # Add without enhancement
        
        print(f"      ✅ Enhanced {len(enhanced_posts)} posts")
        
        # Step 4: Generate Response
        print("   📝 Step 4: Generate Response...")
        
        if enhanced_posts:
            response_parts = [
                f"## 📊 Found {len(enhanced_posts)} posts about '{query}'\n"
            ]
            
            for i, post in enumerate(enhanced_posts, 1):
                response_parts.append(f"### {i}. {post.source} Post")
                response_parts.append(f"**Author**: {post.author}")
                response_parts.append(f"**Content**: {post.content[:150]}...")
                if hasattr(post, 'relevance_score'):
                    response_parts.append(f"**Relevance**: {post.relevance_score:.2f}")
                if hasattr(post, 'sentiment'):
                    response_parts.append(f"**Sentiment**: {post.sentiment}")
                if hasattr(post, 'summary'):
                    response_parts.append(f"**Summary**: {post.summary}")
                response_parts.append("")
            
            final_response = "\n".join(response_parts)
            
            print("      ✅ Generated final response")
            print(f"\n📄 Final Response Preview:")
            print("-" * 60)
            print(final_response[:800] + "..." if len(final_response) > 800 else final_response)
            print("-" * 60)
            
            return True
        else:
            print("      ❌ No posts to generate response from")
            return False
        
    except Exception as e:
        print(f"   ❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main testing function."""
    print("🚀 Starting SentientEcho Component Testing")
    print("   Testing individual components to see what's working...\n")
    
    start_time = time.time()
    
    # Test individual components
    ai_success = await test_ai_provider()
    reddit_success = await test_reddit_provider()
    twitter_success = await test_twitter_provider()
    combined_success = await test_combined_search()
    e2e_success = await test_end_to_end_simple()
    
    # Summary
    total_tests = 5
    successful_tests = sum([ai_success, reddit_success, twitter_success, combined_success, e2e_success])
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("🎉 COMPONENT TESTING COMPLETE")
    print('='*80)
    print(f"📊 Results Summary:")
    print(f"   ✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"   📈 Success rate: {(successful_tests/total_tests)*100:.1f}%")
    print(f"   ⏱️ Total time: {elapsed:.2f} seconds")
    
    print(f"\n🔧 Component Status:")
    print(f"   🧠 AI Provider (Sentient Dobby): {'✅ Working' if ai_success else '❌ Issues'}")
    print(f"   📱 Reddit Provider: {'✅ Working' if reddit_success else '❌ Issues'}")
    print(f"   🐦 Twitter Provider: {'✅ Working' if twitter_success else '❌ Issues'}")
    print(f"   🔍 Combined Search: {'✅ Working' if combined_success else '❌ Issues'}")
    print(f"   🚀 End-to-End Flow: {'✅ Working' if e2e_success else '❌ Issues'}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 ALL COMPONENTS WORKING! SentientEcho is fully functional!")
    elif successful_tests >= 4:
        print(f"\n✨ MOSTLY WORKING! Minor issues but core functionality is solid.")
    elif successful_tests >= 3:
        print(f"\n⚠️ PARTIALLY WORKING. Some components have issues.")
    else:
        print(f"\n❌ SIGNIFICANT ISSUES. Multiple components failing.")
    
    return successful_tests >= 3


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
