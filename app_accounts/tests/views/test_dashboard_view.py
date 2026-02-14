import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_dashboard_renders_template(client):
    # Create and log in a user
    user = User.objects.create_user(username="mike", password="x")
    client.login(username="mike", password="x")

    response = client.get(reverse("accounts:dashboard"))

    assert response.status_code == 200
    assert "app_accounts/dashboard_stats.html" in [t.name for t in response.templates]
