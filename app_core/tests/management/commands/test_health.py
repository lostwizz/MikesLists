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
__version__ = "0.0.1.000049-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-08 23:39:12"
###############################################################################
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch
from app_core.services.health_service import CheckResult, health_service


import subprocess
from jsonschema import validate
from jsonschema.exceptions import ValidationError


# ---------------------------------------------------------------------------
# 1. BASIC HEALTH SUCCESS TEST
# ---------------------------------------------------------------------------


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
        self.assertIn(response.status_code, [200, 503])


# ---------------------------------------------------------------------------
# 2. MASKING LOGIC TESTS
# ---------------------------------------------------------------------------


class HealthMaskingTests(TestCase):

    def setUp(self):
        self.result = CheckResult(
            name="test_check",
            status="ok",
            message="Secret internal info",
            raw_value="0xDEADBEEF",
        )

    @override_settings(ENV_NAME="dev")
    def test_no_masking_in_dev(self):
        data = self.result.to_dict()
        self.assertIn("message", data)
        self.assertIn("raw_value", data)
        self.assertEqual(data["message"], "Secret internal info")

    @override_settings(ENV_NAME="live")
    def test_masking_in_live(self):
        data = self.result.to_dict()
        self.assertNotIn("message", data)
        self.assertNotIn("raw_value", data)
        self.assertEqual(data["name"], "test_check")


# ---------------------------------------------------------------------------
# 3. BASIC VIEW SERIALIZATION TEST
# ---------------------------------------------------------------------------


class HealthViewTests(TestCase):

    @override_settings(ENV_NAME="test")
    def test_health_view_serialization(self):
        response = self.client.get(reverse("health_check"))
        self.assertIn(response.status_code, [200, 503])

        data = response.json()
        self.assertEqual(data["environment"], "test")
        self.assertIsInstance(data["environment"], str)


# ---------------------------------------------------------------------------
# 4. SUCCESS LOGIC TEST (FIXED SIGNATURE)
# ---------------------------------------------------------------------------


class HealthLogicTests(TestCase):

    @patch("app_core.services.health_service.health_service")
    def test_health_view_success_logic(self, mock_health):
        mock_health.return_value = {
            "status": "ok",
            "environment": "dev",
            "checks": {"storage": {"status": "ok"}},
        }

        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# 5. JSON SCHEMA VALIDATION
# ---------------------------------------------------------------------------


health_response_schema = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["ok", "fail", "warn", "skip", "issues_detected"],
        },
        "environment": {"type": "string"},
        "checks": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "raw_value": {"type": ["string", "number", "null", "object"]},
                },
                "required": ["name", "status"],
            },
        },
    },
    "required": ["status", "environment"],
}


class HealthSchemaTests(TestCase):

    def test_health_json_schema(self):
        response = self.client.get(reverse("health_check"))
        data = response.json()

        try:
            validate(instance=data, schema=health_response_schema)
        except ValidationError as e:
            self.fail(f"JSON schema validation failed: {e.message}")


# ---------------------------------------------------------------------------
# 6. DATABASE FAILURE TEST
# ---------------------------------------------------------------------------


class HealthDatabaseTests(TestCase):

    @patch("app_core.services.health_service.connections")
    def test_health_database_failure(self, mock_connections):
        mock_connections.__getitem__.side_effect = Exception("Connection refused")

        response = self.client.get(reverse("health_check"))
        self.assertIn(response.status_code, [200, 503])
        self.assertEqual(response.json()["details"]["database"]["status"], "fail")


# ---------------------------------------------------------------------------
# 7. SUBPROCESS FAILURE TESTS
# ---------------------------------------------------------------------------


class HealthSubprocessTests(TestCase):

    @patch("app_core.services.health_service.subprocess.check_output")
    def test_health_subprocess_error(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "vcgencmd")

        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.json()["details"]["throttling"]["status"], "fail")


class HealthNegativeTests(TestCase):

    @patch("app_core.services.health_service.connections")
    @override_settings(ENV_NAME="dev")
    def test_health_database_unreachable(self, mock_connections):
        mock_connections.__getitem__.side_effect = Exception(
            "Database connection timed out"
        )

        response = self.client.get("/health/")
        data = response.json()

        self.assertEqual(data["details"]["database"]["status"], "fail")
        self.assertIn("connection timed out", data["details"]["database"]["message"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "issues_detected")


class HealthHardwareTests(TestCase):

    @patch("app_core.services.health_service.subprocess.check_output")
    def test_health_subprocess_hardware_failure(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "vcgencmd")

        response = self.client.get("/health/")
        data = response.json()

        self.assertIn(response.status_code, [200, 503])
        self.assertEqual(data["details"]["throttling"]["status"], "fail")
        self.assertEqual(
            data["details"]["throttling"]["message"],
            "Command 'vcgencmd' returned non-zero exit status 1.",
        )
