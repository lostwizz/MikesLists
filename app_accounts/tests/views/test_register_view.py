#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_register_view.py

Tests for user registration view.
"""
###############################################################################

import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_register_get_displays_form(client):
    """
    Test that GET request to register page displays the registration form.
    """
    response = client.get(reverse("accounts:register"))

    assert response.status_code == 200
    assert "registration/register.html" in [t.name for t in response.templates]
    assert "form" in response.context


@pytest.mark.django_db
def test_register_post_valid_creates_user(client):
    """
    Test that valid POST request creates a new user and logs them in.
    Covers lines 31-46 in register.py
    """
    url = reverse("accounts:register")

    data = {
        "username": "newuser",
        "password1": "TestPass123!",
        "password2": "TestPass123!",
    }

    response = client.post(url, data, follow=True)

    # Verify user was created
    assert User.objects.filter(username="newuser").exists()

    # Verify user was logged in (redirected to dashboard)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse("accounts:dashboard")

    # Verify success message
    messages = list(response.context["messages"])
    assert len(messages) > 0
    assert "Registration successful" in str(messages[0])
    assert "Welcome, newuser" in str(messages[0])


@pytest.mark.django_db
def test_register_post_invalid_shows_errors(client):
    """
    Test that invalid POST request shows form errors.
    """
    url = reverse("accounts:register")

    # Invalid data - passwords don't match
    data = {
        "username": "newuser",
        "password1": "TestPass123!",
        "password2": "DifferentPass123!",
    }

    response = client.post(url, data)

    # Should not create user
    assert not User.objects.filter(username="newuser").exists()

    # Should re-render form with errors
    assert response.status_code == 200
    assert "registration/register.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_register_post_duplicate_username(client):
    """
    Test that attempting to register with an existing username fails.
    """
    # Create existing user
    User.objects.create_user(username="existinguser", password="pass")

    url = reverse("accounts:register")

    data = {
        "username": "existinguser",  # Duplicate username
        "password1": "TestPass123!",
        "password2": "TestPass123!",
    }

    response = client.post(url, data)

    # Should show form with error
    assert response.status_code == 200
    assert response.context["form"].errors

    # Should only have one user with that username
    assert User.objects.filter(username="existinguser").count() == 1


@pytest.mark.django_db
def test_register_creates_profile_via_signal(client):
    """
    Test that registering a user also creates their profile via signals.
    """
    url = reverse("accounts:register")

    data = {
        "username": "profiletest",
        "password1": "TestPass123!",
        "password2": "TestPass123!",
    }

    response = client.post(url, data, follow=True)
    assert response

    # Verify user was created
    user = User.objects.get(username="profiletest")

    # Verify profile was created by signal
    assert hasattr(user, "profile")
    assert user.profile is not None
