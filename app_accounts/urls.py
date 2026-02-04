#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
app_accounts.urls
/srv/django/MikesLists_dev/app_accounts/urls.py


"""
__version__ = "0.0.0.000015-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-02 12:34:32"
###############################################################################

from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

from django.shortcuts import render  # Make sure this is imported!

# Local views
from .views.dashboard import dashboard
from .views.group_manager import group_manager_view
from .views.profile import profile_view, edit_profile
from .views.register import register


app_name = "accounts"


class LogoutAllowGet(LogoutView):
    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):
        """Perform logout on GET request without a confirmation page."""
        return self.post(request, *args, **kwargs)


# def logged_out_template_view(request):
#     return render(request, "registration/logged_out.html")


def logged_out(request):
    # from django.contrib.auth import logout
    # logout(request)  # clears admin session too
    return render(request, "registration/logged_out.html")


urlpatterns = [
    # # Authentication
    # path("login/", auth_views.LoginView.as_view(), name="login"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "logout/",
        LogoutAllowGet.as_view(next_page="accounts:logged_out"),
        name="logout",
    ),
    path("logged-out/", logged_out, name="logged_out"),
    # Password Change (Logged-in users)
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/accounts/password-change/done/",
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # Password Reset Flow
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Main Dashboard
    path("dashboard/", dashboard, name="dashboard"),
    # Registration
    path("register/", register, name="register"),
    # Profile Management
    path("profile", profile_view, name="profile_detail"),
    path("profile/", profile_view, name="profile_detail"),
    path("profile/edit", edit_profile, name="edit_profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    # Staff/Admin Tools
    path("group-manager/", group_manager_view, name="group_manager"),
]
