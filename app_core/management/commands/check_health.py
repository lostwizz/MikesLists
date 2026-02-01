#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
check_health.py
check_health
/srv/django/MikesLists_dev/app_core/management/commands/check_health.py

use:
    python3 manage.py check_health




"""
__version__ = "0.0.0.000012-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-01 00:49:33"
###############################################################################


import json
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth.models import User
from app_core.views import health


from app_core.logging.logging import logger

# =================================================================
# =================================================================
class Command(BaseCommand):
    help = 'Runs internal health checks'

    # -----------------------------------------------------------------
    def handle(self, *args, **options):
        # Use a local variable for style to make it cleaner
        # success_style = self.style.SUCCESS
        # error_style = self.style.ERROR
        # warn_style = self.style.WARNING

        self.stdout.write(self.style.HTTP_INFO("--- Initializing System Check ---"))

        factory = RequestFactory()
        request = factory.get('/health/')

        # Simulate auth
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR("Critical Failure: No superuser found to authenticate request."))
            return

        request.user = user

        try:
            response = health(request)
            data = json.loads(response.content)

            # Access 'details' (which is what your health.py returns)
            checks = data.get('details', [])
            latency = data.get('latency_ms', 0.00)
            overall = data.get('status', 'unhealthy').upper()

            logger.tracex( f" just after getting the {checks=}")

            self.stdout.write("Running individual component audits...")
            # logger.traceu( " snow is falling")
            for c in checks:
                # Use dictionary access [key] or .get(key)

                # logger.tracev("before status")
                status = c.get('status', 'unknown').upper()
                # logger.tracew(f" after status {status=}")

                name = c.get('name', 'unknown').upper()
                msg = str(c.get('message', '')).replace("\n", " ").strip()
                raw = str(c.get('raw_value', '')).replace("\n", " ").strip()

                self.stdout.write(f"{name[:20]:<30}", ending="")
                match status:
                    case 'OK':
                        color = self.style.SUCCESS
                    case "WARN":
                        color = self.style.WARNING
                    case "FAIL":
                        color = self.style.ERROR
                    case _:
                        color = self.style.NOTICE

                self.stdout.write(color(f"[{status:<7}] "), ending="")
                self.stdout.write(f"{msg[:25]:<25}", ending="")
                self.stdout.write(f"{raw[:100]:<100}")

            self.stdout.write("-" * 45)
            final_color = self.style.SUCCESS if overall == 'HEALTHY' else self.style.ERROR
            self.stdout.write(final_color(f"FINAL STATUS: {overall}"))
            self.stdout.write(f"VIEW LATENCY: {latency}ms")
            self.stdout.write(f"HOST:         {data.get('host', 'unknown')}")

        except Exception as e:
            # We use a standard print or basic self.stdout here to ensure
            # we see the ACTUAL error if 'self' is the problem
            self.stdout.write(f"\n[!] Execution Error: {str(e)}")
