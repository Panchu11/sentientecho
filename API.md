# SentientEcho API Documentation 📚

## Overview

SentientEcho provides a Sentient Agent API-compliant interface for processing natural language queries and returning real Reddit and Twitter posts with AI-powered analysis.

## Base URL
```
http://localhost:8000  # Development
https://your-domain.com  # Production
```

## Authentication
No authentication required for public endpoints. API keys are managed server-side.

## Endpoints

### 1. Agent Assist (Primary)
**POST** `/assist`

The main endpoint for processing user queries through the Sentient Agent Framework.

#### Request Format
```json
{
  "session_id": "unique-session-id",
  "query": {
    "prompt": "What do people think about Python programming?",
    "context": {}
  }
}
```

#### Response Format (Streaming)
The response streams multiple events:

```json
// Query Analysis Event
{
  "event_type": "QUERY_ANALYSIS",
  "content": "🧠 Analyzing your query..."
}

// Query Intent Event  
{
  "event_type": "QUERY_INTENT",
  "data": {
    "original_query": "What do people think about Python programming?",
    "processed_keywords": ["Python", "programming", "opinions"],
    "search_reddit": true,
    "search_twitter": true,
    "filters": {
      "time_range": "week",
      "sentiment": "any"
    }
  }
}

// Search Event
{
  "event_type": "SEARCH", 
  "content": "🔍 Searching Reddit and Twitter for relevant posts..."
}

// Reddit Results
{
  "event_type": "REDDIT_POSTS",
  "data": {
    "source": "Reddit",
    "count": 5,
    "posts": [
      {
        "id": "abc123",
        "source": "Reddit",
        "content": "I've been learning Python for 6 months...",
        "author": "u/pythonlearner",
        "created_at": "2025-07-24T20:00:00Z",
        "url": "https://reddit.com/r/learnpython/post1",
        "engagement_score": 150,
        "metadata": {
          "score": 120,
          "num_comments": 30,
          "subreddit": "learnpython"
        }
      }
    ]
  }
}

// Twitter Results
{
  "event_type": "TWITTER_POSTS",
  "data": {
    "source": "Twitter",
    "count": 5,
    "posts": [
      {
        "id": "xyz789",
        "source": "Twitter", 
        "content": "Just finished my first Python project!",
        "author": "@coder123",
        "created_at": "2025-07-24T19:30:00Z",
        "url": "https://twitter.com/coder123/status/123",
        "engagement_score": 85,
        "metadata": {
          "likes": 50,
          "retweets": 20,
          "replies": 15
        }
      }
    ]
  }
}

// Final Response (Streaming)
{
  "event_type": "FINAL_RESPONSE",
  "content": "## 📊 Found 10 relevant posts\n\n### 1. Reddit Post\n**Author**: u/pythonlearner\n..."
}

// Completion
{
  "event_type": "COMPLETE"
}
```

### 2. Health Check
**GET** `/health`

Check if the agent is running and healthy.

#### Response
```json
{
  "status": "healthy",
  "agent": "SentientEcho",
  "version": "1.0.0",
  "timestamp": "2025-07-24T21:00:00Z"
}
```

### 3. Agent Information
**GET** `/info`

Get information about the agent capabilities.

#### Response
```json
{
  "name": "SentientEcho",
  "description": "Answers any query using real Reddit and Twitter posts",
  "capabilities": [
    "Reddit Fetch",
    "Twitter Fetch", 
    "Real Post Context",
    "AI Summary",
    "Query Filters"
  ],
  "example_queries": [
    "What do Redditors say about Coinbase's recent outage?",
    "Latest Twitter sentiment on ETH ETFs?",
    "Best subreddit discussions on productivity tools in 2025?"
  ],
  "supported_filters": {
    "subreddit": "Specific subreddit to search",
    "time_range": "day, week, month, year",
    "sentiment": "positive, negative, neutral, any"
  }
}
```

## Query Processing

### Supported Query Types

1. **General Search**
   - "What do people think about [topic]?"
   - "Opinions on [subject]"

2. **Platform-Specific**
   - "Reddit discussions about [topic]"
   - "Twitter sentiment on [subject]"

3. **Filtered Search**
   - "Latest posts on r/MachineLearning about AI"
   - "This week's trending topics in programming"

4. **Sentiment Analysis**
   - "Positive reactions to [event]"
   - "Community sentiment about [topic]"

### Query Filters

Queries can include natural language filters:

- **Subreddit**: "on r/programming", "in the Python subreddit"
- **Time Range**: "this week", "today", "this month", "recent"
- **Sentiment**: "positive opinions", "negative feedback", "neutral discussions"

## Response Processing

### Post Structure
Each post includes:
- **Basic Info**: ID, source, content, author, timestamp, URL
- **Engagement**: Score, likes, comments, retweets
- **AI Enhancement**: Summary, sentiment, relevance score
- **Metadata**: Platform-specific data

### AI Features
- **Query Understanding**: Intent detection and keyword extraction
- **Content Summarization**: AI-generated summaries for each post
- **Sentiment Analysis**: Positive, negative, or neutral classification
- **Relevance Ranking**: Posts ranked by relevance to query

## Error Handling

### Error Response Format
```json
{
  "event_type": "ERROR",
  "error_code": "PROCESSING_ERROR",
  "details": {
    "message": "Failed to process query",
    "timestamp": "2025-07-24T21:00:00Z"
  }
}
```

### Common Error Codes
- `INVALID_QUERY`: Query format is invalid
- `PROCESSING_ERROR`: Internal processing error
- `API_LIMIT_EXCEEDED`: Rate limit exceeded
- `SERVICE_UNAVAILABLE`: External service unavailable

## Rate Limits

- **Queries per minute**: 60
- **Queries per hour**: 1000
- **Concurrent requests**: 10

## Integration Examples

### JavaScript/Node.js
```javascript
const response = await fetch('/assist', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'session-123',
    query: { prompt: 'What do people think about Python?' }
  })
});

// Handle streaming response
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Process streaming events
}
```

### Python
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post('/assist', json={
        'session_id': 'session-123',
        'query': {'prompt': 'What do people think about Python?'}
    })
    
    async for line in response.aiter_lines():
        event = json.loads(line)
        print(f"Event: {event['event_type']}")
```

## Performance Optimization

- **Caching**: Responses cached for 5 minutes
- **Parallel Processing**: Reddit and Twitter searches run concurrently
- **Rate Limiting**: Built-in protection against API abuse
- **Graceful Degradation**: Fallback options if services are unavailable
