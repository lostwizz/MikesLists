#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_login_required_middleware.py

Comprehensive test suite for Django middleware components:
- LoginRequiredMiddleware: Enforces authentication requirements
- UpdateLastActivityMiddleware: Tracks user activity timestamps
- ActiveUserMiddleware: Updates last_seen timestamp on each request

These middleware classes work together to secure the application and
track user engagement.
"""
__version__ = "0.0.0.000037-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-13 23:18:13"
###############################################################################
import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from unittest.mock import Mock, patch

from app_accounts.middleware.login_required_middleware import (
    LoginRequiredMiddleware,
    UpdateLastActivityMiddleware,
    ActiveUserMiddleware,
)


###############################################################################
# UpdateLastActivityMiddleware Tests
###############################################################################


@pytest.mark.django_db
def test_update_last_activity_updates_timestamp_for_authenticated_user():
    """
    Verify that UpdateLastActivityMiddleware updates the profile's last_seen
    timestamp when an authenticated user makes a request.
    """
    rf = RequestFactory()
    user = User.objects.create_user(username="mike", password="x")
    profile = user.profile

    request = rf.get("/some/path/")
    request.user = user

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = UpdateLastActivityMiddleware(get_response)
    middleware(request)

    # Verify the timestamp was updated
    profile.refresh_from_db()
    assert profile.last_seen is not None

    # Verify the response is passed through correctly
    assert middleware(request) is mock_response


@pytest.mark.django_db
def test_update_last_activity_skips_for_anonymous_user():
    """
    Verify that UpdateLastActivityMiddleware does not attempt to update
    the profile for anonymous (unauthenticated) users.
    """
    rf = RequestFactory()
    request = rf.get("/some/path/")
    request.user = AnonymousUser()

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = UpdateLastActivityMiddleware(get_response)

    # Mock the Profile query to verify it's never called for anonymous users
    with patch("app_accounts.middleware.login_required_middleware.Profile.objects.filter") as mock_filter:
        response = middleware(request)
        mock_filter.assert_not_called()
        assert response is mock_response


###############################################################################
# ActiveUserMiddleware Tests
###############################################################################


@pytest.mark.django_db
def test_active_user_middleware_updates_last_seen():
    """
    Verify that ActiveUserMiddleware updates last_seen for authenticated users.
    This middleware is functionally similar to UpdateLastActivityMiddleware.
    """
    rf = RequestFactory()
    user = User.objects.create_user(username="activetest", password="x")

    request = rf.get("/some/path/")
    request.user = user

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = ActiveUserMiddleware(get_response)
    response = middleware(request)

    # Verify timestamp was updated
    user.profile.refresh_from_db()
    assert user.profile.last_seen is not None
    assert response is mock_response


@pytest.mark.django_db
def test_active_user_middleware_skips_anonymous():
    """
    Verify that ActiveUserMiddleware gracefully handles anonymous users
    without attempting database updates.
    """
    rf = RequestFactory()
    request = rf.get("/some/path/")
    request.user = AnonymousUser()

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = ActiveUserMiddleware(get_response)
    response = middleware(request)

    assert response is mock_response


###############################################################################
# LoginRequiredMiddleware - process_view() Tests
###############################################################################


@pytest.mark.django_db
def test_process_view_skips_accounts_paths():
    """
    Verify that all /accounts/* URLs are exempt from login requirements.
    This allows users to access login, logout, registration, and password
    reset pages without being authenticated.
    """
    rf = RequestFactory()
    request = rf.get("/accounts/something/")
    request.user = AnonymousUser()
    request.resolver_match = None

    middleware = LoginRequiredMiddleware(lambda r: None)
    assert middleware.process_view(request, None, None, None) is None


@pytest.mark.django_db
def test_process_view_exempt_path_prefixes():
    """
    Verify that static files, admin URLs, and other exempt path prefixes
    are accessible without authentication.
    """
    rf = RequestFactory()
    request = rf.get("/static/somefile.css")
    request.user = AnonymousUser()

    middleware = LoginRequiredMiddleware(lambda r: None)
    assert middleware.process_view(request, None, None, None) is None


@pytest.mark.django_db
def test_process_view_exempt_named_url():
    """
    Verify that named URLs in the EXEMPT_NAMES set (like 'accounts:login')
    are accessible without authentication.
    """
    rf = RequestFactory()
    request = rf.get("/whatever/")
    request.user = AnonymousUser()

    class DummyResolver:
        view_name = "accounts:login"

    request.resolver_match = DummyResolver()

    middleware = LoginRequiredMiddleware(lambda r: None)
    assert middleware.process_view(request, None, None, None) is None


@pytest.mark.django_db
def test_process_view_redirects_unauthenticated_non_exempt_view():
    """
    Verify that unauthenticated users are redirected to the login page
    when attempting to access non-exempt views.
    """
    rf = RequestFactory()
    request = rf.get("/protected/page/")
    request.user = AnonymousUser()

    class DummyResolver:
        view_name = "some_non_exempt_view"

    request.resolver_match = DummyResolver()

    middleware = LoginRequiredMiddleware(lambda r: None)
    result = middleware.process_view(request, None, None, None)

    # Should redirect to login
    assert result.status_code == 302
    assert reverse("accounts:login") in result.url


@pytest.mark.django_db
def test_process_view_allows_authenticated_user_when_no_resolver_match():
    """
    Verify that authenticated users can access pages even when there's
    no resolver_match (edge case handling).
    """
    rf = RequestFactory()
    request = rf.get("/protected/")
    request.user = User.objects.create_user(username="mike", password="x")
    request.resolver_match = None

    middleware = LoginRequiredMiddleware(lambda r: None)
    assert middleware.process_view(request, None, None, None) is None


@pytest.mark.django_db
def test_process_view_authenticated_non_exempt():
    """
    Verify that authenticated users can access non-exempt views without
    being redirected.
    """
    rf = RequestFactory()
    request = rf.get("/protected/page/")
    request.user = User.objects.create_user(username="auth2", password="x")

    class DummyResolver:
        view_name = "non_exempt_view"

    request.resolver_match = DummyResolver()

    middleware = LoginRequiredMiddleware(lambda r: None)
    result = middleware.process_view(request, None, None, None)

    # Should return None, allowing the view to process normally
    assert result is None


###############################################################################
# LoginRequiredMiddleware - __call__() Tests
###############################################################################


@pytest.mark.django_db
def test_call_health_check_hits_health_branch():
    """
    Verify that /health/ endpoint bypasses authentication checks.
    This is critical for load balancers and monitoring systems.
    """
    rf = RequestFactory()
    request = rf.get("/health/")
    request.user = AnonymousUser()

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = LoginRequiredMiddleware(get_response)
    assert middleware(request) is mock_response


@pytest.mark.django_db
def test_call_health_without_trailing_slash():
    """
    Verify that /health endpoint (without trailing slash) also bypasses
    authentication checks.
    """
    rf = RequestFactory()
    request = rf.get("/health")
    request.user = AnonymousUser()

    mock_response = Mock()
    middleware = LoginRequiredMiddleware(Mock(return_value=mock_response))

    assert middleware(request) is mock_response


@pytest.mark.django_db
def test_call_authenticated_user_passes_through():
    """
    Verify that authenticated users can access any path through the
    __call__ method.
    """
    rf = RequestFactory()
    request = rf.get("/normal-path/")
    request.user = User.objects.create_user(username="auth", password="x")

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = LoginRequiredMiddleware(get_response)
    assert middleware(request) is mock_response


@pytest.mark.django_db
def test_call_authenticated_user_direct_call():
    """
    Verify that calling middleware.__call__() directly works correctly
    for authenticated users.
    """
    rf = RequestFactory()
    request = rf.get("/another-path/")
    request.user = User.objects.create_user(username="direct", password="x")

    mock_response = Mock()
    get_response = Mock(return_value=mock_response)

    middleware = LoginRequiredMiddleware(get_response)
    assert middleware.__call__(request) is mock_response


@pytest.mark.django_db
def test_call_anonymous_non_health_falls_through():
    """
    Verify that anonymous users on non-exempt paths still get a response
    from __call__ (authentication enforcement happens in process_view).
    """
    rf = RequestFactory()
    request = rf.get("/normal/")
    request.user = AnonymousUser()

    mock_response = Mock()
    middleware = LoginRequiredMiddleware(Mock(return_value=mock_response))

    response = middleware(request)
    assert response is mock_response


###############################################################################
# Integration Tests
###############################################################################


def test_health_check_exempt_client(client):
    """
    Integration test: Verify that the health check endpoint is accessible
    using Django's test client (simulates real HTTP request).
    """
    response = client.get("/health/")
    assert response.status_code == 200
