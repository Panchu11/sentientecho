# SentientEcho Architecture Documentation 🏗️

## 📋 **Overview**

SentientEcho is a production-ready Reddit/Twitter query agent built with the Sentient Agent Framework. It provides real-time content retrieval, AI-powered analysis, and intelligent response generation for SentientChat integration.

## 🎯 **Core Architecture**

### **High-Level Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SentientChat  │───▶│  SentientEcho   │───▶│  External APIs  │
│                 │    │     Agent       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Response with  │
                    │  Real Content   │
                    └─────────────────┘
```

### **Detailed Component Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                        SentientEcho Agent                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   FastAPI       │  │   Sentient      │  │   Security      │ │
│  │   Server        │  │   Framework     │  │   Layer         │ │
│  │                 │  │   Integration   │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Query         │  │   Post          │  │   Cache         │ │
│  │   Processor     │  │   Processor     │  │   Manager       │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   AI Provider   │  │  Reddit Provider│  │ Twitter Provider│ │
│  │  (Dobby 70B)    │  │  (JSON API)     │  │  (Serper API)   │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Jina AI       │  │   Rate Limiter  │  │   Circuit       │ │
│  │   Provider      │  │                 │  │   Breaker       │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 **Request Processing Flow**

### **1. Request Reception**
```
User Query → SentientChat → POST /assist → SentientEcho
```

### **2. Processing Pipeline**
```
┌─────────────────┐
│  1. Security    │ ── Rate Limiting, Input Validation
│     Check       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  2. Cache       │ ── Check for cached results
│     Lookup      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  3. Query       │ ── AI-powered intent recognition
│     Analysis    │    Keyword extraction
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  4. Parallel    │ ── Reddit JSON API
│     Search      │    Twitter Serper API
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  5. Content     │ ── AI summarization
│     Enhancement │    Sentiment analysis
│                 │    Relevance ranking
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  6. Response    │ ── Real-time streaming
│     Generation  │    Event emission
└─────────────────┘
```

## 🧩 **Component Details**

### **Core Components**

#### **1. SentientEchoAgent**
- **Purpose**: Main agent class implementing AbstractAgent
- **Responsibilities**: 
  - Query orchestration
  - Provider coordination
  - Response streaming
- **Framework Compliance**: Full Sentient Agent Framework integration

#### **2. Query Processor**
- **Purpose**: AI-powered query understanding
- **Capabilities**:
  - Intent recognition
  - Keyword extraction
  - Platform selection (Reddit/Twitter)
  - Filter application
- **AI Model**: Sentient Dobby Llama 3 70B

#### **3. Post Processor**
- **Purpose**: Content enhancement and ranking
- **Features**:
  - AI summarization
  - Sentiment analysis
  - Relevance scoring
  - Content filtering
- **AI Integration**: Dobby + Jina AI

### **Provider Layer**

#### **1. AI Provider (Sentient Dobby)**
- **Model**: Sentient Dobby Llama 3 Unhinged 70B
- **API**: Fireworks AI
- **Capabilities**:
  - Query processing
  - Content summarization
  - Sentiment analysis
  - Relevance ranking

#### **2. Reddit Provider**
- **API**: Reddit JSON API (public)
- **Features**:
  - Real-time post retrieval
  - Subreddit filtering
  - Time range filtering
  - Engagement scoring

#### **3. Twitter Provider**
- **Primary API**: Serper.dev
- **Fallback**: snscrape
- **Features**:
  - Real-time tweet retrieval
  - Engagement analysis
  - Content filtering

#### **4. Jina AI Provider**
- **Purpose**: Semantic analysis
- **Features**:
  - Embedding generation
  - Similarity calculation
  - Keyword extraction
  - Content ranking

### **Infrastructure Layer**

#### **1. Custom FastAPI Server**
- **Enhanced Features**:
  - All documented endpoints
  - Real-time SSE streaming
  - CORS configuration
  - Health monitoring
- **Advantages over DefaultServer**:
  - Full control
  - Custom endpoints
  - Enhanced security

#### **2. Security Framework**
- **Input Validation**: XSS, SQL injection protection
- **Rate Limiting**: Per-client, per-endpoint
- **Circuit Breakers**: External service protection
- **Security Monitoring**: Suspicious activity tracking

#### **3. Caching System**
- **Query Cache**: LRU with TTL
- **Performance**: 80% cache hit rate potential
- **Background Cleanup**: Automatic expired entry removal
- **Statistics**: Real-time cache metrics

## 📊 **Data Flow Architecture**

### **Input Processing**
```
Natural Language Query
         │
         ▼
