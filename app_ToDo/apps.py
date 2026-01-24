#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
apps.py
app_ToDo.apps
/srv/django/MikesLists_dev/app_ToDo/apps.py



"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 22:09:01"
###############################################################################

# /srv/django/MikesLists_dev/app_ToDo/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate
# from app_accounts.views.permissions import CustomPermissions

# ---------------------------------------------------------------------
def run_setup_logic(sender, **kwargs):
    """
    This function runs ONLY after migrations are finished.
    """

    from django.core.management import call_command

    # Import inside the function to avoid 'Apps not ready' errors
    # from .permissions import assign_group_permissions
    # assign_group_permissions()
    try:
        # This calls the 'assign_permissions' command you have in app_accounts
        call_command('assign_permissions')
    except Exception as e:
        print(f"[ERROR] Failed to run permissions setup: {e}")

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
class AppTodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_ToDo'

    # ---------------------------------------------------------------------
    def ready(self):
        # Connect the logic to the post_migrate signal
        # MOVE THE IMPORT HERE
        # from app_accounts.views.permissions import CustomPermissions

        # Now you can use CustomPermissions safely
        # (e.g., connecting a signal or running setup logic)
        print("Django is ready, permissions imported!")
        # post_migrate.connect(run_setup_logic, sender=self)


# ---------------------------------------------------------------------
# login_required_middleware.py
def process_view(self, request, view_func, view_args, view_kwargs):
    view_name = request.resolver_match.view_name
    print(f"[DEBUG] Processing View: {view_name}") # Check your systemd logs for this!

    if view_name in EXEMPT_NAMES:
        return None
