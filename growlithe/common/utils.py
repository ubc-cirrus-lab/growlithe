"""
Utility module for Growlithe.

This module provides utility functions and decorators used across the Growlithe project,
primarily for performance profiling and timing of function executions.
"""

import time
import functools
from growlithe.common.logger import profiler_logger


def profiler_decorator(func):
    """
    Decorator for profiling function execution time.

    This decorator wraps a function and logs its execution time using the profiler_logger.
    It's useful for performance monitoring and optimization.

    Args:
        func (callable): The function to be profiled.

    Returns:
        callable: A wrapped version of the input function that logs its execution time.

    Example:
        @profiler_decorator
        def some_function():
            # Function implementation
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        profiler_logger.info(f"{func.__name__} took {execution_time} seconds")
        return result

    return wrapper
