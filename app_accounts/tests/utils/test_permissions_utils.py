import pytest
from django.contrib.auth.models import User, Permission
from app_accounts.utils.permissions import get_perms_for_app, check_user_perms


@pytest.mark.django_db
def test_get_perms_for_app_returns_permissions():
    # Pick an app that definitely has permissions
    perms = get_perms_for_app("auth")

    assert perms.exists()
    assert all(p.content_type.app_label == "auth" for p in perms)


@pytest.mark.django_db
def test_check_user_perms_any_logic():
    user = User.objects.create_user(username="mike", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    perm_list = [
        f"{perm.content_type.app_label}.{perm.codename}",  # True
        "auth.nonexistent_perm",                           # False
    ]

    assert check_user_perms(user, perm_list, logic="any") is True


@pytest.mark.django_db
def test_check_user_perms_all_logic():
    user = User.objects.create_user(username="mike2", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    perm_list = [
        f"{perm.content_type.app_label}.{perm.codename}",  # True
        "auth.nonexistent_perm",                           # False
    ]

    assert check_user_perms(user, perm_list, logic="all") is False
