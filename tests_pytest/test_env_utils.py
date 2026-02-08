'''
test_env_utils
/srv/django/MikesLists_dev/app_core/tests/tests_pytest/test_env_utils.py

'''


import pytest
from django.test import override_settings
from app_core.utils.env import get_env, is_dev

@pytest.mark.parametrize("env,expected", [
    ("dev", ("dev", True)),
    ("live", ("live", False)),
    ("test", ("test", False)),
])
def test_env_utils(env, expected):
    with override_settings(ENV_NAME=env):
        assert get_env() == expected[0]
        assert is_dev() == expected[1]
