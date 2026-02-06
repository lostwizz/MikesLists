#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
env.py
app_core.utils.env
/srv/django/MikesLists_dev/app_core/utils/env.py




# Optional: Custom permission/group decorators


"""
__version__ = "0.0.0.000036-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-05 23:07:19"
###############################################################################



from enum import Enum
from django.conf import settings

class AppEnv(Enum):
    DEV = "dev"
    TEST = "test"
    LIVE = "live"

    @classmethod
    def current(cls):
        """Helper to get the current environment object from settings."""
        from django.conf import settings
        # Default to DEV if not set
        env_str = getattr(settings, "ENV_NAME", "dev").lower()
        try:
            return cls(env_str)
        except ValueError:
            return cls.DEV



def get_env() -> str:
    """Returns the current environment as a string (e.g., 'dev', 'test', 'live')."""
    return AppEnv.current().value  # Access .value to get the string from the Enum

# def get_env() -> AppEnv:
#     """Returns the current environment as an Enum member."""
#     return AppEnv.current()

# def is_dev() -> bool:
#     return get_env() == AppEnv.DEV

# def is_live() -> bool:
#     return get_env() == AppEnv.LIVE

# def is_test() -> bool:
#     return get_env() == AppEnv.TEST

def is_dev() -> bool:
    # Compare string to string (e.g., "dev" == "dev")
    return get_env() == AppEnv.DEV.value

def is_live() -> bool:
    return get_env() == AppEnv.LIVE.value

def is_test() -> bool:
    return get_env() == AppEnv.TEST.value
