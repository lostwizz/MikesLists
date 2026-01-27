#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
__init__.py
app_accounts.views
/srv/django/MikesLists_dev/app_accounts/views/__init__.py

-- views--
from .services import UserLifecycleService
# ...
UserLifecycleService.promote_user(target_user, "Manager")

-- template--
{% load auth_extras %}

<p>Your Role: {% get_user_role user %}</p>

{% if user|has_group:"Admins" %}
   <button>Admin Control Panel</button>
{% endif %}


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:03:57"
###############################################################################

from django.contrib.auth import logout


from .login import *
from .profile import *
from .register import *
# from .permissions import *
# from .group_manager import *
# from .dashboard import *
