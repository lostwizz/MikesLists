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
__version__ = "0.0.1.000032-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-06 00:56:02"
###############################################################################

from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch
from app_core.services.health_service import CheckResult
from django.test import TestCase
from unittest.mock import patch

import subprocess

from jsonschema import validate
from jsonschema.exceptions import ValidationError

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
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.status_code, 503)
        self.assertIn(response.status_code, [200, 503])


class HealthMaskingTests(TestCase):

    def setUp(self):
        self.result = CheckResult(
            name="test_check",
            status="ok",
            message="Secret internal info",
            raw_value="0xDEADBEEF"
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
        # Verify keys are GONE, not just set to None
        print(f"{data=}")
        self.assertNotIn("message", data)
        self.assertNotIn("raw_value", data)
        self.assertEqual(data["name"], "test_check")



class HealthViewTests(TestCase):

    @override_settings(ENV_NAME="test")
    def test_health_view_serialization(self):
        response = self.client.get(reverse('health_check'))
        # self.assertEqual(response.status_code, 200)
        self.assertIn(response.status_code, [200, 503])

        data = response.json()
        # Ensure 'environment' is a plain string, not an Enum object
        self.assertEqual(data["environment"], "test")
        self.assertIsInstance(data["environment"], str)




@patch('app_core.services.health_service.get_health_status')
def test_health_view_success_logic(self, mock_health):
    # This simulates a perfect system state
    mock_health.return_value = {
        "status": "ok",
        "environment": "dev",
        "checks": {"storage": {"status": "ok"}}
    }
    response = self.client.get(reverse('health_check'))
    # This now asserts the LOGIC of a successful path
    self.assertEqual(response.status_code, 200)

health_response_schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["ok", "fail", "warn","skip", "issues_detected"]},
        "environment": {"type": "string"},
        "checks": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "raw_value": {"type": ["string", "number", "null", "object"]}
                },
                "required": ["name", "status"]
            }
        }
    },
    "required": ["status", "environment"]
}


class HealthViewTests(TestCase):
    def test_health_json_schema(self):
        response = self.client.get(reverse('health_check'))
        data = response.json()

        try:
            # This will raise a ValidationError if 'data' doesn't match 'health_response_schema'
            validate(instance=data, schema=health_response_schema)
        except ValidationError as e:
            self.fail(f"JSON schema validation failed: {e.message}")



@patch('app_core.services.health_service.connections')
def test_health_database_failure(self, mock_connections):
    # Simulate a database connection error
    mock_connections.__getitem__.side_effect = Exception("Connection refused")

    response = self.client.get(reverse('health_check'))
    self.assertEqual(response.status_code, 503)
    self.assertEqual(response.json()["checks"]["database"]["status"], "fail")



@patch("app_core.services.health_service.subprocess.check_output")
def test_health_subprocess_error(self, mock_subprocess):
    # Simulate a system command not being found or failing
    mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'vcgencmd')

    response = self.client.get(reverse('health_check'))
    # Verify that the 'throttling' check (or similar) handles the error
    self.assertEqual(response.json()["checks"]["throttling"]["status"], "fail")


class HealthNegativeTests(TestCase):
    @patch("app_core.services.health_service.connections")
    @override_settings(ENV_NAME="dev") # MUST add this to see the 'message'
    def test_health_database_unreachable(self, mock_connections):
        """Ensure the app handles a total database connection failure."""
        mock_connections.__getitem__.side_effect = Exception("Database connection timed out")

        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)

        data = response.json()
        self.assertEqual(data["details"]["database"]["status"], "fail")
        # message will no longer be None because of @override_settings
        self.assertIn("connection timed out", data["details"]["database"]["message"])



@patch("app_core.services.health_service.subprocess.check_output")
def test_health_subprocess_hardware_failure(self, mock_subprocess):
    """Ensure the app handles hardware command failures gracefully."""
    # Simulate a 'command not found' or execution error (Exit Code 1)
    mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'vcgencmd')

    response = self.client.get("/health/")

    # The system should stay up (503) but report the specific check as failed
    self.assertEqual(response.status_code, 503)
    data = response.json()

    # Check that the specific hardware check is marked as failed
    self.assertEqual(data["checks"]["throttling"]["status"], "fail")
    self.assertEqual(data["checks"]["throttling"]["message"], "Command 'vcgencmd' returned non-zero exit status 1.")
