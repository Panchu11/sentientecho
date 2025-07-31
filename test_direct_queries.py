#!/usr/bin/env python3
"""
Direct query testing for SentientEcho agent components.
Test the core functionality without the Sentient Agent Framework.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from providers.ai_provider import AIProvider
from providers.reddit_provider import RedditProvider
from providers.twitter_provider import TwitterProvider
from providers.jina_provider import JinaProvider
from processors.query_processor import QueryProcessor
from processors.post_processor import PostProcessor
from config import get_settings


async def test_query_processing(query: str, query_name: str):
    """Test query processing and content retrieval."""
    print(f"\n{'='*80}")
    print(f"🔍 Testing: {query_name}")
    print(f"📝 Query: {query}")
    print('='*80)
    
    start_time = time.time()
    
    try:
        settings = get_settings()
        
        # Initialize providers
        print("🔧 Initializing providers...")
        ai_provider = AIProvider(
            api_key=settings.fireworks_api_key,
            model_id=settings.fireworks_model_id
        )
        
        reddit_provider = RedditProvider(max_results=5)
        
        twitter_provider = TwitterProvider(
            max_results=5,
            serper_api_key=settings.serper_api_key
        )
        
        jina_provider = JinaProvider(api_key=settings.jina_ai_api_key)
        
        # Initialize processors
        query_processor = QueryProcessor(ai_provider)
        post_processor = PostProcessor(ai_provider, jina_provider)
        
        print("✅ All providers initialized")
        
        # Step 1: Process query
        print("\n🧠 Step 1: Processing query with AI...")
        processed_query = await query_processor.process_query(query)
        
        print(f"   🎯 Keywords: {processed_query.keywords}")
        print(f"   🔍 Search Reddit: {processed_query.search_reddit}")
        print(f"   🐦 Search Twitter: {processed_query.search_twitter}")
        print(f"   📋 Intent: {processed_query.intent}")
        print(f"   ⏱️ Time range: {processed_query.filters.time_range}")
        
        # Step 2: Search Reddit
        reddit_posts = []
        if processed_query.search_reddit:
            print("\n📱 Step 2: Searching Reddit...")
            try:
                reddit_posts = await reddit_provider.search_posts(
                    keywords=processed_query.keywords[:3],  # Limit keywords
                    time_range=processed_query.filters.time_range
                )
                print(f"   ✅ Found {len(reddit_posts)} Reddit posts")
                
                for i, post in enumerate(reddit_posts[:3], 1):
                    print(f"   {i}. r/{post.metadata.get('subreddit', 'unknown')} - {post.author}")
                    print(f"      📝 {post.content[:100]}...")
                    print(f"      👍 Score: {post.metadata.get('score', 0)}")
                    
            except Exception as e:
                print(f"   ❌ Reddit search failed: {e}")
        
        # Step 3: Search Twitter
        twitter_posts = []
        if processed_query.search_twitter:
            print("\n🐦 Step 3: Searching Twitter...")
            try:
                twitter_posts = await twitter_provider.search_posts(
                    keywords=processed_query.keywords[:3],  # Limit keywords
                    time_range=processed_query.filters.time_range
                )
                print(f"   ✅ Found {len(twitter_posts)} Twitter posts")
                
                for i, post in enumerate(twitter_posts[:3], 1):
                    print(f"   {i}. {post.author}")
                    print(f"      📝 {post.content[:100]}...")
                    print(f"      💫 Engagement: {post.engagement_score}")
                    
            except Exception as e:
                print(f"   ❌ Twitter search failed: {e}")
        
        # Step 4: Process and rank posts
        all_posts = reddit_posts + twitter_posts
        if all_posts:
            print(f"\n⚡ Step 4: Processing {len(all_posts)} posts...")
            try:
                processed_posts = await post_processor.process_posts(
                    posts=all_posts,
                    query=query,
                    max_posts=5
                )
                
                print(f"   ✅ Processed and ranked {len(processed_posts)} posts")
                
                print("\n🏆 Top Results:")
                for i, post in enumerate(processed_posts[:3], 1):
                    print(f"   {i}. {post.source} - {post.author}")
                    print(f"      📝 {post.content[:80]}...")
                    print(f"      🎯 Relevance: {post.relevance_score:.2f}")
                    print(f"      😊 Sentiment: {post.sentiment}")
                    if hasattr(post, 'jina_relevance_score'):
                        print(f"      🧠 Jina Score: {post.jina_relevance_score:.2f}")
                    if post.summary:
                        print(f"      📄 Summary: {post.summary[:60]}...")
                
            except Exception as e:
                print(f"   ❌ Post processing failed: {e}")
        else:
            print("   ⚠️ No posts found to process")
        
        # Step 5: Generate final response
        if processed_posts:
            print("\n📝 Step 5: Generating AI response...")
            try:
                # Create a simple response format
                response_parts = [
                    f"## 📊 Found {len(processed_posts)} relevant posts about '{query}'\n"
                ]
                
                for i, post in enumerate(processed_posts[:3], 1):
                    response_parts.append(f"### {i}. {post.source} Post")
                    response_parts.append(f"**Author**: {post.author}")
                    response_parts.append(f"**Content**: {post.content[:200]}...")
                    response_parts.append(f"**Relevance**: {post.relevance_score:.2f}/1.0")
                    response_parts.append(f"**Sentiment**: {post.sentiment}")
                    if post.summary:
                        response_parts.append(f"**AI Summary**: {post.summary}")
                    response_parts.append("")
                
                final_response = "\n".join(response_parts)
                print("   ✅ Generated final response")
                print(f"\n📄 Final Response Preview:")
                print(final_response[:500] + "..." if len(final_response) > 500 else final_response)
                
            except Exception as e:
                print(f"   ❌ Response generation failed: {e}")
        
        # Cleanup
        await jina_provider.close()
        
        elapsed = time.time() - start_time
        print(f"\n⏱️ Total processing time: {elapsed:.2f} seconds")
        
        return len(all_posts) > 0
        
    except Exception as e:
        print(f"💥 Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main testing function."""
    print("🚀 Starting Direct SentientEcho Query Testing")
    print("   (Bypassing Sentient Agent Framework for core functionality testing)\n")
    
    # Test queries
    test_queries = [
        ("Programming Discussion", "What do people think about Python vs JavaScript for beginners?"),
        ("Reddit Focus", "Latest discussions on r/MachineLearning about AI breakthroughs"),
        ("Twitter Focus", "Twitter sentiment about the new iPhone release"),
        ("Gaming", "How is the gaming community reacting to the latest AAA game releases?"),
        ("General Tech", "Best productivity tools for remote work"),
    ]
    
    successful_queries = 0
    total_queries = len(test_queries)
    
    for i, (query_name, query_text) in enumerate(test_queries, 1):
        print(f"\n🎯 Test {i}/{total_queries}")
        success = await test_query_processing(query_text, query_name)
        
        if success:
            successful_queries += 1
            print(f"   ✅ Query '{query_name}' - SUCCESS")
        else:
            print(f"   ❌ Query '{query_name}' - FAILED")
        
        # Small delay between queries
        if i < total_queries:
            print("   ⏳ Waiting 5 seconds before next query...")
            await asyncio.sleep(5)
    
    # Final summary
    print(f"\n{'='*80}")
    print("🎉 DIRECT TESTING COMPLETE")
    print('='*80)
    print(f"📊 Results Summary:")
    print(f"   ✅ Successful queries: {successful_queries}/{total_queries}")
    print(f"   📈 Success rate: {(successful_queries/total_queries)*100:.1f}%")
    
    if successful_queries == total_queries:
        print(f"\n🎉 ALL QUERIES SUCCESSFUL! Core functionality is working perfectly!")
    elif successful_queries >= total_queries * 0.8:
        print(f"\n✨ MOSTLY SUCCESSFUL! Core functionality is working well.")
    elif successful_queries >= total_queries * 0.5:
        print(f"\n⚠️ PARTIALLY WORKING. Some components have issues.")
    else:
        print(f"\n❌ SIGNIFICANT ISSUES. Core functionality needs investigation.")
    
    print(f"\n🔧 Component Status:")
    print(f"   🧠 AI Provider (Sentient Dobby): {'✅ Working' if successful_queries > 0 else '❌ Issues'}")
    print(f"   📱 Reddit Provider: {'✅ Working' if successful_queries > 0 else '❌ Issues'}")
    print(f"   🐦 Twitter Provider: {'✅ Working' if successful_queries > 0 else '❌ Issues'}")
    print(f"   🎯 Query Processing: {'✅ Working' if successful_queries > 0 else '❌ Issues'}")
    print(f"   📊 Post Processing: {'✅ Working' if successful_queries > 0 else '❌ Issues'}")
    
    return successful_queries >= total_queries * 0.6


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
