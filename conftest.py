import pytest
from django.contrib.auth.models import User
from django.test import Client

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="mike", password="x")


@pytest.fixture
def editor():
    return User.objects.create_user(username="editor", password="x")


@pytest.fixture
def client():
    return Client()
