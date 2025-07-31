# SentientEcho Developer Guide 👨‍💻

**Complete guide for developers working on SentientEcho codebase.**

## 🏗️ **Project Structure**

### **Core Architecture**
```
src/
├── sentient_echo_agent.py      # Main agent implementation
├── server.py                   # Custom FastAPI server
├── config.py                   # Configuration management
├── main.py                     # Application entry point
├── models/                     # Data models and schemas
│   ├── __init__.py
│   ├── query_models.py         # Query-related models
│   ├── response_models.py      # Response models
│   └── content_models.py       # Content data models
├── processors/                 # Query and content processors
│   ├── __init__.py
│   ├── query_processor.py      # AI-powered query analysis
│   └── post_processor.py       # Content enhancement
├── providers/                  # External service providers
│   ├── __init__.py
│   ├── ai_provider.py          # Fireworks AI integration
│   ├── reddit_provider.py      # Reddit content fetching
│   ├── twitter_provider.py     # Twitter content fetching
│   └── jina_provider.py        # Jina AI embeddings
└── utils/                      # Utility modules
    ├── __init__.py
    ├── cache_manager.py        # Caching system
    ├── rate_limiter.py         # Rate limiting
    ├── security.py             # Security utilities
    └── helpers.py              # General helpers
```

## 🚀 **Development Setup**

### **Prerequisites**
- Python 3.8+
- Docker & Docker Compose
- Git
- API Keys (Fireworks, Serper, Jina AI)

### **Local Development**
```bash
# 1. Clone repository
git clone https://github.com/Panchu11/sentientecho.git
cd sentientecho

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 5. Validate setup
python setup.py

# 6. Run locally
python src/main.py
```

### **Docker Development**
```bash
# Build and run with Docker
docker-compose up --build

# Development with hot reload
docker-compose -f docker-compose.dev.yml up
```

## 🧩 **Core Components**

### **1. SentientEchoAgent**
**File**: `src/sentient_echo_agent.py`

Main agent class implementing the Sentient Agent Framework:

```python
class SentientEchoAgent(AbstractAgent):
    def __init__(self, name: str):
        super().__init__(name)
        self.query_processor = QueryProcessor()
        self.post_processor = PostProcessor()
        # Initialize providers...
    
    async def assist(self, session, query, response_handler):
        # Main query processing logic
        pass
```

**Key Methods**:
- `assist()` - Main entry point for query processing
- `_process_query()` - AI-powered query analysis
- `_search_content()` - Multi-platform content search
- `_enhance_content()` - AI content enhancement
- `_generate_response()` - Response formatting and streaming

### **2. Query Processor**
**File**: `src/processors/query_processor.py`

Handles AI-powered query understanding:

```python
class QueryProcessor:
    async def process_query(self, query: str) -> QueryIntent:
        # Extract keywords, determine intent, select platforms
        pass
    
    async def extract_keywords(self, query: str) -> List[str]:
        # AI-powered keyword extraction
        pass
```

**Responsibilities**:
- Intent recognition (opinion, factual, comparison, etc.)
- Keyword extraction and optimization
- Platform selection (Reddit vs Twitter focus)
- Search parameter generation

### **3. Content Providers**

#### **Reddit Provider**
**File**: `src/providers/reddit_provider.py`

```python
class RedditProvider:
    async def search_posts(self, keywords: List[str], 
                          time_range: str = "month") -> List[RedditPost]:
        # Search Reddit using JSON API
        pass
```

#### **Twitter Provider**
**File**: `src/providers/twitter_provider.py`

```python
class TwitterProvider:
    async def search_posts(self, keywords: List[str],
                          time_range: str = "week") -> List[TwitterPost]:
        # Search Twitter using Serper API
        pass
```

#### **AI Provider**
**File**: `src/providers/ai_provider.py`

```python
class AIProvider:
    async def process_query(self, query: str) -> QueryIntent:
        # Sentient Dobby query processing
        pass
    
    async def summarize_content(self, content: str) -> str:
        # AI content summarization
        pass
```

### **4. Post Processor**
**File**: `src/processors/post_processor.py`

Enhances content with AI analysis:

```python
class PostProcessor:
    async def enhance_posts(self, posts: List[Post]) -> List[EnhancedPost]:
        # Add summaries, sentiment, relevance scores
        pass
    
    async def rank_by_relevance(self, posts: List[Post], 
                               query: str) -> List[Post]:
        # AI-powered relevance ranking
        pass
```

## 🔧 **Adding New Features**

### **Adding a New Content Provider**

1. **Create Provider Class**:
```python
# src/providers/new_provider.py
class NewProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search_posts(self, keywords: List[str]) -> List[Post]:
        # Implement search logic
        pass
```

2. **Add Configuration**:
```python
# src/config.py
NEW_PROVIDER_API_KEY = os.getenv("NEW_PROVIDER_API_KEY")
```

3. **Integrate in Agent**:
```python
# src/sentient_echo_agent.py
from providers.new_provider import NewProvider

class SentientEchoAgent:
    def __init__(self, name: str):
        # ...
        self.new_provider = NewProvider(config.NEW_PROVIDER_API_KEY)
    
    async def _search_content(self, intent: QueryIntent):
        # Add new provider to search logic
        new_posts = await self.new_provider.search_posts(intent.keywords)
```

### **Adding New AI Capabilities**

1. **Extend AI Provider**:
```python
# src/providers/ai_provider.py
class AIProvider:
    async def new_ai_function(self, input_data: str) -> str:
        prompt = f"New AI task: {input_data}"
        response = await self._call_ai(prompt)
        return response
```

