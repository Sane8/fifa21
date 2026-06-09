from functools import wraps
from time import perf_counter


def track_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        wrapper.last_seconds = perf_counter() - start
        return result

    wrapper.last_seconds = None
    return wrapper
