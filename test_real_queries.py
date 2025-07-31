#!/usr/bin/env python3
"""
Real-world query testing for SentientEcho agent.
Test with actual queries you might ask the agent.
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


async def process_real_query(query: str):
    """Process a real query end-to-end and show the full response."""
    print(f"\n{'='*100}")
    print(f"🔍 QUERY: {query}")
    print('='*100)
    
    start_time = time.time()
    
    try:
        settings = get_settings()
        
        # Initialize providers
        ai_provider = AIProvider(
            api_key=settings.fireworks_api_key,
            model_id=settings.fireworks_model_id
        )
        
        reddit_provider = RedditProvider(max_results=5)
        twitter_provider = TwitterProvider(
            max_results=5,
            serper_api_key=settings.serper_api_key
        )
        
        # Step 1: AI Query Processing
        print("🧠 STEP 1: AI Analysis...")
        ai_result = await ai_provider.process_query(query)
        keywords = ai_result.get('keywords', [])
        search_reddit = ai_result.get('search_reddit', True)
        search_twitter = ai_result.get('search_twitter', True)
        intent = ai_result.get('intent', 'General query')
        
        print(f"   🎯 Intent: {intent}")
        print(f"   🔑 Keywords: {keywords}")
        print(f"   📱 Search Reddit: {search_reddit}")
        print(f"   🐦 Search Twitter: {search_twitter}")
        
        # Step 2: Content Search
        print("\n🔍 STEP 2: Content Search...")
        all_posts = []
        
        if search_reddit:
            try:
                reddit_posts = await reddit_provider.search_posts(
                    keywords=keywords[:3],
                    time_range="week"
                )
                all_posts.extend(reddit_posts)
                print(f"   📱 Reddit: Found {len(reddit_posts)} posts")
            except Exception as e:
                print(f"   ❌ Reddit search failed: {e}")
        
        if search_twitter:
            try:
                twitter_posts = await twitter_provider.search_posts(
                    keywords=keywords[:3],
                    time_range="week"
                )
                all_posts.extend(twitter_posts)
                print(f"   🐦 Twitter: Found {len(twitter_posts)} posts")
            except Exception as e:
                print(f"   ❌ Twitter search failed: {e}")
        
        print(f"   📊 Total posts found: {len(all_posts)}")
        
        if not all_posts:
            print("\n❌ No posts found for this query.")
            return False
        
        # Step 3: AI Enhancement
        print("\n⚡ STEP 3: AI Enhancement...")
        enhanced_posts = []
        
        for i, post in enumerate(all_posts[:5], 1):  # Limit to 5 posts
            try:
                print(f"   Processing post {i}/{min(len(all_posts), 5)}...")
                
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
                print(f"   ⚠️ Enhancement failed for post {i}: {e}")
                enhanced_posts.append(post)
        
        # Sort by relevance
        enhanced_posts.sort(key=lambda x: getattr(x, 'relevance_score', 0.5), reverse=True)
        
        print(f"   ✅ Enhanced {len(enhanced_posts)} posts")
        
        # Step 4: Generate Final Response
        print("\n📝 STEP 4: Final Response Generation...")
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*100}")
        print(f"🎉 SENTIENTECHO RESPONSE (Generated in {elapsed:.1f}s)")
        print('='*100)
        
        print(f"\n## 📊 Analysis Results for: '{query}'")
        print(f"\n**🎯 Intent**: {intent}")
        print(f"**🔍 Sources**: {len([p for p in enhanced_posts if p.source == 'Reddit'])} Reddit posts, {len([p for p in enhanced_posts if p.source == 'Twitter'])} Twitter posts")
        print(f"**⏱️ Time Range**: Past week")
        
        print(f"\n## 🏆 Top {len(enhanced_posts)} Most Relevant Posts:")
        
        for i, post in enumerate(enhanced_posts, 1):
            print(f"\n### {i}. {post.source} Post")
            print(f"**👤 Author**: {post.author}")
            
            if post.source == "Reddit":
                subreddit = post.metadata.get('subreddit', 'unknown')
                score = post.metadata.get('score', 0)
                print(f"**📍 Subreddit**: r/{subreddit}")
                print(f"**👍 Score**: {score} upvotes")
            else:
                print(f"**💫 Engagement**: {post.engagement_score}")
            
            print(f"**🎯 Relevance**: {getattr(post, 'relevance_score', 0.5):.2f}/1.0")
            print(f"**😊 Sentiment**: {getattr(post, 'sentiment', 'neutral')}")
            
            # Show content
            content = post.content
            if len(content) > 300:
                content = content[:300] + "..."
            print(f"**📝 Content**: {content}")
            
            # Show AI summary
            if hasattr(post, 'summary') and post.summary:
                summary = post.summary
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                print(f"**🤖 AI Summary**: {summary}")
            
            # Show URL if available
            if post.url:
                print(f"**🔗 Link**: {post.url}")
        
        # Generate overall summary
        print(f"\n## 🎯 Overall Insights:")
        
        sentiments = [getattr(p, 'sentiment', 'neutral') for p in enhanced_posts]
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        neutral_count = sentiments.count('neutral')
        
        print(f"- **Sentiment Distribution**: {positive_count} positive, {neutral_count} neutral, {negative_count} negative")
        
        reddit_posts = [p for p in enhanced_posts if p.source == 'Reddit']
        twitter_posts = [p for p in enhanced_posts if p.source == 'Twitter']
        
        if reddit_posts:
            avg_reddit_score = sum(p.metadata.get('score', 0) for p in reddit_posts) / len(reddit_posts)
            print(f"- **Reddit Engagement**: Average {avg_reddit_score:.0f} upvotes")
        
        if twitter_posts:
            avg_twitter_engagement = sum(p.engagement_score for p in twitter_posts) / len(twitter_posts)
            print(f"- **Twitter Engagement**: Average {avg_twitter_engagement:.0f} engagement score")
        
        avg_relevance = sum(getattr(p, 'relevance_score', 0.5) for p in enhanced_posts) / len(enhanced_posts)
        print(f"- **Average Relevance**: {avg_relevance:.2f}/1.0")
        
        print(f"\n*Generated by SentientEcho AI Agent • Powered by Sentient Dobby Llama 3 70B*")
        
        return True
        
    except Exception as e:
        print(f"💥 Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Test with real-world queries."""
    print("🚀 SentientEcho Real-World Query Testing")
    print("   Testing with actual queries you might ask the agent...\n")
    
    # Real queries to test
    test_queries = [
        "What do people think about the new iPhone 15?",
        "Latest discussions about AI and machine learning",
        "How is the gaming community reacting to Baldur's Gate 3?",
        "What are developers saying about Python vs JavaScript?",
        "Opinions on electric vehicles and Tesla",
    ]
    
    print(f"📋 Testing {len(test_queries)} real-world queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"   {i}. {query}")
    
    print(f"\n⚠️ Note: Each query will take 15-30 seconds to process completely.")
    print(f"🔄 Processing queries one by one...\n")
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🎯 PROCESSING QUERY {i}/{len(test_queries)}")
        success = await process_real_query(query)
        
        if success:
            successful_queries += 1
            print(f"\n✅ Query {i} completed successfully!")
        else:
            print(f"\n❌ Query {i} failed!")
        
        # Wait between queries
        if i < len(test_queries):
            print(f"\n⏳ Waiting 5 seconds before next query...")
            await asyncio.sleep(5)
    
    # Final summary
    print(f"\n{'='*100}")
    print("🎉 REAL-WORLD TESTING COMPLETE")
    print('='*100)
    print(f"📊 Final Results:")
    print(f"   ✅ Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"   📈 Success rate: {(successful_queries/len(test_queries))*100:.1f}%")
    
    if successful_queries == len(test_queries):
        print(f"\n🎉 PERFECT! All queries processed successfully!")
        print(f"🚀 SentientEcho is ready for real-world deployment!")
    elif successful_queries >= len(test_queries) * 0.8:
        print(f"\n✨ EXCELLENT! Most queries worked perfectly!")
        print(f"🔧 Minor issues but overall very functional!")
    else:
        print(f"\n⚠️ Some issues detected. Needs investigation.")
    
    return successful_queries >= len(test_queries) * 0.6


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
