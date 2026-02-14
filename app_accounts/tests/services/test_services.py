import pytest
from unittest.mock import patch

from django.contrib.auth.models import User
from app_accounts.services.services import (
    UserRegistrationService,
    UserLifecycleService,
)


# ---------------------------------------------------------
# UserRegistrationService.register_new_user
# ---------------------------------------------------------
@pytest.mark.django_db
@patch("app_accounts.services.services.assign_role_to_user")
def test_register_new_user(mock_assign_role):
    data = {
        "username": "mike",
        "email": "mike@example.com",
        "password": "secret",
        "bio": "Hello world",
    }

    user = UserRegistrationService.register_new_user(data)

    # User created
    assert User.objects.filter(username="mike").exists()

    # Profile updated
    assert user.profile.bio == "Hello world"

    # Role assignment called
    mock_assign_role.assert_called_once_with(user, "Viewer")


# ---------------------------------------------------------
# UserLifecycleService.register_user
# ---------------------------------------------------------
@pytest.mark.django_db
@patch("app_accounts.services.services.assign_role_to_user")
def test_lifecycle_register_user(mock_assign_role):
    user = UserLifecycleService.register_user(
        username="john",
        email="john@example.com",
        password="pass123",
        role="Editor",
    )

    assert User.objects.filter(username="john").exists()
    mock_assign_role.assert_called_once_with(user, "Editor")


# ---------------------------------------------------------
# UserLifecycleService.delete_user_safely
# ---------------------------------------------------------
@pytest.mark.django_db
def test_delete_user_safely():
    user = User.objects.create_user(username="temp", password="x")
    user_id = user.id

    result = UserLifecycleService.delete_user_safely(user_id)

    assert result is True
    assert not User.objects.filter(id=user_id).exists()


# ---------------------------------------------------------
# UserLifecycleService.promote_user
# ---------------------------------------------------------
@pytest.mark.django_db
@patch("app_accounts.services.services.assign_role_to_user")
def test_promote_user(mock_assign_role):
    user = User.objects.create_user(username="bob", password="x")

    UserLifecycleService.promote_user(user, "Admin")

    mock_assign_role.assert_called_once_with(user, "Admin", clear_existing=True)
