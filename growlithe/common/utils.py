import time
import functools
from growlithe.common.logger import profiler_logger


def profiler_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        profiler_logger.info(f"{func.__name__} took {time.time() - start_time} seconds")
        return result

    return wrapper