┌─────────────────┐
│   Input         │ ── Validation, Sanitization
│   Validation    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   AI Query      │ ── Intent: {keywords, platforms, filters}
│   Processing    │
└─────────────────┘
```

### **Content Retrieval**
```
┌─────────────────┐    ┌─────────────────┐
│   Reddit API    │    │   Twitter API   │
│   Search        │    │   Search        │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │   Raw Posts     │
            │   Collection    │
            └─────────────────┘
```

### **AI Enhancement Pipeline**
```
Raw Posts → AI Summarization → Sentiment Analysis → Relevance Ranking → Enhanced Posts
```

### **Response Generation**
```
Enhanced Posts → Response Formatting → Real-time Streaming → SentientChat
```

## 🔧 **Technology Stack**

### **Core Technologies**
- **Language**: Python 3.8+
- **Framework**: Sentient Agent Framework
- **Web Server**: FastAPI + Uvicorn
- **Async**: asyncio, aiohttp

### **AI & ML**
- **Primary LLM**: Sentient Dobby Llama 3 70B (Fireworks)
- **Embeddings**: Jina AI v3
- **Processing**: Custom AI pipeline

### **APIs & Services**
- **Reddit**: JSON API (public)
- **Twitter**: Serper.dev + snscrape fallback
- **Search**: Serper.dev
- **AI**: Fireworks AI, Jina AI

### **Infrastructure**
- **Caching**: In-memory LRU with TTL
- **Security**: Custom validation framework
- **Monitoring**: Health checks, metrics
- **Deployment**: Docker + docker-compose

## 🚀 **Performance Characteristics**

### **Response Times**
- **Cold Start**: 15-20 seconds
- **Warm Cache**: 2-3 seconds
- **AI Processing**: 10-15 seconds
- **Content Retrieval**: 2-3 seconds

### **Throughput**
- **Concurrent Users**: 10-50 (rate limited)
- **Requests/Minute**: 60 (configurable)
- **Cache Hit Rate**: 70-80% potential

### **Resource Usage**
- **Memory**: ~200MB baseline
- **CPU**: Moderate (async I/O bound)
- **Network**: High (external API calls)

## 🔒 **Security Architecture**

### **Input Security**
- **Validation**: Comprehensive input sanitization
- **XSS Protection**: HTML/script tag filtering
- **SQL Injection**: Parameter sanitization
- **Size Limits**: Request payload limits

### **Access Control**
- **Rate Limiting**: Per-client tracking
- **CORS**: Restricted origins
- **IP Monitoring**: Suspicious activity detection

### **External Service Security**
- **Circuit Breakers**: Failure protection
- **Timeout Management**: Request timeouts
- **Error Handling**: Graceful degradation

## 📈 **Scalability Considerations**

### **Horizontal Scaling**
- **Stateless Design**: No server-side state
- **Load Balancing**: Multiple instance support
- **Database**: No database dependency

### **Vertical Scaling**
- **Memory**: Configurable cache sizes
- **CPU**: Async processing optimization
- **Network**: Connection pooling

### **Optimization Opportunities**
- **Caching**: Enhanced cache strategies
- **Batching**: AI request batching
- **CDN**: Static content delivery
- **Database**: Optional persistent caching

## 🔄 **Integration Points**

### **SentientChat Integration**
- **Protocol**: HTTP + SSE
- **Events**: JSON, Text, Streams
- **Framework**: Full Sentient Agent compliance

### **External APIs**
- **Reddit**: Public JSON API
- **Twitter**: Serper.dev API
- **AI**: Fireworks AI API
- **Embeddings**: Jina AI API

### **Monitoring Integration**
- **Health**: `/health` endpoint
- **Metrics**: `/metrics` endpoint
- **Logs**: Structured logging
- **Alerts**: Error tracking

## 🔮 **Future Enhancements**

### **Planned Improvements**
- **Database Integration**: Persistent caching and analytics
- **Advanced AI**: Multi-model ensemble
- **Real-time Updates**: WebSocket support
- **Analytics**: User behavior tracking
- **Multi-language**: International support

### **Extensibility**
- **Plugin Architecture**: Custom provider plugins
- **API Extensions**: Additional endpoints
- **Custom Models**: Alternative AI models
- **Data Sources**: Additional content sources

---

*This architecture supports production deployment with high availability, security, and performance for SentientChat integration.*
