#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health.py

    this file will return a json string which will let you know that:
        - the database connection is good
        - the database is connecting to the correct database (.i.e. MikesLists_dev )
        - checks disk available (storage)





# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK:
# INCOMPLETE:
# SEE NOTES:
# POST
# HACK

"""
__version__ = "0.0.0.00016-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-02 21:42:20"
###############################################################################

from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings

import shutil


def health(request):
    """
    Detailed health check returning a status list for all core components.
    """
    # Initialize the report with individual component checks
    checks = {
        'database': 'unknown',
        'storage': 'unknown',
    }

    from django.conf import settings

    # 1. Check Database
    try:
        # Use connection.settings_dict to get the actual DB name from config
        current_db = connections['default'].settings_dict['NAME']

        # Get the environment name you set in your settings.py
        env_name = getattr(settings, 'ENV_NAME', 'unknown')

        # Verification logic
        if env_name.lower() in current_db.lower():
            checks['database'] = 'ok'
        else:
            checks['database'] = f'wrong_env: found {current_db} but expected {env_name}'

        # Still run a dummy query to ensure the connection is actually ALIVE
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")

    except Exception as e:
        checks['database'] = f'error: {str(e)}'


    # 2. Check Disk Space (Example: Ensure > 100MB free)
    total, used, free = shutil.disk_usage("/")
    free_mb = free // (1024 * 1024)
    checks['storage'] = 'ok' if free_mb > 100 else f'low_space_{free_mb}MB'

    # Determine overall status
    # The script passes if "status": "ok" is found anywhere in the body
    overall_status = 'ok' if all(v == 'ok' for v in checks.values()) else 'issues_detected'

    return JsonResponse({
        'status': overall_status,
        'details': checks,
        'environment': request.META.get('HTTP_HOST', 'unknown')
    }, status=200 if overall_status == 'ok' else 503)