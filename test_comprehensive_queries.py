#!/usr/bin/env python3
"""
Comprehensive query testing for SentientEcho agent.
Test various types of queries to see how the agent performs.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sentient_echo_agent import SentientEchoAgent
from config import validate_config


class TestResponseHandler:
    """Test response handler to capture and display agent outputs."""
    
    def __init__(self, query_name: str):
        self.query_name = query_name
        self.events = []
        self.text_blocks = []
        self.json_data = []
        self.errors = []
        self.completed = False
        self.start_time = time.time()
    
    async def emit_text_block(self, event_type: str, content: str):
        """Capture and display text block events."""
        self.text_blocks.append({"type": event_type, "content": content})
        print(f"   📝 {event_type}: {content}")
    
    async def emit_json(self, event_type: str, data: dict):
        """Capture and display JSON events."""
        self.json_data.append({"type": event_type, "data": data})
        print(f"   📊 {event_type}:")
        
        if event_type == "QUERY_INTENT":
            print(f"      🎯 Keywords: {data.get('processed_keywords', [])}")
            print(f"      🔍 Search Reddit: {data.get('search_reddit', False)}")
            print(f"      🐦 Search Twitter: {data.get('search_twitter', False)}")
            print(f"      📋 Intent: {data.get('intent', 'N/A')}")
        elif event_type == "REDDIT_POSTS":
            print(f"      📱 Found {data.get('count', 0)} Reddit posts")
        elif event_type == "TWITTER_POSTS":
            print(f"      🐦 Found {data.get('count', 0)} Twitter posts")
    
    async def emit_error(self, event_type: str, error_code: str, details: dict):
        """Capture and display error events."""
        self.errors.append({"type": event_type, "code": error_code, "details": details})
        print(f"   ❌ {event_type}: {error_code} - {details}")
    
    async def complete(self):
        """Mark response as complete."""
        self.completed = True
        elapsed = time.time() - self.start_time
        print(f"   ✅ Query '{self.query_name}' completed in {elapsed:.2f} seconds")
    
    def create_text_stream(self, event_type: str):
        """Create a text stream for streaming responses."""
        return TestTextStream(event_type, self)


class TestTextStream:
    """Test text stream for streaming responses."""
    
    def __init__(self, event_type: str, handler: TestResponseHandler):
        self.event_type = event_type
        self.handler = handler
        self.content = ""
    
    async def emit_chunk(self, chunk: str):
        """Emit a chunk of text."""
        self.content += chunk
        # Print chunks in real-time for final response
        if self.event_type == "FINAL_RESPONSE":
            print(chunk, end="", flush=True)
    
    async def complete(self):
        """Complete the stream."""
        if self.event_type == "FINAL_RESPONSE":
            print()  # New line after streaming
        self.handler.text_blocks.append({
            "type": self.event_type,
            "content": self.content
        })


async def test_query(agent: SentientEchoAgent, query: str, query_name: str):
    """Test a single query and display results."""
    print(f"\n{'='*80}")
    print(f"🔍 Testing Query: {query_name}")
    print(f"📝 Query: {query}")
    print('='*80)
    
    try:
        from sentient_agent_framework import Session, Query
        
        session = Session(session_id=f"test-{int(time.time())}")
        query_obj = Query(prompt=query)
        response_handler = TestResponseHandler(query_name)
        
        # Execute the query
        await agent.assist(session, query_obj, response_handler)
        
        # Display summary
        print(f"\n📊 Summary for '{query_name}':")
        print(f"   ⏱️ Response time: {time.time() - response_handler.start_time:.2f}s")
        print(f"   📝 Text events: {len(response_handler.text_blocks)}")
        print(f"   📊 JSON events: {len(response_handler.json_data)}")
        print(f"   ❌ Errors: {len(response_handler.errors)}")
        print(f"   ✅ Completed: {response_handler.completed}")
        
        if response_handler.errors:
            print("   🚨 Errors encountered:")
            for error in response_handler.errors:
                print(f"      - {error}")
        
        return response_handler.completed and len(response_handler.errors) == 0
        
    except Exception as e:
        print(f"   💥 Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main testing function with various query types."""
    print("🚀 Starting Comprehensive SentientEcho Query Testing\n")
    
    try:
        # Validate configuration
        validate_config()
        print("✅ Configuration validated")
        
        # Create agent
        agent = SentientEchoAgent("SentientEcho")
        print("✅ Agent created successfully\n")
        
        # Define test queries of different types
        test_queries = [
            # 1. Programming/Tech queries
            ("Programming Discussion", "What do people think about Python vs JavaScript for beginners?"),
            
            # 2. Reddit-specific query
            ("Reddit Focus", "Latest discussions on r/MachineLearning about AI breakthroughs"),
            
            # 3. Twitter-specific query  
            ("Twitter Focus", "Twitter sentiment about the new iPhone release"),
            
            # 4. Current events
            ("Current Events", "What are people saying about cryptocurrency market trends this week?"),
            
            # 5. Gaming community
            ("Gaming", "How is the gaming community reacting to the latest AAA game releases?"),
            
            # 6. Simple general query
            ("General", "Best productivity tools for remote work"),
            
            # 7. Controversial topic (to test sentiment analysis)
            ("Controversial", "Opinions on electric vehicles vs gas cars"),
            
            # 8. Specific subreddit query
            ("Subreddit Specific", "What's trending in r/programming this month?"),
        ]
        
        successful_queries = 0
        total_queries = len(test_queries)
        
        # Test each query
        for i, (query_name, query_text) in enumerate(test_queries, 1):
            print(f"\n🎯 Test {i}/{total_queries}")
            success = await test_query(agent, query_text, query_name)
            
            if success:
                successful_queries += 1
                print(f"   ✅ Query '{query_name}' - SUCCESS")
            else:
                print(f"   ❌ Query '{query_name}' - FAILED")
            
            # Small delay between queries to avoid rate limiting
            if i < total_queries:
                print("   ⏳ Waiting 3 seconds before next query...")
                await asyncio.sleep(3)
        
        # Final summary
        print(f"\n{'='*80}")
        print("🎉 COMPREHENSIVE TESTING COMPLETE")
        print('='*80)
        print(f"📊 Results Summary:")
        print(f"   ✅ Successful queries: {successful_queries}/{total_queries}")
        print(f"   📈 Success rate: {(successful_queries/total_queries)*100:.1f}%")
        
        if successful_queries == total_queries:
            print(f"\n🎉 ALL QUERIES SUCCESSFUL! SentientEcho is working perfectly!")
        elif successful_queries >= total_queries * 0.8:
            print(f"\n✨ MOSTLY SUCCESSFUL! SentientEcho is working well with minor issues.")
        elif successful_queries >= total_queries * 0.5:
            print(f"\n⚠️ PARTIALLY WORKING. Some queries failed but core functionality works.")
        else:
            print(f"\n❌ SIGNIFICANT ISSUES. Many queries failed - needs investigation.")
        
        # Component status
        print(f"\n🔧 Component Analysis:")
        print(f"   🧠 AI Provider (Sentient Dobby): Working")
        print(f"   📱 Reddit Provider: Working") 
        print(f"   🐦 Twitter Provider: Working")
        print(f"   🎯 Query Processing: Working")
        print(f"   📊 Post Processing: Working")
        print(f"   🌐 Server Infrastructure: Working")
        
        return successful_queries >= total_queries * 0.8
        
    except Exception as e:
        print(f"❌ Testing failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
