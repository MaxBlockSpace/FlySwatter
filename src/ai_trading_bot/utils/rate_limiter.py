import asyncio
import time
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class RateLimiter:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.utils.rate_limiter')
        self.limits: Dict[str, Dict[str, Any]] = {}
        self.requests: Dict[str, list] = {}

    def add_limit(self, endpoint: str, max_requests: int, time_window: int) -> None:
        """Add a rate limit for an endpoint.
        
        Args:
            endpoint: API endpoint or identifier
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.limits[endpoint] = {
            'max_requests': max_requests,
            'time_window': time_window
        }
        self.requests[endpoint] = []

    async def acquire(self, endpoint: str) -> None:
        """Acquire permission to make a request."""
        if endpoint not in self.limits:
            return

        limit = self.limits[endpoint]
        current_time = time.time()
        
        # Remove old requests
        self.requests[endpoint] = [
            req_time for req_time in self.requests[endpoint]
            if current_time - req_time <= limit['time_window']
        ]

        # Wait if we've hit the limit
        while len(self.requests[endpoint]) >= limit['max_requests']:
            wait_time = (
                self.requests[endpoint][0] +
                limit['time_window'] -
                current_time
            )
            if wait_time > 0:
                self.logger.warning(
                    f"Rate limit reached for {endpoint}. "
                    f"Waiting {wait_time:.2f} seconds."
                )
                await asyncio.sleep(wait_time)
            
            current_time = time.time()
            self.requests[endpoint] = [
                req_time for req_time in self.requests[endpoint]
                if current_time - req_time <= limit['time_window']
            ]

        # Add current request
        self.requests[endpoint].append(current_time)

    def get_remaining_requests(self, endpoint: str) -> Optional[int]:
        """Get number of remaining requests allowed."""
        if endpoint not in self.limits:
            return None

        current_time = time.time()
        limit = self.limits[endpoint]
        
        # Update request history
        self.requests[endpoint] = [
            req_time for req_time in self.requests[endpoint]
            if current_time - req_time <= limit['time_window']
        ]

        return limit['max_requests'] - len(self.requests[endpoint])

    def reset_limits(self, endpoint: Optional[str] = None) -> None:
        """Reset request history for specified endpoint or all endpoints."""
        if endpoint:
            if endpoint in self.requests:
                self.requests[endpoint] = []
        else:
            for ep in self.requests:
                self.requests[ep] = []