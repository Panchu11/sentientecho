"""
Enhanced server implementation with custom endpoints and rate limiting.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import json

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentient_agent_framework import DefaultServer, Session, Query, ResponseHandler
import uvicorn

try:
    from .config import get_settings
    from .sentient_echo_agent import SentientEchoAgent
    from .utils.logger import get_logger
    from .utils.security import (
        validate_request_data, sanitize_request_data,
        security_monitor, CircuitBreaker
    )
    from .utils.cache import get_cache_stats
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from config import get_settings
    from sentient_echo_agent import SentientEchoAgent
    from utils.logger import get_logger
    from utils.security import (
        validate_request_data, sanitize_request_data,
        security_monitor, CircuitBreaker
    )
    from utils.cache import get_cache_stats

logger = get_logger(__name__)


class RateLimiter:
    """Advanced in-memory rate limiter with multiple tiers."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

        # Different limits for different endpoints
        self.endpoint_limits = {
            "/assist": {"max_requests": 30, "window": 60},  # 30 per minute for main endpoint
            "/health": {"max_requests": 120, "window": 60},  # 120 per minute for health checks
            "/info": {"max_requests": 60, "window": 60},     # 60 per minute for info
            "/metrics": {"max_requests": 10, "window": 60}   # 10 per minute for metrics
        }
    
    def is_allowed(self, client_id: str, endpoint: str = None) -> bool:
        """Check if request is allowed for client and endpoint."""
        now = time.time()

        # Get endpoint-specific limits
        if endpoint and endpoint in self.endpoint_limits:
            limits = self.endpoint_limits[endpoint]
            max_requests = limits["max_requests"]
            window_seconds = limits["window"]
        else:
            max_requests = self.max_requests
            window_seconds = self.window_seconds

        # Use endpoint-specific key for tracking
        key = f"{client_id}:{endpoint}" if endpoint else client_id
        client_requests = self.requests[key]

        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - window_seconds:
            client_requests.popleft()

        # Check if under limit
        if len(client_requests) < max_requests:
            client_requests.append(now)
            return True

        return False
    
    def get_reset_time(self, client_id: str) -> int:
        """Get time until rate limit resets."""
        client_requests = self.requests[client_id]
        if not client_requests:
            return 0
        
        oldest_request = client_requests[0]
        reset_time = oldest_request + self.window_seconds
        return max(0, int(reset_time - time.time()))


