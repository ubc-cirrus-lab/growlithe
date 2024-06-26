import time
from common.logger import profiler_logger

"""
Decorator to profile a function
"""


def profiler_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        profiler_logger.info(f"{func.__name__} took {time.time() - start_time} seconds")

    return wrapper
