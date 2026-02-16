import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.messages import get_messages
from unittest.mock import patch

import logging


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(username="admin", password="x")
    group, _ = Group.objects.get_or_create(name="Admins")
    user.groups.add(group)
    return user


@pytest.mark.django_db
def test_group_manager_get_renders_template(client, admin_user):
    client.login(username="admin", password="x")

    url = reverse("accounts:group_manager")
    response = client.get(url)

    assert response.status_code == 200
    assert "app_accounts/group_manager.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_group_manager_post_assign_success(client, admin_user):
    client.login(username="admin", password="x")

    target = User.objects.create_user(username="bob", password="x")
    url = reverse("accounts:group_manager")

    with patch(
        "app_accounts.views.group_manager.assign_role_to_user", return_value=True
    ):
        response = client.post(
            url,
            {
                "user_id": target.id,
                "role_name": "Admins",
                "action": "assign",
            },
            follow=True,
        )

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any("Updated bob to Admins" in m for m in messages)


@pytest.mark.django_db
def test_group_manager_post_assign_failure(client, admin_user):
    client.login(username="admin", password="x")

    target = User.objects.create_user(username="bob", password="x")
    url = reverse("accounts:group_manager")

    with patch(
        "app_accounts.views.group_manager.assign_role_to_user", return_value=False
    ):
        response = client.post(
            url,
            {
                "user_id": target.id,
                "role_name": "Admins",
                "action": "assign",
            },
            follow=True,
        )

    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any("Role update failed" in m for m in messages)


@pytest.mark.django_db
def test_group_manager_post_clear_all(client, admin_user):
    client.login(username="admin", password="x")

    target = User.objects.create_user(username="bob", password="x")
    group = Group.objects.create(name="TestGroup")
    target.groups.add(group)

    url = reverse("accounts:group_manager")

    response = client.post(
        url,
        {
            "user_id": target.id,
            "role_name": "",  # <-- include this
            "action": "clear_all",
        },
        follow=True,
    )

    assert response
    target.refresh_from_db()
    assert target.groups.count() == 0


@pytest.mark.django_db
def test_group_manager_post_assign_exception(client, admin_user):
    client.login(username="admin", password="x")

    target = User.objects.create_user(username="bob", password="x")
    url = reverse("accounts:group_manager")

    # Patch the actual logger object Django uses
    with patch.object(logging.getLogger("django.request"), "error"):
        with patch(
            "app_accounts.views.group_manager.assign_role_to_user",
            side_effect=Exception("boom"),
        ):
            with pytest.raises(Exception):
                client.post(
                    url,
                    {
                        "user_id": target.id,
                        "role_name": "Admins",
                        "action": "assign",
                    },
                    follow=True,
                )


@pytest.mark.django_db
def test_group_manager_post_invalid_action(client, admin_user):
    """
    Test POST with an action that is neither 'assign' nor 'clear_all'.
    This covers the branch 62->66 where both if conditions are False.
    """
    client.login(username="admin", password="x")

    target = User.objects.create_user(username="bob", password="x")
    url = reverse("accounts:group_manager")

    response = client.post(
        url,
        {
            "user_id": target.id,
            "role_name": "",
            "action": "invalid_action",
        },
        follow=True,
    )

    # Should redirect without crashing
    assert response.status_code == 200
