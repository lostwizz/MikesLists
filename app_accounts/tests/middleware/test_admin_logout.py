#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_admin_logout.py
Tests for ForceAdminLogoutMiddleware
"""
###############################################################################

import pytest
from unittest.mock import Mock, patch
from django.test import RequestFactory

from app_accounts.middleware.admin_logout import ForceAdminLogoutMiddleware


@pytest.mark.django_db
def test_middleware_calls_logout_on_accounts_logout_path():
    rf = RequestFactory()
    request = rf.get("/accounts/logout/")

    # Mock the downstream response
    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    # Patch logout so we can assert it was called
    with patch("app_accounts.middleware.admin_logout.logout") as mock_logout:
        middleware = ForceAdminLogoutMiddleware(get_response)
        response = middleware(request)

        # Ensure the response is passed through unchanged
        assert response is mock_response

        # Ensure logout was called
        mock_logout.assert_called_once_with(request)


@pytest.mark.django_db
def test_middleware_does_not_call_logout_for_other_paths():
    rf = RequestFactory()
    request = rf.get("/some/other/path/")

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    with patch("app_accounts.middleware.admin_logout.logout") as mock_logout:
        middleware = ForceAdminLogoutMiddleware(get_response)
        response = middleware(request)

        assert response is mock_response

        # Ensure logout was NOT called
        mock_logout.assert_not_called()
