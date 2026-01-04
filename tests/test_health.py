#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_health.py


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
__version__ = "0.0.1.00002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-02 22:07:22"
###############################################################################
from django.test import TestCase, RequestFactory, SimpleTestCase, TransactionTestCase, override_settings
from django.http import JsonResponse
from unittest.mock import patch, MagicMock
from MikesLists.health import health
import json
from django.conf import settings


class HealthTestCase(TestCase):
    def test_health_success(self):
        """Test health check when everything is OK."""
        factory = RequestFactory()
        request = factory.get('/health/')
        request.META['HTTP_HOST'] = 'example.com'

        with patch('MikesLists.health.connections') as mock_connections, \
             patch('MikesLists.health.settings') as mock_settings, \
             patch('MikesLists.health.shutil.disk_usage') as mock_disk_usage:

            # Mock database connection
            mock_connection = MagicMock()
            mock_connection.settings_dict = {'NAME': 'DEV_db'}
            mock_connections.__getitem__.return_value = mock_connection
            mock_connections['default'] = mock_connection

            # Mock settings
            mock_settings.ENV_NAME = 'DEV'

            # Mock disk usage (200 MB free)
            mock_disk_usage.return_value = (1000000000, 800000000, 200000000)  # total, used, free in bytes

            # Mock cursor
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            response = health(request)

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'ok')
            self.assertEqual(data['details']['database'], 'ok')
            self.assertEqual(data['details']['storage'], 'ok')
            self.assertEqual(data['environment'], 'example.com')

    def test_health_database_wrong_env(self):
        """Test health check when database env doesn't match."""
        factory = RequestFactory()
        request = factory.get('/health/')

        with patch('MikesLists.health.connections') as mock_connections, \
             patch('MikesLists.health.settings') as mock_settings, \
             patch('MikesLists.health.shutil.disk_usage') as mock_disk_usage:

            # Mock database connection
            mock_connection = MagicMock()
            mock_connection.settings_dict = {'NAME': 'wrong_db'}
            mock_connections.__getitem__.return_value = mock_connection
            mock_connections['default'] = mock_connection

            # Mock settings
            mock_settings.ENV_NAME = 'test'

            # Mock disk usage
            mock_disk_usage.return_value = (1000000000, 800000000, 200000000)

            # Mock cursor
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            response = health(request)

            self.assertEqual(response.status_code, 503)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'issues_detected')
            self.assertIn('wrong_env', data['details']['database'])

    def test_health_database_error(self):
        """Test health check when database connection fails."""
        factory = RequestFactory()
        request = factory.get('/health/')

        with patch('MikesLists.health.connections') as mock_connections, \
             patch('MikesLists.health.settings') as mock_settings, \
             patch('MikesLists.health.shutil.disk_usage') as mock_disk_usage:

            # Mock database connection to raise error
            mock_connection = MagicMock()
            mock_connection.settings_dict = {'NAME': 'test_db'}
            mock_connection.cursor.side_effect = Exception('DB error')
            mock_connections.__getitem__.return_value = mock_connection
            mock_connections['default'] = mock_connection

            # Mock settings
            mock_settings.ENV_NAME = 'test'

            # Mock disk usage
            mock_disk_usage.return_value = (1000000000, 800000000, 200000000)

            response = health(request)

            self.assertEqual(response.status_code, 503)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'issues_detected')
            self.assertIn('error', data['details']['database'])

    def test_health_low_disk_space(self):
        """Test health check when disk space is low."""
        factory = RequestFactory()
        request = factory.get('/health/')

        with patch('MikesLists.health.connections') as mock_connections, \
             patch('MikesLists.health.settings') as mock_settings, \
             patch('MikesLists.health.shutil.disk_usage') as mock_disk_usage:

            # Mock database connection
            mock_connection = MagicMock()
            mock_connection.settings_dict = {'NAME': 'test_db'}
            mock_connections.__getitem__.return_value = mock_connection
            mock_connections['default'] = mock_connection

            # Mock settings
            mock_settings.ENV_NAME = 'test'

            # Mock disk usage (50 MB free)
            mock_disk_usage.return_value = (1000000000, 950000000, 50000000)  # 50 MB free

            # Mock cursor
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            response = health(request)

            self.assertEqual(response.status_code, 503)
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'issues_detected')
            self.assertIn('low_space', data['details']['storage'])


class HealthIntegrationTestCase(TransactionTestCase):
    """Integration tests with actual database."""
    databases = {'default'}  # Allow queries to default DB

    @override_settings(DATABASES={'default': {'TEST': {'NAME': 'MikesLists_dev'}}})
    def test_health_with_actual_db(self):
        """Test health check with the actual database 'MikesLists_dev'."""
        response = self.client.get('/health/')
        data = json.loads(response.content)
        print("Actual DB test response:", data)
        # The DB name 'MikesLists_dev' contains 'dev', and ENV_NAME='DEV', so should pass
        self.assertEqual(data['details']['database'], 'ok')