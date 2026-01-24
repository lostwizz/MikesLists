#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py
app_core.urls
/srv/django/MikesLists_dev/app_core/urls.py



"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 19:50:15"
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
from django.shortcuts import redirect

from .view_status import status_view
from .health import health

from django.contrib.auth.decorators import login_required



def redirect_root_to_dashboard(request):
    return redirect('accounts:dashboard')

urlpatterns = [
    path("admin/", admin.site.urls),

    # Accounts app (dashboard, profile, groups, ToDo page, auth)
    path('app_accounts/', include('app_accounts.urls', namespace='accounts')),

    # ToDo app  ← THIS IS THE MISSING PIECE
    path('app_ToDo/', include('app_ToDo.urls', namespace='todo')),

    # System pages
    path("status/", status_view, name="status_dashboard"),
    path("health/", health),

    # Site root → dashboard
    # path("", redirect_root_to_dashboard, name='root_redirect'),
    path("", login_required(redirect_root_to_dashboard), name="root_redirect"),
]
