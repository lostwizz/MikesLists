#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_profile_view.py

Tests for profile view functionality including profile editing and display.
"""
###############################################################################

import pytest
import io
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from django.contrib.auth.models import User

from app_accounts.models.profile import Profile


###############################################################################
# edit_profile View Tests
###############################################################################

@pytest.mark.django_db
def test_edit_profile_get(client, django_user_model):
    """
    Test that authenticated users can access the profile edit page.
    Covers the else branch (lines 64-66).
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )
    # Profile auto-created by signal

    client.login(username="bob", password="x")

    response = client.get(reverse("accounts:edit_profile"))

    assert response.status_code == 200
    assert "app_accounts/edit_profile.html" in [t.name for t in response.templates]
    assert 'u_form' in response.context
    assert 'p_form' in response.context


@pytest.mark.django_db
def test_edit_profile_post_valid_no_image(client, django_user_model):
    """
    Test that users can successfully update their profile without uploading an image.
    Covers lines 28-33 and the path without avatar upload (skips lines 37-57).
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )
    # Profile auto-created by signal

    client.login(username="bob", password="x")

    url = reverse("accounts:edit_profile")

    response = client.post(
        url,
        {
            "username": "bob",
            "email": "bob@example.com",
            "first_name": "Robert",
            "last_name": "Smith",
            "bio": "hello world",
            "location": "New York",
            "timezone": "America/New_York",
            "email_notifications": "on",
            "theme_preference": "dark",
        },
        follow=True,
    )

    # Should redirect to profile_detail
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse('accounts:profile_detail')

    # Verify profile was updated
    user.refresh_from_db()
    user.profile.refresh_from_db()
    assert user.profile.bio == "hello world"
    assert user.profile.location == "New York"
    assert user.profile.theme_preference == "dark"
    assert user.first_name == "Robert"

    # Verify success message
    messages = list(response.context['messages'])
    assert any('profile has been updated' in str(m) for m in messages)


@pytest.mark.django_db
def test_edit_profile_post_with_jpeg_image(client, django_user_model):
    """
    Test that users can upload a JPEG avatar image.
    Covers lines 37-57 (image upload and processing).
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )
    # Profile auto-created by signal

    client.login(username="bob", password="x")

    # Create a test JPEG image
    img = Image.new("RGB", (500, 500), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)

    uploaded = SimpleUploadedFile(
        "avatar.jpg",
        buffer.getvalue(),
        content_type="image/jpeg"
    )

    url = reverse("accounts:edit_profile")

    response = client.post(
        url,
        {
            "username": "bob",
            "email": "bob@example.com",
            "first_name": "",
            "last_name": "",
            "bio": "test bio",
            "location": "",
            "timezone": "UTC",
            "email_notifications": "on",
            "theme_preference": "light",
            "avatar": uploaded,
        },
        follow=True,
    )

    assert response.status_code == 200

    # Verify avatar was saved
    user.profile.refresh_from_db()
    assert user.profile.avatar_blob is not None
    assert user.profile.avatar_mimetype == "image/jpeg"


@pytest.mark.django_db
def test_edit_profile_post_with_png_image(client, django_user_model):
    """
    Test that users can upload a PNG image and it gets converted to JPEG.
    Covers lines 44-46 (RGBA/P mode conversion to RGB).
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )

    client.login(username="bob", password="x")

    # Create a PNG image with transparency (RGBA mode)
    img = Image.new("RGBA", (500, 500), color=(255, 0, 0, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    uploaded = SimpleUploadedFile(
        "avatar.png",
        buffer.getvalue(),
        content_type="image/png"
    )

    url = reverse("accounts:edit_profile")

    response = client.post(
        url,
        {
            "username": "bob",
            "email": "bob@example.com",
            "first_name": "",
            "last_name": "",
            "bio": "",
            "location": "",
            "timezone": "UTC",
            "email_notifications": "on",
            "theme_preference": "light",
            "avatar": uploaded,
        },
        follow=True,
    )

    assert response.status_code == 200

    # Verify PNG was converted to JPEG
    user.profile.refresh_from_db()
    assert user.profile.avatar_blob is not None
    assert user.profile.avatar_mimetype == "image/jpeg"


@pytest.mark.django_db
def test_edit_profile_post_with_palette_mode_image(client, django_user_model):
    """
    Test that palette mode (P) images are converted to RGB.
    Covers the P mode conversion in line 45.
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )

    client.login(username="bob", password="x")

    # Create a palette mode image
    img = Image.new("P", (500, 500))
    # Add some color
    img.putpalette([255, 0, 0] * 256)  # Red palette
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    uploaded = SimpleUploadedFile(
        "avatar_palette.png",
        buffer.getvalue(),
        content_type="image/png"
    )

    url = reverse("accounts:edit_profile")

    response = client.post(
        url,
        {
            "username": "bob",
            "email": "bob@example.com",
            "first_name": "",
            "last_name": "",
            "bio": "",
            "location": "",
            "timezone": "UTC",
            "email_notifications": "on",
            "theme_preference": "light",
            "avatar": uploaded,
        },
        follow=True,
    )

    assert response.status_code == 200
    user.profile.refresh_from_db()
    assert user.profile.avatar_blob is not None


@pytest.mark.django_db
def test_edit_profile_post_invalid_form(client, django_user_model):
    """
    Test that invalid form submissions re-render the form with errors.
    Covers the case where forms are not valid (implicit else after line 33).
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )

    client.login(username="bob", password="x")

    url = reverse("accounts:edit_profile")

    # Submit with invalid data (empty username)
    response = client.post(url, {"username": ""})

    # Should re-render form, not redirect
    assert response.status_code == 200
    assert "app_accounts/edit_profile.html" in [t.name for t in response.templates]
    assert 'u_form' in response.context
    assert 'p_form' in response.context


@pytest.mark.django_db
def test_edit_profile_requires_login(client):
    """
    Test that unauthenticated users are redirected to login.
    Covers the @login_required decorator.
    """
    url = reverse("accounts:edit_profile")
    response = client.get(url)

    # Should redirect to login
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


###############################################################################
# profile_view Tests
###############################################################################

@pytest.mark.django_db
def test_profile_view(client, django_user_model):
    """
    Test that users can view their profile page.
    Covers lines 73-75.
    """
    user = django_user_model.objects.create_user(
        username="bob", password="x", email="bob@example.com"
    )
    # Profile auto-created by signal

    client.login(username="bob", password="x")

    response = client.get(reverse("accounts:profile_detail"))

    assert response.status_code == 200
    assert "app_accounts/profile_detail.html" in [t.name for t in response.templates]
    assert response.context['user'] == user


@pytest.mark.django_db
def test_profile_view_requires_login(client):
    """
    Test that unauthenticated users cannot access profile view.
    """
    url = reverse("accounts:profile_detail")
    response = client.get(url)

    # Should redirect to login
    assert response.status_code == 302
    assert '/accounts/login/' in response.url
