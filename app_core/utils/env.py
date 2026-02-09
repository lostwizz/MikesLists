#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
env.py
app_core.utils.env
/srv/django/MikesLists_dev/app_core/utils/env.py


Environment helpers for app_core.

Provides:
- AppEnv enum
- get_env(), get_env_enum()
- is_dev(), is_test(), is_live()
- is_local_env(), is_production_env()




# Optional: Custom permission/group decorators


__version__ = "0.0.0.000050-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-09 01:01:45"
"""
###############################################################################
from __future__ import annotations
from enum import Enum
from typing import Optional
from django.conf import settings
from app_core.logging.logging import logger


###############################################################################
###############################################################################
class AppEnv(Enum):
    DEV = "dev"
    TEST = "test"
    LIVE = "live"

    # -----------------------------------------------------------------
    @classmethod
    def from_string(cls, value: Optional[str]) -> "AppEnv":
        """
        Convert a string to an AppEnv enum.
        Unknown values trigger a warning and fall back to DEV.
        """
        if not value:
            logger.warning("ENV_NAME missing; defaulting to DEV")
            return cls.DEV

        value = value.lower().strip()

        try:
            return cls(value)
        except ValueError:
            logger.warning(f"Unknown ENV_NAME '{value}'; defaulting to DEV")
            return cls.DEV

    # -----------------------------------------------------------------
    @classmethod
    def current(cls) -> "AppEnv":
        """
        Return the current environment as an AppEnv enum.
        """
        env_str = getattr(settings, "ENV_NAME", None)
        return cls.from_string(env_str)






# -----------------------------------------------------------------
# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_env_enum() -> AppEnv:
    """Return the current environment as an AppEnv enum."""
    return AppEnv.current()


# -----------------------------------------------------------------
def get_env() -> str:
    """Return the current environment as a lowercase string."""
    return get_env_enum().value


# -----------------------------------------------------------------
def is_dev() -> bool:
    return get_env_enum() is AppEnv.DEV


# -----------------------------------------------------------------
def is_test() -> bool:
    return get_env_enum() is AppEnv.TEST


# -----------------------------------------------------------------
def is_live() -> bool:
    return get_env_enum() is AppEnv.LIVE


# -----------------------------------------------------------------
def is_local_env() -> bool:
    """Return True for dev or test environments."""
    return get_env_enum() in {AppEnv.DEV, AppEnv.TEST}


# -----------------------------------------------------------------
def is_production_env() -> bool:
    """Return True only for live environment."""
    return get_env_enum() is AppEnv.LIVE
