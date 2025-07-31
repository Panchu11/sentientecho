# SentientEcho Configuration Guide ⚙️

**Complete guide to configuring and tuning SentientEcho for optimal performance.**

## 📋 **Configuration Overview**

SentientEcho uses environment variables for all configuration. This allows easy deployment across different environments without code changes.

### **Configuration Files**
- **`.env`** - Main configuration file (create from `.env.example`)
- **`docker-compose.yml`** - Docker deployment configuration
- **`src/config.py`** - Configuration validation and defaults

## 🔑 **Required Configuration**

### **API Keys (Required)**
```env
# Fireworks AI (Sentient Dobby Llama 3 70B)
FIREWORKS_API_KEY=fw_your_fireworks_api_key_here
FIREWORKS_MODEL_ID=accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new

# Serper.dev (Twitter/Google Search)
SERPER_API_KEY=your_serper_api_key_here

# Jina AI (Embeddings and Reranking)
JINA_AI_API_KEY=jina_your_jina_api_key_here
```

**How to Get API Keys**:
1. **Fireworks**: https://fireworks.ai/account/api-keys
2. **Serper**: https://serper.dev/api-key
3. **Jina AI**: https://jina.ai/embeddings/

### **Basic Agent Configuration**
```env
# Agent Identity
AGENT_NAME=SentientEcho
AGENT_VERSION=1.0.0
AGENT_DESCRIPTION="Answers queries using real Reddit and Twitter posts"

# Server Configuration
AGENT_HOST=0.0.0.0
AGENT_PORT=8000
```

## ⚡ **Performance Configuration**

### **Content Limits**
```env
# Reddit Configuration
MAX_REDDIT_POSTS=10          # Max posts to fetch from Reddit
REDDIT_TIME_RANGE=month      # Time range: hour, day, week, month, year
REDDIT_SORT=relevance        # Sort: relevance, hot, top, new

# Twitter Configuration  
MAX_TWITTER_POSTS=10         # Max posts to fetch from Twitter
TWITTER_TIME_RANGE=week      # Time range: hour, day, week, month
TWITTER_INCLUDE_REPLIES=false # Include reply tweets

# AI Processing
MAX_AI_SUMMARY_LENGTH=200    # Max characters for AI summaries
AI_BATCH_SIZE=5              # Process posts in batches
```

### **Caching Configuration**
```env
# Cache Settings
ENABLE_CACHING=true          # Enable/disable caching
CACHE_TTL_SECONDS=300        # Cache time-to-live (5 minutes)
CACHE_MAX_SIZE=1000          # Maximum cache entries
CACHE_CLEANUP_INTERVAL=60    # Cleanup interval in seconds

# Cache Types
ENABLE_QUERY_CACHE=true      # Cache query results
ENABLE_CONTENT_CACHE=true    # Cache fetched content
ENABLE_AI_CACHE=true         # Cache AI responses
```

### **Timeout Configuration**
```env
# Request Timeouts
REQUEST_TIMEOUT=30           # Overall request timeout
AI_TIMEOUT=20               # AI processing timeout
REDDIT_TIMEOUT=10           # Reddit API timeout
TWITTER_TIMEOUT=10          # Twitter API timeout
JINA_TIMEOUT=10             # Jina AI timeout

# Connection Settings
CONNECTION_POOL_SIZE=20      # HTTP connection pool size
MAX_RETRIES=3               # Max retry attempts
RETRY_DELAY=1               # Delay between retries (seconds)
```

## 🔒 **Security Configuration**

### **Rate Limiting**
```env
# Rate Limiting
ENABLE_RATE_LIMITING=true    # Enable rate limiting
RATE_LIMIT_PER_MINUTE=60     # Requests per minute per client
RATE_LIMIT_BURST=10          # Burst allowance
RATE_LIMIT_STORAGE=memory    # Storage: memory, redis

# Security Monitoring
ENABLE_SECURITY_MONITORING=true
MAX_FAILED_REQUESTS=10       # Max failed requests before blocking
SECURITY_BLOCK_DURATION=300  # Block duration in seconds
```

### **CORS Configuration**
```env
# CORS Settings
CORS_ORIGINS=https://sentientchat.com,https://*.sentientchat.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE
CORS_ALLOW_HEADERS=*
CORS_MAX_AGE=3600
```

### **Input Validation**
```env
# Input Limits
MAX_QUERY_LENGTH=1000        # Maximum query length
MAX_SESSION_ID_LENGTH=100    # Maximum session ID length
ENABLE_XSS_PROTECTION=true   # Enable XSS filtering
ENABLE_SQL_INJECTION_PROTECTION=true
```

## 🧠 **AI Model Configuration**

### **Fireworks AI (Sentient Dobby)**
```env
# Model Parameters
AI_TEMPERATURE=0.7           # Creativity (0.0-1.0)
AI_MAX_TOKENS=1000          # Max response length
AI_TOP_P=0.9                # Nucleus sampling
AI_FREQUENCY_PENALTY=0.0     # Repetition penalty

# Processing Options
AI_ENABLE_STREAMING=true     # Enable streaming responses
AI_PARALLEL_PROCESSING=true  # Process multiple requests in parallel
AI_BATCH_REQUESTS=true       # Batch multiple AI calls
```

### **Jina AI Configuration**
```env
# Embedding Settings
JINA_MODEL=jina-embeddings-v3
JINA_DIMENSIONS=1024         # Embedding dimensions
JINA_BATCH_SIZE=10          # Batch size for embeddings

# Reranking Settings
ENABLE_JINA_RERANKING=true   # Enable content reranking
JINA_RERANK_TOP_K=20        # Top K results to rerank
```

