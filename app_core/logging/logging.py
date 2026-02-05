#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
logging.py
app_core.logging.logging
/srv/django/MikesLists_dev/app_core/logging/logging.py


To dump all the defined (assuming the base set never change):
        import logging
        from app_core.logging.decorators import log_function_call
        from app_core.logging.logging import logger
        logger.dump_all_loggers()

logger.dump_all_loggers()

"""
__version__ = "0.0.0.000036-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-05 14:52:15"
###############################################################################
import logging

from app_core.logging.constants import CUSTOM_LOG_LEVELS

# DEBUG: Print this to your console to see if it's empty
print(f"DEBUG: CUSTOM_LOG_LEVELS contains {len(CUSTOM_LOG_LEVELS)} levels")

# =================================================================
# =================================================================
class LoggingProxy:

    # -----------------------------------------------------------------
    def __init__(self, name):
        self.name = name

    # -----------------------------------------------------------------
    def __getattr__(self, name):
        """
        Catch-all to forward standard logging methods (debug, info, etc.)
        to the actual logger instance.
        """
        return getattr(logging.getLogger(self.name), name)

    # -----------------------------------------------------------------
    def add_runtime_filter(self, filter_instance):
        """
        Dynamically adds a filter to all handlers of the current logger.
        """
        logger = logging.getLogger(self.name)
        for handler in logger.handlers:
            handler.addFilter(filter_instance)
        # Also add to the parent logger to ensure console output is filtered
        logging.getLogger().handlers[0].addFilter(filter_instance)

    # -----------------------------------------------------------------
    def remove_runtime_filter(self, filter_instance):
        """
        Dynamically removes a filter from all handlers.
        """
        logger = logging.getLogger(self.name)
        for handler in logger.handlers:
            handler.removeFilter(filter_instance)

    # -----------------------------------------------------------------
    def dump_all_loggers(self):
        """Outputs a sample of all standard and custom log levels."""
        from app_core.logging.constants import CUSTOM_LOG_LEVELS

        # Standard Python levels
        standard_levels = {
            "DEBUG": (10, "\x1b[36m", ""),
            "INFO": (20, "\x1b[32m", ""),
            "WARNING": (30, "\x1b[33m", ""),
            "ERROR": (40, "\x1b[31m", ""),
            "CRITICAL": (50, "\x1b[1;31m", ""),
        }

        # Merge them (custom levels take precedence if there's a name clash)
        all_display_levels = {**standard_levels, **CUSTOM_LOG_LEVELS}

        print(f"\n{'LEVEL NAME':<25} | {'LEVEL NUM':<10} | {'SAMPLE OUTPUT'}")
        print("-" * 75)

        # Sort by the level number (the first element of the tuple)
        for name, (num, color, char) in sorted(
            all_display_levels.items(), key=lambda x: x[1][0]
        ):
            data = f"{name:<25} | {num:<10} | "
            # Fire the actual log message using the numeric level
            self.log(num, f"Sample {name} output  - " + data)



def add_custom_logging_levels(levels_dict):
    # If the dictionary is empty, the import didn't trigger the add() calls
    if not levels_dict:
        print("CRITICAL: CUSTOM_LOG_LEVELS is empty. Forcing registration...")
        import app_core.logging.constants as const
        # This forces the module-level code in constants.py to run
        levels_dict = const.CUSTOM_LOG_LEVELS

    for name, (num, color, prefix) in levels_dict.items():
        logging.addLevelName(num, name)
        def make_method(level_num):
            def log_method(self, message, *args, **kwargs):
                if self.isEnabledFor(level_num):
                    self._log(level_num, message, args, stacklevel=2, **kwargs)
            return log_method
        setattr(logging.Logger, name.lower(), make_method(num))



def patch_builtin_levels():
    for method_name in ["debug", "info", "warning", "error", "critical"]:
        original = getattr(logging.Logger, method_name)

        def wrapper(self, message, *args, _orig=original, **kwargs):
            return _orig(self, message, *args, stacklevel=2, **kwargs)

        setattr(logging.Logger, method_name, wrapper)



# logger = LoggingProxy("app_core")



# Now call the function here, where it is defined
add_custom_logging_levels(CUSTOM_LOG_LEVELS)

patch_builtin_levels()

# Instantiate the proxy
logger = LoggingProxy("app_core")
