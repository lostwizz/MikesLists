#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health.py
app_core.views.health
/srv/django/MikesLists_dev/app_core/views/health.py



    this file will return a json string which will let you know that:
        - the database connection is good
        - the database is connecting to the correct database (.i.e. MikesLists_dev )
        - checks disk available (storage)



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-02 14:55:32"
###############################################################################

import time
import json
import shutil
from django.http import JsonResponse
from django.conf import settings
from dataclasses import dataclass, asdict
from django.db import connections  # Add this line

from app_core.services.health_service import health_service, CheckResult
from app_core.logging.logging import logger


def health(request):

    # Start the clock
    start_time = time.perf_counter()

    checks, env_name = health_service()

    # # Testing block to check for JSON serialization errors
    # for name, result in checks.items():
    #     try:
    #         # Convert dataclass to dict and attempt to serialize
    #         json.dumps(asdict(result))
    #     except (TypeError, OverflowError) as e:
    #         # This will identify exactly which record is causing the failure
    #         logger.error(f"JSON serialization failed for record '{name}': {e}")
    #         # Optionally print the problematic data to see what isn't serializable
    #         logger.error(f"Problematic data: {asdict(result)}")

    # Determine overall status
    is_healthy = all(c.status == "ok" for c in checks.values())
    # logger.tracet(f"{is_healthy=}")

    # Compute overall status
    overall_status = "ok"
    if any(c.status in ("fail", "hot", "power_issue") for c in checks.values()):
        overall_status = "issues_detected"


    # logger.traces((f"{overall_status=}"))

    # Calculate Latency
    duration_ms = (time.perf_counter() - start_time) * 1000

    response_status = 200 if is_healthy else 503
    # logger.tracea(f"{response_status=}")

    # logger.tracez( request.META)
    return JsonResponse(
        {
            "status": overall_status,
            "latency_ms": round(duration_ms, 2),
            "environment": env_name,
            "host": request.META.get("HTTP_HOST", "unknown"),
            # "details": {name: asdict(result) for name, result in checks.items()},
            "details":  {k: v.to_dict() for k, v in checks.items()},
        },
        status=response_status,
    )