## 📊 **Monitoring Configuration**

### **Logging**
```env
# Log Settings
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=structured       # structured, simple
ENABLE_FILE_LOGGING=true    # Log to files
LOG_FILE_PATH=logs/sentientecho.log
LOG_MAX_SIZE=10MB           # Max log file size
LOG_BACKUP_COUNT=5          # Number of backup files

# Component Logging
LOG_REQUESTS=true           # Log all requests
LOG_AI_CALLS=true          # Log AI API calls
LOG_CACHE_OPERATIONS=false  # Log cache operations (verbose)
```

### **Metrics**
```env
# Metrics Collection
ENABLE_METRICS=true         # Enable metrics collection
METRICS_ENDPOINT=/metrics   # Metrics endpoint path
ENABLE_PROMETHEUS=false     # Prometheus format metrics

# Health Checks
HEALTH_CHECK_INTERVAL=30    # Health check interval (seconds)
ENABLE_COMPONENT_HEALTH=true # Individual component health
```

## 🚀 **Environment-Specific Configurations**

### **Development Environment**
```env
# Development Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_RATE_LIMITING=false
CACHE_TTL_SECONDS=60
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Development Shortcuts
ENABLE_MOCK_PROVIDERS=false # Use mock providers for testing
SKIP_API_VALIDATION=false   # Skip API key validation
```

### **Production Environment**
```env
# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_RATE_LIMITING=true
CACHE_TTL_SECONDS=300
CORS_ORIGINS=https://sentientchat.com

# Production Security
ENABLE_SECURITY_MONITORING=true
ENABLE_REQUEST_LOGGING=true
ENABLE_ERROR_TRACKING=true
```

### **Testing Environment**
```env
# Testing Settings
ENVIRONMENT=testing
LOG_LEVEL=WARNING
ENABLE_CACHING=false        # Disable caching for consistent tests
REQUEST_TIMEOUT=60          # Longer timeouts for tests
ENABLE_RATE_LIMITING=false  # No rate limiting in tests
```

## 🔧 **Advanced Configuration**

### **Custom Provider Settings**
```env
# Reddit Provider
REDDIT_USER_AGENT="SentientEcho/1.0"
REDDIT_MAX_SUBREDDITS=5     # Max subreddits to search
REDDIT_EXCLUDE_NSFW=true    # Exclude NSFW content

# Twitter Provider
TWITTER_LANG=en             # Language filter
TWITTER_RESULT_TYPE=mixed   # mixed, recent, popular
TWITTER_EXCLUDE_RETWEETS=false
```

### **Circuit Breaker Configuration**
```env
# Circuit Breaker Settings
ENABLE_CIRCUIT_BREAKER=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5    # Failures before opening
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=30    # Recovery timeout (seconds)
CIRCUIT_BREAKER_EXPECTED_EXCEPTION=RequestException
```

### **Background Tasks**
```env
# Background Processing
ENABLE_BACKGROUND_TASKS=true
BACKGROUND_TASK_INTERVAL=300    # Task interval (seconds)
ENABLE_CACHE_WARMUP=true        # Warm cache with popular queries
ENABLE_METRICS_COLLECTION=true  # Collect usage metrics
```

## 📝 **Configuration Validation**

### **Validation Script**
```bash
# Validate configuration
python setup.py

# Or manually:
python -c "
from src.config import validate_config
try:
    validate_config()
    print('✅ Configuration is valid!')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"
```

### **Required vs Optional**
**Required** (will fail if missing):
- `FIREWORKS_API_KEY`
- `SERPER_API_KEY`
- `JINA_AI_API_KEY`

**Optional** (have defaults):
- All other settings have sensible defaults

### **Configuration Precedence**
1. **Environment Variables** (highest priority)
2. **`.env` file**
3. **Default values in code** (lowest priority)

## 🎯 **Performance Tuning**

### **For High Traffic**
```env
# Optimize for high traffic
CACHE_TTL_SECONDS=600       # Longer cache
MAX_REDDIT_POSTS=5          # Fewer posts for speed
MAX_TWITTER_POSTS=5
AI_BATCH_SIZE=10           # Larger batches
CONNECTION_POOL_SIZE=50     # More connections
```

### **For Quality Over Speed**
```env
# Optimize for quality
MAX_REDDIT_POSTS=15         # More posts
MAX_TWITTER_POSTS=15
AI_TEMPERATURE=0.3          # More focused AI
ENABLE_JINA_RERANKING=true  # Better ranking
CACHE_TTL_SECONDS=60        # Fresher content
```

### **For Resource Constrained**
```env
# Optimize for low resources
MAX_REDDIT_POSTS=3          # Minimal posts
MAX_TWITTER_POSTS=3
CACHE_MAX_SIZE=100          # Smaller cache
AI_BATCH_SIZE=1            # No batching
CONNECTION_POOL_SIZE=5      # Fewer connections
```

## 🔄 **Configuration Updates**

### **Runtime Configuration Changes**
Some settings can be changed without restart:
- Cache settings (via admin endpoints)
- Rate limits (via admin endpoints)
- Log levels (via admin endpoints)

### **Restart Required**
These settings require restart:
- API keys
- Server host/port
- Core feature toggles

### **Hot Reload**
```bash
# Reload configuration without restart
curl -X POST http://localhost:8000/admin/reload-config

# Or restart specific components
docker-compose restart sentientecho
```

---

**Proper configuration is key to optimal SentientEcho performance. Start with defaults and tune based on your specific needs!** ⚙️
