from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
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

    # 1. Check Database
    try:
        db_conn = connections['default']
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = 'ok'
    except OperationalError:
        checks['database'] = 'down'
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