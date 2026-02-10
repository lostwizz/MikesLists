import pytest
from unittest.mock import patch
from django.urls import reverse
from django.test import override_settings



@override_settings(ADMIN_ALLOWED_IP_PREFIXES=["127.0.0.1"])
@patch("app_core.views.status.status_service.collect_checks", return_value=[])
@patch("app_core.services.status_service.network_diagnostics")
def test_status_view_network_panel(mock_net, mock_checks, client, django_user_model):
    mock_net.return_value = {
        "dns_google": {
            "ok": True,
            "emoji": "🟢",
            "latency_ms": 12.3,
            "details": {"ip": "8.8.8.8", "error": None},
        }
    }

    User = django_user_model
    user = User.objects.create_user("admin", password="x", is_staff=True)
    client.force_login(user)

    response = client.get(
        reverse("status_dashboard"),
        REMOTE_ADDR="127.0.0.1"
    )

    content = response.content.decode()

    assert "Network Diagnostics" in content
    assert "🟢" in content
    assert "12.3" in content
    assert "8.8.8.8" in content
