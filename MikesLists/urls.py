#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
urls.py


# TODO:
# COMMENT:
# NOTE:
# USEFULL:
# LEARN:
# RECHECK:
# INCOMPLETE:
# SEE NOTES:
# POST
# HACK

"""
__version__ = "0.0.0.00010-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-03 00:17:13"
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



from .view_status import status_view
from .home import home
from .health import health

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path("status/", status_view, name ="status_dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("health/", health),
]
