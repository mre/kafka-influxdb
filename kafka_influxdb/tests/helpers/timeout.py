from functools import wraps
from multiprocessing import Process

#class TimeoutError(Exception):
#    pass

def timeout(seconds=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            process = Process(None, func, None, args, kwargs)
            process.start()
            process.join(seconds)
            if process.is_alive():
                process.terminate()
        return wraps(func)(wrapper)
    return decorator
