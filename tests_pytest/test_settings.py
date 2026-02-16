#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_settings.py

Tests for settings configuration to achieve 100% coverage.
"""
###############################################################################

import pytest
import os
from unittest.mock import patch


def test_core_settings_extra_allowed_hosts():
    """
    Test that EXTRA_ALLOWED_HOSTS environment variable adds to ALLOWED_HOSTS.
    Covers settings/core.py line 68
    """
    with patch.dict(os.environ, {'EXTRA_ALLOWED_HOSTS': 'example.com'}):
        # Reload settings to pick up the env var
        from importlib import reload
        import settings.core as core_settings
        reload(core_settings)

        assert 'example.com' in core_settings.ALLOWED_HOSTS


def test_dev_settings_get_local_ip_success():
    """
    Test successful local IP retrieval in dev settings.
    Covers settings/dev.py line 75 (the try block)
    """
    from settings.dev import get_local_ip

    ip = get_local_ip()

    # Should return a valid IP address (not 127.0.0.1 unless it fails)
    assert isinstance(ip, str)
    assert len(ip.split('.')) == 4  # Valid IPv4 format


def test_dev_settings_get_local_ip_exception():
    """
    Test that get_local_ip returns fallback IP on exception.
    Covers settings/dev.py line 76 (the except block)
    """
    import socket
    from unittest.mock import patch
    from settings.dev import get_local_ip

    # Mock socket to raise an exception
    with patch('socket.socket') as mock_socket:
        mock_socket.side_effect = Exception("Network error")

        ip = get_local_ip()

        # Should return fallback IP
        assert ip == "127.0.0.1"
