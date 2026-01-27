
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
__init__.py
app_accounts.utils
app_accounts.utils/srv/django/MikesLists_dev/app_accounts/utils/__init__.py

Now in your views, you can just do: from app_accounts.utils import is_in_group, check_user_perms

"""
__version__ = "0.0.0.000021-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-27 11:14:36"
###############################################################################


from .roles import *
from .permissions import *
from .user_helpers import *
