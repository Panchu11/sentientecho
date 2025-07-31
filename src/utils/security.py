"""
Security utilities for input validation and protection.
"""

import re
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib

try:
    from .logger import get_logger
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from logger import get_logger

logger = get_logger(__name__)


class InputValidator:
    """Input validation and sanitization utilities."""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # eval() calls
        r'exec\s*\(',  # exec() calls
        r'import\s+',  # Python imports
        r'__\w+__',  # Python dunder methods
        r'\.\./',  # Path traversal
        r'[;&|`$]',  # Shell injection characters
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'--\s*$',  # SQL comments
        r'/\*.*?\*/',  # SQL block comments
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> tuple[bool, str]:
        """
        Validate user query for security issues.
        
        Args:
            query: User input query
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not isinstance(query, str):
            return False, "Query must be a non-empty string"
        
        # Length check
        if len(query) > 1000:
            return False, "Query too long (max 1000 characters)"
        
        if len(query.strip()) < 3:
            return False, "Query too short (min 3 characters)"
        
        # Check for dangerous patterns
        query_lower = query.lower()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Blocked dangerous pattern in query: {pattern}")
                return False, "Query contains potentially dangerous content"
        
        # Check for SQL injection
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Blocked SQL injection pattern in query: {pattern}")
                return False, "Query contains potentially malicious SQL"
        
        # Check for excessive special characters
        special_char_count = sum(1 for c in query if not c.isalnum() and not c.isspace())
        if special_char_count > len(query) * 0.3:  # More than 30% special chars
            return False, "Query contains too many special characters"
        
        return True, ""
    
    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """
        Sanitize user query by removing/escaping dangerous content.
        
        Args:
            query: Raw user query
            
        Returns:
            Sanitized query
        """
        if not query:
            return ""
        
        # Remove null bytes
        query = query.replace('\x00', '')
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        # Remove HTML tags
        query = re.sub(r'<[^>]+>', '', query)
        
        # Escape special characters that could be problematic
        query = query.replace('\\', '\\\\')
        query = query.replace('"', '\\"')
        query = query.replace("'", "\\'")
        
        # Limit length
        if len(query) > 1000:
            query = query[:1000]
        
        return query.strip()
    
    @classmethod
    def validate_session_id(cls, session_id: str) -> bool:
        """
        Validate session ID format.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if valid, False otherwise
        """
        if not session_id or not isinstance(session_id, str):
            return False
        
        # Check length
        if len(session_id) < 8 or len(session_id) > 128:
            return False
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            return False
        
        return True


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


class SecurityMonitor:
    """Monitor and track security-related events."""
    
    def __init__(self):
        self.blocked_queries = deque(maxlen=1000)  # Keep last 1000 blocked queries
        self.suspicious_ips = defaultdict(list)
        self.rate_limit_violations = defaultdict(int)
    
    def log_blocked_query(self, query: str, reason: str, client_ip: str = None):
        """Log a blocked query for security monitoring."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query[:100],  # Truncate for storage
            "reason": reason,
            "client_ip": client_ip,
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16]
        }
        
        self.blocked_queries.append(event)
        
        if client_ip:
            self.suspicious_ips[client_ip].append(event)
            
            # Clean old entries (keep last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            self.suspicious_ips[client_ip] = [
                e for e in self.suspicious_ips[client_ip]
                if datetime.fromisoformat(e["timestamp"]) > cutoff
            ]
        
        logger.warning(f"Blocked suspicious query from {client_ip}: {reason}")
    
    def log_rate_limit_violation(self, client_ip: str):
        """Log rate limit violation."""
        self.rate_limit_violations[client_ip] += 1
        logger.warning(f"Rate limit violation from {client_ip}")
    
    def is_suspicious_ip(self, client_ip: str) -> bool:
        """Check if IP has suspicious activity."""
        if not client_ip:
            return False
        
        # Check recent blocked queries
        recent_blocks = len(self.suspicious_ips.get(client_ip, []))
        if recent_blocks > 10:  # More than 10 blocked queries in 24h
            return True
        
        # Check rate limit violations
        if self.rate_limit_violations.get(client_ip, 0) > 5:
            return True
        
        return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security monitoring statistics."""
        return {
            "total_blocked_queries": len(self.blocked_queries),
            "suspicious_ips": len(self.suspicious_ips),
            "rate_limit_violations": sum(self.rate_limit_violations.values()),
            "recent_blocks": len([
                q for q in self.blocked_queries
                if datetime.fromisoformat(q["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
            ])
        }


# Global security monitor instance
security_monitor = SecurityMonitor()


def validate_request_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate incoming request data.
    
    Args:
        data: Request data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Request data must be a dictionary"
    
    # Check required fields
    if "query" not in data:
        return False, "Missing 'query' field"
    
    query_data = data["query"]
    if not isinstance(query_data, dict):
        return False, "Query field must be a dictionary"
    
    if "prompt" not in query_data:
        return False, "Missing 'prompt' in query"
    
    # Validate prompt
    prompt = query_data["prompt"]
    is_valid, error = InputValidator.validate_query(prompt)
    if not is_valid:
        return False, f"Invalid prompt: {error}"
    
    # Validate session ID if present
    session_id = data.get("session_id")
    if session_id and not InputValidator.validate_session_id(session_id):
        return False, "Invalid session ID format"
    
    return True, ""


def sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize incoming request data.
    
    Args:
        data: Raw request data
        
    Returns:
        Sanitized request data
    """
    if not isinstance(data, dict):
        return {}
    
    sanitized = {}
    
    # Sanitize session ID
    session_id = data.get("session_id", "default")
    if isinstance(session_id, str):
        sanitized["session_id"] = re.sub(r'[^a-zA-Z0-9_-]', '', session_id)[:128]
    else:
        sanitized["session_id"] = "default"
    
    # Sanitize query
    query_data = data.get("query", {})
    if isinstance(query_data, dict):
        prompt = query_data.get("prompt", "")
        if isinstance(prompt, str):
            sanitized_prompt = InputValidator.sanitize_query(prompt)
            sanitized["query"] = {
                "prompt": sanitized_prompt,
                "context": query_data.get("context", {})
            }
        else:
            sanitized["query"] = {"prompt": "", "context": {}}
    else:
        sanitized["query"] = {"prompt": "", "context": {}}
    
    return sanitized
