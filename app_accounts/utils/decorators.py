#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
decorators.py
decorators
/srv/django/MikesLists_dev/app_accounts/utils/decorators.py


# Optional: Custom permission/group decorators


"""
__version__ = "0.0.0.000020-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 13:24:24"
###############################################################################

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps

def group_required(group_name):
    """
    Decorator for views that checks if a user is in a specific group.
    Usage: @group_required('Admins')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Check if authenticated
            if not request.user.is_authenticated:
                return redirect('login')

            # 2. Check if user is a superuser (bypass) or in the group
            if request.user.is_superuser or request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)

            # 3. Otherwise, deny access
            raise PermissionDenied
        return _wrapped_view
    return decorator


from django.core.exceptions import PermissionDenied
from functools import wraps

def user_owns_object(model_class, field_name='user'):
    """
    Checks if the logged-in user owns the specific object.
    Usage: @user_owns_object(ToDoList)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, pk, *args, **kwargs):
            obj = model_class.objects.get(pk=pk)
            # Check if object.user == request.user
            if getattr(obj, field_name) != request.user and not request.user.is_superuser:
                raise PermissionDenied
            return view_func(request, pk, *args, **kwargs)
        return _wrapped_view
    return decorator
