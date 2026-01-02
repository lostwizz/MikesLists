import pytest

@pytest.mark.django_db
def test_user_count():
    from django.contrib.auth.models import User
    assert User.objects.count() == 0