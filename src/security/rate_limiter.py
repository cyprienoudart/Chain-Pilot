"""
Rate Limiting - Phase 6
Protect API from abuse and DoS attacks
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter
    - Prevents API abuse
    - Configurable limits per endpoint
    - Per-IP tracking
    """
    
    def __init__(self):
        # Storage: {ip: {endpoint: (tokens, last_update)}}
        self.buckets: Dict[str, Dict[str, Tuple[float, float]]] = defaultdict(dict)
        
        # Rate limits: requests per minute
        self.limits = {
            "default": 60,           # 60 req/min for most endpoints
            "/api/v1/transaction/send": 10,  # 10 req/min for transactions
            "/api/v1/wallet/create": 5,      # 5 req/min for wallet creation
            "/api/v1/rules/create": 10,      # 10 req/min for rule creation
            "/api/v1/ai/parse": 30,          # 30 req/min for AI parsing
        }
        
        logger.info("Rate limiter initialized")
    
    def is_allowed(self, ip: str, endpoint: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed
        
        Returns:
            Tuple of (allowed: bool, info: dict)
        """
        # Get rate limit for this endpoint
        limit = self.limits.get(endpoint, self.limits["default"])
        
        # Get or create bucket
        if endpoint not in self.buckets[ip]:
            self.buckets[ip][endpoint] = (limit, time.time())
        
        tokens, last_update = self.buckets[ip][endpoint]
        now = time.time()
        
        # Refill tokens based on time passed
        time_passed = now - last_update
        tokens = min(limit, tokens + (time_passed * limit / 60.0))  # Refill rate: limit per minute
        
        # Check if we have tokens
        if tokens >= 1.0:
            # Consume one token
            tokens -= 1.0
            self.buckets[ip][endpoint] = (tokens, now)
            
            return True, {
                "allowed": True,
                "remaining": int(tokens),
                "limit": limit,
                "reset_in": int((limit - tokens) * 60 / limit)
            }
        else:
            # No tokens available
            return False, {
                "allowed": False,
                "remaining": 0,
                "limit": limit,
                "reset_in": int((1.0 - tokens) * 60 / limit),
                "retry_after": int((1.0 - tokens) * 60 / limit)
            }
    
    def reset_ip(self, ip: str):
        """Reset rate limits for an IP"""
        if ip in self.buckets:
            del self.buckets[ip]
            logger.info(f"Reset rate limits for IP: {ip}")
    
    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics"""
        return {
            "tracked_ips": len(self.buckets),
            "limits": self.limits,
            "total_buckets": sum(len(endpoints) for endpoints in self.buckets.values())
        }


# Global rate limiter instance
rate_limiter = RateLimiter()