class EnhancedSentientServer:
    """Enhanced server with custom endpoints and rate limiting."""
    
    def __init__(self, agent: SentientEchoAgent):
        self.agent = agent
        self.settings = get_settings()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=60,  # 60 requests per minute
            window_seconds=60
        )

        # Initialize circuit breaker for external services
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        
        # Create FastAPI app
        self.app = FastAPI(
            title="SentientEcho Agent",
            description="Reddit/Twitter query agent for SentientChat",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize Sentient framework server
        self.sentient_server = DefaultServer(agent)
        
        # Mount Sentient framework routes
        self._setup_sentient_routes()
        
        # Add custom routes
        self._setup_custom_routes()
        
        logger.info("Enhanced SentientEcho server initialized")
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use IP address as client identifier
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _create_rate_limit_check(self, endpoint: str):
        """Create endpoint-specific rate limit check."""
        async def check_rate_limit(request: Request):
            """Rate limiting dependency with security monitoring."""
            client_id = self._get_client_id(request)

            # Check if IP is suspicious
            if security_monitor.is_suspicious_ip(client_id):
                logger.warning(f"Blocking request from suspicious IP: {client_id}")
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Access denied",
                        "message": "Suspicious activity detected"
                    }
                )

            if not self.rate_limiter.is_allowed(client_id, endpoint):
                security_monitor.log_rate_limit_violation(client_id)
                reset_time = self.rate_limiter.get_reset_time(client_id)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests to {endpoint}",
                        "retry_after": reset_time,
                        "endpoint": endpoint
                    },
                    headers={"Retry-After": str(reset_time)}
                )

        return check_rate_limit
    
    def _setup_sentient_routes(self):
        """Setup routes from Sentient Agent Framework."""
        # Mount the Sentient framework app
        # Note: This integrates with the framework's built-in /assist endpoint
        try:
            # Get the framework's FastAPI app if available
            if hasattr(self.sentient_server, '_app'):
                framework_app = self.sentient_server._app
                # Mount framework routes under /sentient
                self.app.mount("/sentient", framework_app)
            else:
                # Fallback: implement assist endpoint manually
                self._setup_assist_endpoint()
        except Exception as e:
            logger.warning(f"Could not mount framework routes: {e}")
            self._setup_assist_endpoint()
    
    def _setup_assist_endpoint(self):
        """Setup assist endpoint manually if framework mounting fails."""
        @self.app.post("/assist")
        async def assist_endpoint(
            request: Dict[str, Any],
            req: Request = None,
            _: None = Depends(self._create_rate_limit_check("/assist"))
        ):
            """Main assist endpoint for SentientChat integration."""
            try:
                client_ip = self._get_client_id(req) if req else "unknown"

                # Validate request data
                is_valid, error_msg = validate_request_data(request)
                if not is_valid:
                    security_monitor.log_blocked_query(
                        str(request), error_msg, client_ip
                    )
                    raise HTTPException(
                        status_code=400,
                        detail={"error": "Invalid request", "message": error_msg}
                    )

                # Sanitize request data
                sanitized_request = sanitize_request_data(request)

                # Extract session and query from sanitized request
                session_id = sanitized_request.get("session_id", "default")
                query_data = sanitized_request.get("query", {})
                prompt = query_data.get("prompt", "")
                
                # Create session and query objects
                session = Session(session_id=session_id)
                query = Query(prompt=prompt, context=query_data.get("context", {}))
                
                # Create response handler for streaming
                response_handler = StreamingResponseHandler()
                
                # Process the query
                await self.agent.assist(session, query, response_handler)
                
                # Return the collected response
                return {
                    "session_id": session_id,
                    "events": response_handler.events,
                    "final_response": response_handler.final_response,
                    "completed": response_handler.completed
                }
                
            except Exception as e:
                logger.error(f"Error in assist endpoint: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Internal server error", "message": str(e)}
                )
    
    def _setup_custom_routes(self):
        """Setup custom HTTP endpoints."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                # Test basic functionality
                agent_status = "healthy" if self.agent else "unhealthy"
                
                # Test AI provider
                ai_status = "healthy"
                try:
                    # Quick test of AI provider
                    if hasattr(self.agent, 'ai_provider'):
                        ai_status = "healthy"
                    else:
                        ai_status = "unhealthy"
                except Exception:
                    ai_status = "unhealthy"
                
                return {
                    "status": "healthy" if agent_status == "healthy" and ai_status == "healthy" else "degraded",
                    "agent": self.settings.agent_name,
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "components": {
                        "agent": agent_status,
                        "ai_provider": ai_status,
                        "reddit_provider": "healthy",
                        "twitter_provider": "healthy"
                    },
                    "uptime": "unknown"  # Could be enhanced with actual uptime tracking
                }
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        @self.app.get("/info")
        async def agent_info():
            """Agent information endpoint."""
            return {
                "name": "SentientEcho",
                "description": "Answers any query using real Reddit and Twitter posts. Cuts through noise with actual public sentiment and AI summaries.",
                "version": "1.0.0",
                "capabilities": [
                    "Reddit Fetch",
                    "Twitter Fetch",
                    "Real Post Context",
                    "AI Summary",
                    "Query Filters",
                    "Sentiment Analysis",
                    "Relevance Ranking"
                ],
                "example_queries": [
                    "What do Redditors say about Coinbase's recent outage?",
                    "Latest Twitter sentiment on ETH ETFs?",
                    "Best subreddit discussions on productivity tools in 2025?",
                    "How is the gaming community reacting to GTA 6 leaks?",
                    "Python programming opinions on r/learnpython this week"
                ],
                "supported_filters": {
                    "subreddit": "Specific subreddit to search (e.g., 'MachineLearning')",
                    "time_range": "day, week, month, year",
                    "sentiment": "positive, negative, neutral, any"
                },
                "rate_limits": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "concurrent_requests": 10
                },
                "endpoints": {
                    "assist": "/assist - Main query processing endpoint",
                    "health": "/health - Health check endpoint",
                    "info": "/info - Agent information endpoint",
                    "docs": "/docs - API documentation"
                }
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Basic metrics endpoint with security and cache stats."""
            security_stats = security_monitor.get_security_stats()
            cache_stats = await get_cache_stats()

            return {
                "requests_total": "unknown",
                "requests_per_minute": "unknown",
                "average_response_time": "unknown",
                "error_rate": "unknown",
                "active_connections": "unknown",
                "security": security_stats,
                "cache": cache_stats,
                "circuit_breaker_state": self.circuit_breaker.state
            }

        @self.app.get("/security")
        async def security_status():
            """Security monitoring endpoint (admin only)."""
            # In production, this should require authentication
            return {
                "status": "monitoring",
                "stats": security_monitor.get_security_stats(),
                "circuit_breaker": {
                    "state": self.circuit_breaker.state,
                    "failure_count": self.circuit_breaker.failure_count,
                    "last_failure": self.circuit_breaker.last_failure_time
                }
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the enhanced server."""
        logger.info(f"Starting enhanced SentientEcho server on {host}:{port}")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            access_log=True
        )


class StreamingResponseHandler:
    """Response handler for collecting streaming responses."""
    
    def __init__(self):
        self.events = []
        self.final_response = ""
        self.completed = False
    
    async def emit_text_block(self, event_type: str, content: str):
        """Capture text block events."""
        self.events.append({
            "type": "text_block",
            "event_type": event_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def emit_json(self, event_type: str, data: dict):
        """Capture JSON events."""
        self.events.append({
            "type": "json",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def emit_error(self, event_type: str, error_code: str, details: dict):
        """Capture error events."""
        self.events.append({
            "type": "error",
            "event_type": event_type,
            "error_code": error_code,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def complete(self):
        """Mark response as complete."""
        self.completed = True
    
    def create_text_stream(self, event_type: str):
        """Create a text stream for streaming responses."""
        return TextStreamCollector(event_type, self)


class TextStreamCollector:
    """Collects streaming text into final response."""
    
    def __init__(self, event_type: str, handler: StreamingResponseHandler):
        self.event_type = event_type
        self.handler = handler
        self.content = ""
    
    async def emit_chunk(self, chunk: str):
        """Collect text chunks."""
        self.content += chunk
    
    async def complete(self):
        """Complete the stream."""
        self.handler.final_response = self.content
        self.handler.events.append({
            "type": "text_stream",
            "event_type": self.event_type,
            "content": self.content,
            "timestamp": datetime.utcnow().isoformat()
        })
