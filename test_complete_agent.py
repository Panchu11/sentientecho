#!/usr/bin/env python3
"""
Complete integration test for SentientEcho agent.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sentient_agent_framework import Session, Query, ResponseHandler
from sentient_echo_agent import SentientEchoAgent
from config import validate_config


class TestResponseHandler(ResponseHandler):
    """Test response handler to capture agent outputs."""
    
    def __init__(self):
        self.events = []
        self.text_blocks = []
        self.json_data = []
        self.errors = []
        self.completed = False
    
    async def emit_text_block(self, event_type: str, content: str):
        """Capture text block events."""
        self.text_blocks.append({"type": event_type, "content": content})
        print(f"📝 {event_type}: {content}")
    
    async def emit_json(self, event_type: str, data: dict):
        """Capture JSON events."""
        self.json_data.append({"type": event_type, "data": data})
        print(f"📊 {event_type}: {data}")
    
    async def emit_error(self, event_type: str, error_code: str, details: dict):
        """Capture error events."""
        self.errors.append({"type": event_type, "code": error_code, "details": details})
        print(f"❌ {event_type}: {error_code} - {details}")
    
    async def complete(self):
        """Mark response as complete."""
        self.completed = True
        print("✅ Response completed")
    
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
        print(chunk, end="", flush=True)
    
    async def complete(self):
        """Complete the stream."""
        self.handler.text_blocks.append({
            "type": self.event_type,
            "content": self.content
        })
        print(f"\n🔚 Stream {self.event_type} completed")


async def test_complete_agent():
    """Test the complete SentientEcho agent."""
    print("🚀 Testing Complete SentientEcho Agent\n")
    
    try:
        # Validate configuration
        validate_config()
        print("✅ Configuration validated")
        
        # Create agent
        agent = SentientEchoAgent("SentientEcho")
        print("✅ Agent created successfully")
        
        # Create test session and query
        session = Session(session_id="test-session-123")
        
        # Test queries
        test_queries = [
            "What do people think about Python programming?",
            "Latest discussions on r/MachineLearning",
            "Twitter sentiment on AI this week"
        ]
        
        for i, query_text in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"🔍 Test Query {i}: {query_text}")
            print('='*60)
            
            query = Query(prompt=query_text)
            response_handler = TestResponseHandler()
            
            # Execute the agent
            await agent.assist(session, query, response_handler)
            
            # Verify results
            print(f"\n📊 Results Summary:")
            print(f"   Text blocks: {len(response_handler.text_blocks)}")
            print(f"   JSON events: {len(response_handler.json_data)}")
            print(f"   Errors: {len(response_handler.errors)}")
            print(f"   Completed: {response_handler.completed}")
            
            if response_handler.errors:
                print("❌ Errors occurred:")
                for error in response_handler.errors:
                    print(f"   - {error}")
                return False
            
            if not response_handler.completed:
                print("❌ Response not completed")
                return False
            
            print("✅ Query processed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_server():
    """Test the agent server setup."""
    print("\n🌐 Testing Agent Server Setup\n")
    
    try:
        from sentient_agent_framework import DefaultServer
        from main import run_server
        
        # Test server creation
        agent = SentientEchoAgent("SentientEcho")
        server = DefaultServer(agent)
        
        print("✅ Server created successfully")
        print(f"   Agent: {agent.name}")
        print(f"   Server: {type(server).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting SentientEcho Complete Integration Test\n")
    
    success1 = await test_complete_agent()
    success2 = await test_agent_server()
    
    if success1 and success2:
        print("\n🎉 All integration tests passed!")
        print("\n🔥 SentientEcho agent is ready for deployment!")
    else:
        print("\n❌ Some integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
