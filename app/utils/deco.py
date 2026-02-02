from functools import wraps
import traceback
from core.exceptions import *
from app.services.error_handler import run_on_error


def handle_exceptions(func):
    """
    Universal decorator to catch any exception in the wrapped function
    and call run_on_error.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            run_on_error(e)
            raise
    return wrapper

