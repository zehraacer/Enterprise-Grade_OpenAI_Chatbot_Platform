# utils/performance_logger.py
import time
import logging
from functools import wraps
from typing import Callable, Any
import psutil
import numpy as np

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger('performance')
        self.measurements = []

    def measure_time(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            result = func(*args, **kwargs)

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            execution_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            self.measurements.append({
                'function': func.__name__,
                'execution_time': execution_time,
                'memory_used': memory_used
            })
            
            self.logger.info(
                f"Function: {func.__name__} | "
                f"Time: {execution_time:.2f}s | "
                f"Memory: {memory_used:.2f}MB"
            )
            
            return result
        return wrapper

    def get_statistics(self):
        if not self.measurements:
            return {}
            
        times = [m['execution_time'] for m in self.measurements]
        memory = [m['memory_used'] for m in self.measurements]
        
        return {
            'avg_time': np.mean(times),
            'max_time': np.max(times),
            'avg_memory': np.mean(memory),
            'max_memory': np.max(memory)
        }