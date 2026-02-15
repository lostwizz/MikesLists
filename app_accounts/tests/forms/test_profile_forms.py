#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_profile_forms.py
Tests for UserUpdateForm and ProfileUpdateForm
"""
###############################################################################

import pytest
from django.contrib.auth.models import User
# from forms.profile_form import UserUpdateForm, ProfileUpdateForm
from app_accounts.forms.profile_form import UserUpdateForm, ProfileUpdateForm



@pytest.mark.django_db
def test_user_update_form_initializes_widgets():
    user = User.objects.create(username="mike", email="mike@example.com")

    form = UserUpdateForm(instance=user)

    # All fields should have class="form-control"
    for field in form.fields.values():
        assert field.widget.attrs.get("class") == "form-control"


@pytest.mark.django_db
def test_profile_update_form_initializes_all_widget_types():
    user = User.objects.create(username="mike", email="mike@example.com")

    # IMPORTANT: use the auto-created profile from the signal
    profile = user.profile

    form = ProfileUpdateForm(instance=profile)

    # CheckboxInput branch
    checkbox = form.fields["email_notifications"].widget
    assert checkbox.attrs.get("class") == "form-check-input"

    # Select branch
    select = form.fields["theme_preference"].widget
    assert select.attrs.get("class") == "form-select"

    # Textarea branch
    textarea = form.fields["bio"].widget
    assert textarea.attrs.get("class") == "form-control"

    # TextInput branch
    textinput = form.fields["location"].widget
    assert textinput.attrs.get("class") == "form-control"
