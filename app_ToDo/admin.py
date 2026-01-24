#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
admin.py
app_ToDo.admin
/srv/django/MikesLists_dev/app_ToDo/admin.py



    ToDo app's  admin.py


"""
__version__ = "0.0.0.000011-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-23 01:22:39"
###############################################################################

from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
import re
from django.db import transaction

# from .models.lists import Lists
# from .models.items import Items

from .models.node import Node  # Adjust this based on where you put the Node class


# =================================================================
# =================================================================
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')


# =================================================================
# =================================================================
# @admin.register(Lists)
# class ListsAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", "completed", "created_at")
#     list_filter = ("completed",)
#     search_fields = ("title",)
#     # Autocomplete is better for Items; remove filter_horizontal
#     autocomplete_fields = ("items",)


# =================================================================
# =================================================================
# @admin.register(Items)
# class ItemsAdmin(admin.ModelAdmin):
#     # Primary List View Configuration
#     list_display = ("id", "title", "version", "completed", "clone_button")
#     list_display_links = ("id", "title")
#     list_editable = ("completed",)
#     list_filter = ("title", "completed", "created_at")
#     search_fields = ("title", "description")
#     ordering = ("title", "-version")

#     actions = ["make_completed", "compare_versions"]
#     save_as = True

#     # -----------------------------------------------------------------
#     # --- Actions ---
#     @admin.action(description="Mark selected items as completed")
#     def make_completed(self, request, queryset):
#         updated = queryset.update(completed=True)
#         self.message_user(
#             request,
#             f"Successfully marked {updated} items as completed.",
#             messages.SUCCESS,
#         )

#     # -----------------------------------------------------------------
#     @admin.action(description="Compare two selected versions")
#     def compare_versions(self, request, queryset):
#         if queryset.count() != 2:
#             self.message_user(
#                 request, "Please select exactly two items to compare.", messages.ERROR
#             )
#             return

#         items = queryset.order_by("version")
#         item1, item2 = items[0], items[1]

#         diff = {}
#         fields = ["title", "description", "version", "completed", "created_at"]
#         for field in fields:
#             val1, val2 = getattr(item1, field), getattr(item2, field)
#             if val1 != val2:
#                 diff[field] = {"v1": val1, "v2": val2}

#         return TemplateResponse(
#             request,
#             "admin/compare_items.html",
#             {
#                 "item1": item1,
#                 "item2": item2,
#                 "diff": diff,
#                 "title": "Compare Item Versions",
#             },
#         )

#     # -----------------------------------------------------------------
#     # --- Cloning Logic ---
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path(
#                 "<int:item_id>/clone/",
#                 self.admin_site.admin_view(self.clone_item),
#                 name="item-clone",
#             ),
#         ]
#         return custom_urls + urls

#     # -----------------------------------------------------------------
#     def clone_item(self, request, item_id):
#         original_item = self.get_object(request, item_id)

#         # Use the new model method
#         new_version = original_item.get_next_version()

#         with transaction.atomic():
#             new_item = Items.objects.create(
#                 title=original_item.title,
#                 description=original_item.description,
#                 version=new_version,
#                 completed=False,
#             )
#             print(f"{new_item=}")

#     # -----------------------------------------------------------------
#     def clone_button(self, obj):
#         return format_html(
#             '<a class="button" href="{}">Clone</a>',
#             reverse("admin:item-clone", args=[obj.pk]),
#         )

#     clone_button.short_description = "Clone"

#     # -----------------------------------------------------------------
#     def get_changeform_initial_data(self, request):
#         initial = super().get_changeform_initial_data(request)
#         initial["version"] = "0.0.0.000011-dev"
#         return initial
