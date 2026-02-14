import pytest
from django.contrib.auth import get_user_model
from django.http import Http404

from app_accounts.utils.user_helpers import get_active_users, toggle_user_status

User = get_user_model()


@pytest.mark.django_db
def test_get_active_users_filters_correctly():
    active = User.objects.create(username="active", is_active=True)
    inactive = User.objects.create(username="inactive", is_active=False)

    result = list(get_active_users())

    assert active in result
    assert inactive not in result


@pytest.mark.django_db
def test_toggle_user_status_deactivates_user():
    user = User.objects.create(username="mike", is_active=True)

    new_status = toggle_user_status(user.id)

    assert new_status is False
    user.refresh_from_db()
    assert user.is_active is False


@pytest.mark.django_db
def test_toggle_user_status_activates_user():
    user = User.objects.create(username="mike2", is_active=False)

    new_status = toggle_user_status(user.id)

    assert new_status is True
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_toggle_user_status_raises_404_for_missing_user():
    with pytest.raises(Http404):
        toggle_user_status(999999)  # nonexistent ID
