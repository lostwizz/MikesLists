#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_example.py


# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK
# INCOMPLETE
# SEE NOTES
# POST
# HACK
# FIXME
# BUG
# [ ] something to do
# [x]  i did sometrhing



"""
__version__ = "0.0.1.000005-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-02 22:08:54"
###############################################################################
import pytest

@pytest.mark.django_db
def test_user_count():
    from django.contrib.auth.models import User
    assert User.objects.count() == 0