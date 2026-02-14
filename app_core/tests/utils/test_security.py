import pytest
from unittest.mock import MagicMock, patch
from django.test import override_settings

from app_core.utils.security import is_admin_access_allowed


@override_settings(ADMIN_ALLOWED_IP_PREFIXES=["192.168.1."])
@patch("app_core.utils.security.get_client_ip", return_value="192.168.1.55")
@patch("app_core.utils.security.is_ip_allowed_for_admin", return_value=True)
def test_admin_access_allowed(mock_allowed, mock_ip):
    request = MagicMock()
    assert is_admin_access_allowed(request) is True

    mock_ip.assert_called_once_with(request)
    mock_allowed.assert_called_once_with("192.168.1.55", ["192.168.1."])


@override_settings(ADMIN_ALLOWED_IP_PREFIXES=["10.0.0."])
@patch("app_core.utils.security.get_client_ip", return_value="192.168.1.55")
@patch("app_core.utils.security.is_ip_allowed_for_admin", return_value=False)
def test_admin_access_denied(mock_allowed, mock_ip):
    request = MagicMock()
    assert is_admin_access_allowed(request) is False

    mock_ip.assert_called_once_with(request)
    mock_allowed.assert_called_once_with("192.168.1.55", ["10.0.0."])
