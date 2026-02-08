""" """

import pytest
from django.test import RequestFactory, override_settings
from django.contrib.auth.models import AnonymousUser, User
from app_core.context_processors import export_env_vars, user_info
from app_accounts.models import Profile


@pytest.fixture
def rf():
    return RequestFactory()


def test_export_env_vars(rf):
    with override_settings(ENV_NAME="dev"):
        request = rf.get("/")
        assert export_env_vars(request) == {"env": "dev"}


pytestmark = pytest.mark.django_db


def test_user_info_authenticated(rf):
    user = User.objects.create_user(username="mike", password="x")
    profile = Profile.objects.get(user=user)

    request = rf.get("/", REMOTE_ADDR="1.2.3.4")
    request.user = user

    ctx = user_info(request)

    assert ctx["sidebar_username"] == "mike"
    assert ctx["sidebar_ip"] == "1.2.3.4"
    assert ctx["sidebar_env"]  # optional: depends on your env setup
    assert ctx["user_profile"] == profile


def test_profile_str(self):
    p = Profile.objects.create(user=self.user)
    assert str(p) == "mike"

def test_profile_has_avatar(self):
    p = Profile.objects.create(user=self.user, avatar_blob=b"123")
    assert p.has_avatar is True

def test_editor_cannot_delete_profile(self):
    self.client.force_login(self.editor)
    response = self.client.post("/accounts/delete/1/")
    assert response.status_code == 403

def test_profile_detail_view(self):
    self.client.force_login(self.user)
    response = self.client.get(f"/accounts/profile/{self.user.id}/")
    assert response.status_code == 200