2. **Add to Processing Pipeline**:
```python
# src/processors/post_processor.py
async def enhance_posts(self, posts: List[Post]) -> List[EnhancedPost]:
    for post in posts:
        # Existing enhancements...
        post.new_ai_field = await self.ai_provider.new_ai_function(post.content)
```

### **Adding New Endpoints**

1. **Add to Server**:
```python
# src/server.py
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "New endpoint"}
```

2. **Add Documentation**:
```python
@app.get("/new-endpoint", 
         summary="New Endpoint",
         description="Description of new endpoint")
async def new_endpoint():
    pass
```

## 🧪 **Testing**

### **Test Structure**
```
tests/
├── __init__.py
├── test_config.py              # Configuration tests
├── test_integration.py         # Integration tests
├── unit/                       # Unit tests
│   ├── test_query_processor.py
│   ├── test_post_processor.py
│   └── test_providers.py
└── fixtures/                   # Test data
    ├── sample_queries.json
    └── sample_responses.json
```

### **Writing Tests**

#### **Unit Tests**:
```python
# tests/unit/test_query_processor.py
import pytest
from src.processors.query_processor import QueryProcessor

@pytest.mark.asyncio
async def test_extract_keywords():
    processor = QueryProcessor()
    keywords = await processor.extract_keywords("What do people think about Python?")
    assert "Python" in keywords
    assert len(keywords) > 0
```

#### **Integration Tests**:
```python
# tests/test_integration.py
async def test_full_query_flow():
    agent = SentientEchoAgent("test")
    session = MockSession("test")
    query = MockQuery("test query")
    handler = MockResponseHandler()
    
    await agent.assist(session, query, handler)
    assert handler.completed
```

### **Running Tests**
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_integration.py

# Run with coverage
python -m pytest --cov=src tests/

# Run integration tests only
python tests/test_integration.py
```

## 🔍 **Debugging**

### **Debug Configuration**
```env
# .env
LOG_LEVEL=DEBUG
DEBUG=true
ENABLE_REQUEST_LOGGING=true
```

### **Debug Techniques**

#### **Logging**:
```python
import logging
logger = logging.getLogger(__name__)

async def some_function():
    logger.debug("Debug information")
    logger.info("Processing query: %s", query)
    logger.error("Error occurred: %s", error)
```

#### **Breakpoints**:
```python
import pdb; pdb.set_trace()  # Python debugger
# or
breakpoint()  # Python 3.7+
```

#### **Response Inspection**:
```python
# Add debug endpoints
@app.get("/debug/cache")
async def debug_cache():
    return cache_manager.get_stats()

@app.get("/debug/providers")
async def debug_providers():
    return {
        "reddit": await reddit_provider.health_check(),
        "twitter": await twitter_provider.health_check()
    }
```

## 📊 **Performance Optimization**

### **Profiling**
```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()
await some_function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### **Async Optimization**
```python
# Use asyncio.gather for parallel operations
results = await asyncio.gather(
    reddit_provider.search_posts(keywords),
    twitter_provider.search_posts(keywords),
    return_exceptions=True
)

# Use connection pooling
connector = aiohttp.TCPConnector(limit=100)
session = aiohttp.ClientSession(connector=connector)
```

### **Caching Strategies**
```python
# Add caching to expensive operations
@cache_manager.cached(ttl=300)
async def expensive_ai_operation(input_data: str) -> str:
    return await ai_provider.process(input_data)
```

## 🔒 **Security Considerations**

### **Input Validation**
```python
from src.utils.security import validate_input, sanitize_query

async def process_query(query: str):
    # Validate input
    if not validate_input(query):
        raise ValueError("Invalid query")
    
    # Sanitize for safety
    clean_query = sanitize_query(query)
    return await self._process_clean_query(clean_query)
```

### **API Key Management**
```python
# Never hardcode API keys
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

# Use secure headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "User-Agent": "SentientEcho/1.0"
}
```

### **Rate Limiting**
```python
from src.utils.rate_limiter import RateLimiter

rate_limiter = RateLimiter(requests_per_minute=60)

async def api_call():
    await rate_limiter.acquire()
    # Make API call
```

## 📝 **Code Style & Standards**

### **Python Style**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Use async/await for I/O operations

### **Example Function**:
```python
async def process_query(self, query: str, session_id: str) -> QueryResult:
    """
    Process a user query and return enhanced results.
    
    Args:
        query: The user's natural language query
        session_id: Unique session identifier
        
    Returns:
        QueryResult containing processed content and metadata
        
    Raises:
        ValueError: If query is invalid
        APIError: If external API calls fail
    """
    logger.info("Processing query for session %s", session_id)
    
    # Implementation...
    
    return QueryResult(
        content=enhanced_content,
        metadata=query_metadata
    )
```

### **Error Handling**:
```python
try:
    result = await external_api_call()
except aiohttp.ClientError as e:
    logger.error("API call failed: %s", e)
    raise APIError(f"External service unavailable: {e}")
except Exception as e:
    logger.exception("Unexpected error in process_query")
    raise ProcessingError(f"Query processing failed: {e}")
```

## 🚀 **Deployment**

### **Production Checklist**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] API keys valid
- [ ] Docker build successful
- [ ] Health checks working
- [ ] Monitoring configured
- [ ] Security review completed

### **CI/CD Pipeline**
```yaml
# .github/workflows/deploy.yml
name: Deploy SentientEcho
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python -m pytest tests/
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: docker-compose up -d
```

---

**Happy coding! Remember to test thoroughly and follow security best practices.** 👨‍💻
