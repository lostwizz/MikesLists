import pytest
from django.contrib.auth.models import User, Permission
from app_accounts.permissions import get_user_permissions_list, has_permissions


# ---------------------------------------------------------
# get_user_permissions_list()
# ---------------------------------------------------------
@pytest.mark.django_db
def test_get_user_permissions_list_returns_list_of_permissions():
    user = User.objects.create_user(username="mike3", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    result = get_user_permissions_list(user)

    assert isinstance(result, list)

    expected = f"{perm.content_type.app_label}.{perm.codename}"
    assert expected in result




@pytest.mark.django_db
def test_has_permissions_any_perm_branch():
    user = User.objects.create_user(username="bob", password="x")

    perm = Permission.objects.first()
    user.user_permissions.add(perm)

    perm_list = [
        f"{perm.content_type.app_label}.{perm.codename}",
        "nonexistent.permission",
    ]

    assert has_permissions(user, perm_list, any_perm=True) is True
