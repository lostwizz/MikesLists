import pytest
from unittest.mock import MagicMock
from django.contrib.auth.models import User, Group

# from app_accounts.forms.CustomUserChangeForm import CustomUserChangeForm
from app_accounts.forms.custom_user_change_form import CustomUserChangeForm


@pytest.mark.django_db
def test_custom_user_change_form_non_superuser_filters_groups():
    # Create a user with one group
    user = User.objects.create(username="normal")
    g1 = Group.objects.create(name="G1")
    user.groups.add(g1)

    # Fake request with non-superuser
    request = MagicMock()
    request.user = MagicMock(is_superuser=False)

    form = CustomUserChangeForm(
        request=request,
        instance=user,
        data={"first_name": "A", "last_name": "B", "email": "x@test.com", "username": "normal"}
    )

    # The queryset should be filtered to ONLY the user's groups
    assert list(form.fields["groups"].queryset) == list(user.groups.all())
    assert form.fields["groups"].disabled is True


@pytest.mark.django_db
def test_custom_user_change_form_superuser_sees_all_groups():
    # Create two groups
    g1 = Group.objects.create(name="G1")
    g2 = Group.objects.create(name="G2")

    user = User.objects.create(username="admin")

    # Fake request with superuser
    request = MagicMock()
    request.user = MagicMock(is_superuser=True)

    form = CustomUserChangeForm(
        request=request,
        instance=user,
        data={"first_name": "A", "last_name": "B", "email": "x@test.com", "username": "admin"}
    )

    # Superuser should see ALL groups
    assert set(form.fields["groups"].queryset) == set(Group.objects.all())
    assert form.fields["groups"].disabled is False
