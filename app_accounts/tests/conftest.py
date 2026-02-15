# app_accounts/tests/conftest.py
import pytest
from django.contrib.auth.models import User, Group

@pytest.fixture
def admin_user(db):
    """Reusable admin user fixture"""
    user = User.objects.create_user(username="admin", password="x")
    group, _ = Group.objects.get_or_create(name="Admins")
    user.groups.add(group)
    return user

@pytest.fixture
def regular_user(db):
    """Reusable regular user fixture"""
    return User.objects.create_user(username="user", password="x")
