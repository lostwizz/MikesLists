#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_example.py
tests.test_example
/srv/django/MikesLists_dev/tests/test_example.py


"""
__version__ = "0.0.1.000005-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-19 18:45:36"
###############################################################################
import pytest

@pytest.mark.django_db
def test_user_count():
    from django.contrib.auth.models import User
    assert User.objects.count() == 0
