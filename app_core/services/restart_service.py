#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
restart_service.py
restart_service
/srv/django/MikesLists_dev/app_core/tests/services/restart_service.py




"""
__version__ = "0.1.0.000043-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 22:37:27"
###############################################################################

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
restart_service.py
app_core.services.restart_service
"""
__version__ = "0.1.0.000043-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 22:37:27"
###############################################################################

import os
from django.conf import settings

from app_core.utils.shell import run
from app_core.logging.logging import logger


def restart_allowed() -> bool:
    """
    Returns True if restart functionality is enabled in settings.
    """
    return getattr(settings, "STATUS_ALLOW_RESTART", False)


def perform_restart() -> tuple[bool, str]:
    """
    Attempt to run the bounce script and return (success, message).
    """
    script = getattr(settings, "STATUS_RESTART_SCRIPT", "/home/pi/bin/bounce.sh")

    logger.info(f"Restart requested. Script: {script}")

    if not os.path.exists(script):
        msg = "Restart script not found"
        logger.error(msg)
        return False, msg

    if not os.access(script, os.X_OK):
        msg = "Restart script is not executable"
        logger.error(msg)
        return False, msg

    result = run(script)

    if result.returncode == 0:
        msg = "Restart OK"
        logger.info(msg)
        return True, msg

    msg = f"Restart FAILED: {result.stderr.strip()}"
    logger.error(msg)
    return False, msg
