#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
app_core.urls
/srv/django/MikesLists_dev/app_core/urls.py

Adding decorators to the path function:
            from django.contrib.auth.decorators import login_required, permission_required
            path(
                    'settings/',
                    login_required(permission_required('is_staff')(views.settings_view)),
                    name='settings'
                ),


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
__version__ = "0.0.0.000027-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-16 23:00:33"
###############################################################################

"""
URL configuration for MikesLists project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from app_core.views.health import health
from app_core.views.status import status_view, dashboard


from app_core.views.home import (
    redirect_root_to_dashboard,
    redirect_home_to_dashboard,
    redirect_accounts_to_dashboard,
    redirect_dashboard_to_dashboard,
    catchall_redirect,
    redirect_pet,
)

from app_core.utils.auth import is_staff

from django.conf import settings

# NOTE  - Becarfull of the traling slash - it is important


urlpatterns = [
    # Admin
    # path("admin", admin.site.urls),
    path("admin/", admin.site.urls),

    # Redirect /home → dashboard
    # path("home", redirect_home_to_dashboard),
    path("home/", redirect_home_to_dashboard),

    # Redirect /dashboard → dashboard
    # path("dashboard", redirect_dashboard_to_dashboard),
    # path("dashboard/", redirect_dashboard_to_dashboard),
    path("dashboard/", dashboard, name="dashboard"),

    # Redirect ONLY /accounts and /accounts/ → dashboard
    path("accounts", redirect_accounts_to_dashboard),

    # path("accounts/", redirect_accounts_to_dashboard),
    path("accounts/", include("app_accounts.urls")),

    # ToDo
    path("todo/", include("app_ToDo.urls")),

    # Pet
    path("pet", redirect_pet),
    path("pet/", include("app_pet.urls")),

    # System / Core
    path("status", status_view, name="status_dashboard"),
    path("status/", status_view, name="status_dashboard"),

    # path("health", health, name="health_check"),
    path("health/", health, name="health_check"),

    # Site root → dashboard
    path("", redirect_root_to_dashboard, name="root_redirect"),

    # Global password reset URLs required by Django's built-in auth system
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]


# Catch‑all only in LIVE environment
if True:  # not settings.DEBUG:
    urlpatterns += [
        path("<path:path>", catchall_redirect, name="catchall"),
    ]
