from datetime import datetime, timedelta
from typing import Dict, List

class RequestLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self.requests: Dict[str, List[datetime]] = {}

    def is_rate_limited(self, ip_address: str) -> bool:
        now = datetime.now()

        if ip_address not in self.requests:
            self.requests[ip_address] = [now]
            return False
        
        window_start = now - timedelta(seconds=self.window_seconds)
        self.requests[ip_address] = [
            t for t in self.requests[ip_address] if t > window_start
        ]

        if len(self.requests[ip_address]) >= self.max_requests:
            return True
        
        self.requests[ip_address].append(now)
        return False

login_limiter = RequestLimiter(max_requests=5, window_seconds=60)