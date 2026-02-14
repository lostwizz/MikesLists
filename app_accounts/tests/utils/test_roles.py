import pytest
from unittest.mock import Mock

from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from app_accounts.utils.roles import (
    require_group,
    get_user_role,
    sync_group_permissions,
    assign_role_to_user,
)

from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView


def test_require_group_does_not_wrap_auth_views():
    dec = require_group("Admins")

    assert dec(LogoutView) is LogoutView
    assert dec(LoginView) is LoginView
    assert dec(PasswordResetView) is PasswordResetView


@pytest.mark.django_db
def test_require_group_denies_unauthenticated():
    rf = RequestFactory()
    request = rf.get("/test/")
    request.user = Mock(is_authenticated=False)

    @require_group("Admins")
    def dummy(request):
        return "OK"

    with pytest.raises(PermissionDenied):
        dummy(request)


@pytest.mark.django_db
def test_require_group_denies_non_member():
    rf = RequestFactory()
    request = rf.get("/test/")
    user = User.objects.create(username="bob")
    request.user = user

    @require_group("Admins")
    def dummy(request):
        return "OK"

    with pytest.raises(PermissionDenied):
        dummy(request)




@pytest.mark.django_db
def test_require_group_allows_member():
    rf = RequestFactory()
    request = rf.get("/test/")

    group, _ = Group.objects.get_or_create(name="Admins")
    user = User.objects.create(username="bob")
    user.groups.add(group)
    request.user = user

    @require_group("Admins")
    def dummy(request):
        return "OK"

    assert dummy(request) == "OK"



@pytest.mark.django_db
def test_get_user_role_anonymous_none():
    assert get_user_role(None) == "anonymous"


@pytest.mark.django_db
def test_get_user_role_anonymous_user():
    user = Mock(is_anonymous=True)
    assert get_user_role(user) == "anonymous"


@pytest.mark.django_db
def test_get_user_role_superuser():
    user = User.objects.create(username="admin", is_superuser=True)
    assert get_user_role(user) == "admin"


@pytest.mark.django_db
def test_get_user_role_staff():
    user = User.objects.create(username="staff", is_staff=True)
    assert get_user_role(user) == "staff"


@pytest.mark.django_db
def test_get_user_role_default_user():
    user = User.objects.create(username="bob")
    assert get_user_role(user) == "user"


@pytest.mark.django_db
def test_sync_group_permissions_sets_correct_perms():
    # Create a permission to match
    perm = Permission.objects.first()
    app_label = perm.content_type.app_label
    codename = perm.codename

    group = sync_group_permissions("Managers", {app_label: [codename]})

    assert group.permissions.filter(codename=codename).exists()



@pytest.mark.django_db
def test_assign_role_to_user_success():
    user = User.objects.create(username="bob")
    group, _ = Group.objects.get_or_create(name="Admins")

    assert assign_role_to_user(user, "Admins") is True
    assert group in user.groups.all()



@pytest.mark.django_db
def test_assign_role_to_user_group_missing():
    user = User.objects.create(username="bob")

    assert assign_role_to_user(user, "NoSuchGroup") is False


@pytest.mark.django_db
def test_assign_role_to_user_clear_existing():
    user = User.objects.create(username="bob")

    g1, _ = Group.objects.get_or_create(name="Old")
    g2, _ = Group.objects.get_or_create(name="New")

    user.groups.add(g1)

    assign_role_to_user(user, "New", clear_existing=True)

    assert list(user.groups.all()) == [g2]
