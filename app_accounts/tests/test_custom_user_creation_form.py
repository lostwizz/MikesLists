#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_custom_user_creation_form.py
app_accounts.tests.test_custom_user_creation_form
/srv/django/MikesLists_dev/app_accounts/tests/test_custom_user_creation_form.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 00:58:46"
###############################################################################

# forms_tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from app_accounts.forms import CustomUserCreationForm

class CustomUserCreationFormTestCase(TestCase):
    def test_custom_user_creation_form(self):
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'test@example.com'
        }
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_missing_email(self):
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['This field is required.'])

    # Add more test methods as needed
