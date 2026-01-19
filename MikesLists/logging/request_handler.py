#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
request_handler.py
MikesLists.logging.request_handler
/srv/django/MikesLists_dev/MikesLists/logging/request_handler.py


"""
__version__ = "0.0.0.000070-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 20:48:47"
###############################################################################
# from django.core.servers.basehttp import WSGIRequestHandler

# # class RequestHandlerWithIPAndUser(WSGIRequestHandler):
# #     def log_message(self, format, *args):
# #         print(">>> CUSTOM HANDLER ACTIVE <<<")


# #         # Extract IP
# #         ip = self.client_address[0]

# #         # Extract username if available
# #         user = getattr(getattr(self, "request", None), "user", None)
# #         if user and user.is_authenticated:
# #             username = user.get_username()
# #         else:
# #             username = "anonymous"

# #         # Build message
# #         msg = f"{ip} {username} " + (format % args)

# #         # Send to Django's logger
# #         self.server.logger.info(msg)

# class RequestHandlerWithIPAndUser(WSGIRequestHandler):
#     def log_message(self, format, *args):
#         print(">>> CUSTOM HANDLER ACTIVE <<<")
#         ip = self.client_address[0]
#         user = getattr(getattr(self, "request", None), "user", None)
#         username = user.get_username() if user and user.is_authenticated else "anonymous"
#         msg = f"{ip} {username} " + (format % args)
#         self.server.logger.info(msg)
