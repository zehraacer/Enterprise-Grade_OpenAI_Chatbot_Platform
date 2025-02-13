# utils/decorators.py
from functools import wraps
from utils.rate_limiter import RateLimiter

def rate_limit(max_requests: int = 60, time_window: int = 60):
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator