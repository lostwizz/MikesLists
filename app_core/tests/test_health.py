#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_health.py
tests.test_health
/srv/django/MikesLists_dev/tests/test_health.py


# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK
# INCOMPLETE
# SEE NOTES
# POST
# HACK
# FIXME
# BUG
# [ ] something to do
# [x]  i did sometrhing



"""
__version__ = "0.0.1.000003-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-02 16:47:21"
###############################################################################

from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch
from app_core.services.health_service import CheckResult
from django.test import TestCase
from unittest.mock import patch

class HealthTestCase(TestCase):

    @patch("app_core.services.health_service.subprocess.check_output", return_value="0")
    @patch("app_core.services.health_service.subprocess.check_call", return_value=0)
    @patch("app_core.services.health_service.connections")
    @patch("app_core.services.health_service.settings")
    def test_health_success(self, mock_settings, mock_connections, *_):
        mock_settings.ENV_NAME = "MikesLists_dev"
        mock_settings.DATABASES = {"default": {"NAME": "MikesLists_dev"}}

        mock_conn = mock_connections.__getitem__.return_value
        mock_conn.settings_dict = {"NAME": "MikesLists_dev"}
        mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = [1]

        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
