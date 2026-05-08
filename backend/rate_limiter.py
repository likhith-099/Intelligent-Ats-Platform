"""
Simple in-memory rate limiter for FastAPI.
For production, use Redis or a dedicated rate limiting library.
"""
import time
from collections import defaultdict
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Tuple
import asyncio

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit."""
        async with self.lock:
            current_time = time.time()
            # Clean old requests (older than 1 minute)
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
            
            # Check if limit exceeded
            if len(self.requests[client_ip]) >= self.requests_per_minute:
                return True
            
            # Add current request
            self.requests[client_ip].append(current_time)
            return False

# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)  # 60 requests per minute

async def rate_limit_middleware(request: Request, call_next):
    """Middleware to apply rate limiting to all requests."""
    # Skip rate limiting for health check
    if request.url.path == "/":
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    if await rate_limiter.is_rate_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please try again later.",
                "retry_after": 60
            },
            headers={"Retry-After": "60"}
        )
    
    return await call_next(request)