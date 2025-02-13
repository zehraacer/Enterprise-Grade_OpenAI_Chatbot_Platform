# utils/rate_limiter.py
import time
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = deque()

    def can_proceed(self) -> bool:
        now = datetime.now()
        
        # Remove old requests
        while self.requests and (now - self.requests[0]) > timedelta(seconds=self.time_window):
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
            
        return False

    def wait_if_needed(self):
        while not self.can_proceed():
            time.sleep(1)