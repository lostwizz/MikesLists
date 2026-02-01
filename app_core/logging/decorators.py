#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
decorators.py
app_core.logging.decorators
/srv/django/MikesLists_dev/app_core/logging/decorators.py



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-31 23:44:15"
###############################################################################

import functools
import logging

logger = logging.getLogger("app_core")

# -----------------------------------------------------------------
def log_function_call(func):
    """Decorator to log function arguments and return values."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Format the arguments for logging
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)

        # 2. Log the entry (using your 'DEBUG' or a custom level like 'SUCCESS')
        logger.debug(f"Calling {func.__name__}({signature})")

        try:
            # 3. Execute the function
            result = func(*args, **kwargs)

            # 4. Log the return value
            logger.debug(f"{func.__name__!r} returned {result!r}")
            return result

        except Exception as e:
            # 5. Log exceptions if they occur
            logger.error(f"{func.__name__!r} raised error: {e}")
            raise

    return wrapper
