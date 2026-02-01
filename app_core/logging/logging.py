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



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-01 00:40:26"
###############################################################################
import logging


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
        for name, (num, color, char) in sorted(all_display_levels.items(), key=lambda x: x[1][0]):
            data = f"{name:<25} | {num:<10} | "
            # Fire the actual log message using the numeric level
            self.log(num, f"Sample {name} output  - " + data)


# -----------------------------------------------------------------
def add_custom_logging_levels(levels_dict):
    for name, (num, color, prefix) in levels_dict.items():
        logging.addLevelName(num, name)

        # We attach the prefix to the method so it's accessible if needed
        def log_method(self, message, *args, level_num=num, **kwargs):
            if self.isEnabledFor(level_num):
                self._log(level_num, message, args, **kwargs)

        setattr(logging.Logger, name.lower(), log_method)



logger = LoggingProxy("app_core")


from app_core.logging.constants import CUSTOM_LOG_LEVELS

# Now call the function here, where it is defined
add_custom_logging_levels(CUSTOM_LOG_LEVELS)

# Instantiate the proxy
logger = LoggingProxy("app_core")
