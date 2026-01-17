#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_models.py

# how to run tests:
#       python manage.py test ToDo --settings=MikesLists.settings.dev
#    or? python manage.py test
"""
__version__ = "0.0.1.000002-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-16 20:23:16"
###############################################################################

from django.test import TestCase
from ToDo.models.items import Items
from ToDo.models.lists import Lists

# =================================================================
# =================================================================
class ToDoModelTest(TestCase):

    # -----------------------------------------------------------------
    def setUp(self):
        # Create a sample item
        self.item = Items.objects.create(
            title="Test Task",
            version="1.0",
            description="A test description"
        )
        # Create a sample list
        self.todo_list = Lists.objects.create(
            title="Work List"
        )

    # -----------------------------------------------------------------
    def test_item_creation(self):
        """Test if an item is created with correct defaults"""
        self.assertEqual(self.item.title, "Test Task")
        self.assertFalse(self.item.completed)

    # -----------------------------------------------------------------
    def test_many_to_many_relationship(self):
        """Test linking items to lists"""
        self.todo_list.items.add(self.item)
        self.assertEqual(self.todo_list.items.count(), 1)
        self.assertEqual(self.item.lists.count(), 1)


# =================================================================
# =================================================================
class ItemVersioningTest(TestCase):

    # -----------------------------------------------------------------
    def test_version_increment(self):
        """Test that versions increment numbers correctly"""
        item = Items.objects.create(title="Build Deck", version="1.0.9")
        next_v = item.get_next_version()
        self.assertEqual(next_v, "1.0.10")

    # -----------------------------------------------------------------
    def test_version_increment_non_numeric(self):
        """Test incrementing a version that doesn't end in a number"""
        item = Items.objects.create(title="Build Deck", version="v-alpha")
        next_v = item.get_next_version()
        self.assertEqual(next_v, "v-alpha.1")
