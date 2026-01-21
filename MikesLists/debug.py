#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
debug.py
MikesLists.debug
/srv/django/MikesLists_dev/MikesLists/debug.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-20 18:44:04"
###############################################################################

# /srv/django/MikesLists_dev/MikesLists/debug.py

class DebugViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            view_name = request.resolver_match.view_name
        except Exception:
            view_name = None

        print(f"[DEBUG] VIEW FUNC: {view_func} | VIEW NAME: {view_name}")
        return None
