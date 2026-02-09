#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
auth.py
app_core.utils.auth
/srv/django/MikesLists_dev/app_core/utils/auth.py

Authentication utility helpers for Django user objects.

These helpers wrap Django's built‑in user attributes in a safe,
test‑friendly way that avoids crashes when the object is None,
AnonymousUser, or a mock.



"""
__version__ = "0.1.0.000028-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 21:34:56"
###############################################################################


from typing import Any


# -----------------------------------------------------------------
def is_authenticated(user: Any) -> bool:
    """
    Safely check whether a user is authenticated.

    Django's AnonymousUser has is_authenticated = False,
    but this wrapper avoids attribute errors for non‑User objects.
    """
    return bool(getattr(user, "is_authenticated", False))


# -----------------------------------------------------------------
def is_staff(user: Any) -> bool:
    """
    Safely check whether a user is staff.

    This avoids crashes if the object is None or missing attributes.
    """
    return bool(getattr(user, "is_staff", False))


# -----------------------------------------------------------------
def is_superuser(user: Any) -> bool:
    """
    Safely check whether a user is a superuser.
    """
    return bool(getattr(user, "is_superuser", False))


# -----------------------------------------------------------------
def require_staff(user: Any) -> None:
    """
    Raise PermissionError if the user is not staff.

    Useful for service‑layer checks or view guards.
    """
    if not is_staff(user):
        raise PermissionError("User is not staff")


# -----------------------------------------------------------------
# -----------------------------------------------------------------
