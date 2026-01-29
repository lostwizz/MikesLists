#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health.py
app_core.health
/srv/django/MikesLists_dev/app_core/health.py



    this file will return a json string which will let you know that:
        - the database connection is good
        - the database is connecting to the correct database (.i.e. MikesLists_dev )
        - checks disk available (storage)



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:11:02"
###############################################################################

from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings

import shutil

from django.http import JsonResponse
from django.db import connections
from django.conf import settings
import shutil

def health(request):
    """
    Detailed health check returning a status list for all core components.
    """
    checks = {
        'database': 'unknown',
        'storage': 'unknown',
    }

    # 1. Check Database
    try:
        db_conn = connections['default']
        current_db = db_conn.settings_dict.get('NAME', 'unknown')
        env_name = getattr(settings, 'ENV_NAME', 'unknown')

        # Logic check: Does the DB name match our expected environment?
        if env_name.lower() in current_db.lower():
            # Check if connection is actually alive
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks['database'] = 'ok'
        else:
            checks['database'] = f'wrong_env: found {current_db} but expected {env_name}'

    except Exception as e:
        checks['database'] = f'error: {str(e)}'

    # 2. Check Disk Space (Threshold: 100MB)
    # Using getattr for the path allows you to change it in settings.py if needed
    disk_path = getattr(settings, 'HEALTH_CHECK_DISK_PATH', '/')
    try:
        _, _, free = shutil.disk_usage(disk_path)
        free_mb = free // (1024 * 1024)
        checks['storage'] = 'ok' if free_mb > 100 else f'low_space_{free_mb}MB'
    except Exception as e:
        checks['storage'] = f'error: {str(e)}'

    # Determine overall status
    is_healthy = all(v == 'ok' for v in checks.values())
    overall_status = 'ok' if is_healthy else 'issues_detected'

    return JsonResponse({
        'status': overall_status,
        'details': checks,
        'environment': env_name,
        'host': request.META.get('HTTP_HOST', 'unknown')
    }, status=200 if is_healthy else 503)
