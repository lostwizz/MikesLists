import pytest
from unittest.mock import Mock

from django.contrib.auth.models import User, Group, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from app_accounts.utils.decorators import group_required, user_owns_object

from django.db import models

# class DummyOwned(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)



@pytest.mark.django_db
def test_group_required_redirects_if_not_authenticated():
    rf = RequestFactory()
    request = rf.get("/test/")
    request.user = AnonymousUser()

    @group_required("Admins")
    def dummy_view(request):
        return "OK"

    response = dummy_view(request)
    assert response.status_code == 302
    assert "login" in response.url




@pytest.mark.django_db
def test_group_required_allows_superuser():
    rf = RequestFactory()
    request = rf.get("/test/")
    request.user = User.objects.create(username="admin", is_superuser=True)

    @group_required("Admins")
    def dummy_view(request):
        return "OK"

    assert dummy_view(request) == "OK"



@pytest.mark.django_db
def test_group_required_allows_group_member():
    rf = RequestFactory()
    request = rf.get("/test/")

    group, _ = Group.objects.get_or_create(name="Admins")


    user = User.objects.create(username="bob")
    user.groups.add(group)

    request.user = user

    @group_required("Admins")
    def dummy_view(request):
        return "OK"

    assert dummy_view(request) == "OK"



@pytest.mark.django_db
def test_group_required_denies_non_member():
    rf = RequestFactory()
    request = rf.get("/test/")
    request.user = User.objects.create(username="bob")

    @group_required("Admins")
    def dummy_view(request):
        return "OK"

    with pytest.raises(PermissionDenied):
        dummy_view(request)



@pytest.mark.django_db
def test_user_owns_object_allows_owner(mocker):
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from app_accounts.utils.decorators import user_owns_object

    rf = RequestFactory()
    request = rf.get("/test/")
    owner = User.objects.create(username="owner")
    request.user = owner

    # Mock model_class.objects.get()
    mock_model = mocker.Mock()
    mock_obj = mocker.Mock(user=owner)
    mock_model.objects.get.return_value = mock_obj

    @user_owns_object(mock_model)
    def dummy_view(request, pk):
        return "OK"

    assert dummy_view(request, 1) == "OK"



@pytest.mark.django_db
def test_user_owns_object_denies_non_owner(mocker):
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from django.core.exceptions import PermissionDenied
    from app_accounts.utils.decorators import user_owns_object

    rf = RequestFactory()
    request = rf.get("/test/")
    owner = User.objects.create(username="owner")
    other = User.objects.create(username="other")
    request.user = other

    mock_model = mocker.Mock()
    mock_obj = mocker.Mock(user=owner)
    mock_model.objects.get.return_value = mock_obj

    @user_owns_object(mock_model)
    def dummy_view(request, pk):
        return "OK"

    with pytest.raises(PermissionDenied):
        dummy_view(request, 1)



@pytest.mark.django_db
def test_user_owns_object_allows_superuser(mocker):
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from app_accounts.utils.decorators import user_owns_object

    rf = RequestFactory()
    request = rf.get("/test/")
    superuser = User.objects.create(username="admin", is_superuser=True)
    request.user = superuser

    mock_model = mocker.Mock()
    mock_obj = mocker.Mock(user=None)
    mock_model.objects.get.return_value = mock_obj

    @user_owns_object(mock_model)
    def dummy_view(request, pk):
        return "OK"

    assert dummy_view(request, 1) == "OK"
