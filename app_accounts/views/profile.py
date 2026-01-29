#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
profile.py
app_accounts.views.profile
/srv/django/MikesLists_dev/app_accounts/views/profile.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:05:48"
###############################################################################
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from io import BytesIO
from PIL import Image  # CRITICAL: Needed for the resizing logic

# Import both forms from your forms package
from ..forms.CustomUserChangeForm import CustomUserChangeForm
from ..forms.profileForm import ProfileUpdateForm, UserUpdateForm


@login_required
def edit_profile(request):
    if request.method == 'POST':
        # You'll likely want to handle the User form and Profile form together
        u_form = CustomUserChangeForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            profile = p_form.save(commit=False)

            # Check if a new image was uploaded
            if 'avatar' in request.FILES:
                uploaded_file = request.FILES['avatar']

                # 1. Open with Pillow
                img = Image.open(uploaded_file)

                # Convert to RGB if it's a PNG with transparency (to save as JPEG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img.thumbnail((300, 300))

                # 2. Save to memory buffer
                buffer = BytesIO()
                # We force JPEG to keep the BLOB size small in MariaDB
                img.save(buffer, format="JPEG", quality=85)

                # 3. Save bytes to the blob field
                profile.avatar_blob = buffer.getvalue()
                profile.avatar_mimetype = "image/jpeg"

            profile.save()
            messages.success(request, 'Your profile has been updated and synced to the database!')
            return redirect('accounts:profile_detail')
    else:
        u_form = CustomUserChangeForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'app_accounts/edit_profile.html', context)

@login_required
def profile_view(request):
    """Simple read-only view of the user's profile."""
    return render(request, 'app_accounts/profile_detail.html', {'user': request.user})
