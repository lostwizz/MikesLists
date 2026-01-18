#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
MikesLists.urls
/srv/django/MikesLists_dev/MikesLists/urls.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 15:30:01"
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
from django.urls import path, include

from django.contrib.auth import views as auth_views

from .view_status import status_view
from .home import home
from .health import health




urlpatterns = [
    path("admin/", admin.site.urls),
    # path("accounts/", include("accounts.urls")),   # This handles login/logout
    # path('accounts/', include('accounts.urls', namespace='accounts')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("status/", status_view, name="status_dashboard"),
    path("health/", health),
    path("", include("ToDo.urls")),               # This makes ToDo the homepage
]

# urlpatterns = [
#     # path('', home),
#     path("", include("ToDo.urls")),
#     path("admin/", admin.site.urls),
#     path("status/", status_view, name="status_dashboard"),
#     # path("accounts/", include("django.contrib.auth.urls")),
#     path("accounts/", include("accounts.urls")),  # All auth URLs start with /accounts/
#     path("health/", health),
#     path("login/", auth_views.LoginView.as_view(), name="login"),
#     path("todo/", include("ToDo.urls")),
# ]
