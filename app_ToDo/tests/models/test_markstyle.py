#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
test_markstyle.py

Tests for app_ToDo.models.markstyle.MarkStyle
"""
###############################################################################

import pytest
from app_ToDo.models.markstyle import MarkStyle


def test_markstyle_values_and_labels():
    """Test that MarkStyle enum has correct values and labels"""
    assert MarkStyle.USERSCOPE == "user"
    assert MarkStyle.TIMESCOPEUSER == "timeUSER"
    assert MarkStyle.TIMESCOPELIST == "timeLIST"
    assert MarkStyle.THELISTSCOPE == "thelist"
    assert MarkStyle.ITEMSCOPE == "theitem"

    assert MarkStyle.USERSCOPE.label == "User Scope"
    assert MarkStyle.ITEMSCOPE.label == "Item Scope"


def test_markstyle_choices_set():
    """Test that MarkStyle.values contains all expected choices"""
    expected = {
        "user",
        "timeUSER",
        "timeLIST",
        "thelist",
        "theitem",
    }
    assert set(MarkStyle.values) == expected


def test_markstyle_is_text_choices():
    """Test that MarkStyle is a proper TextChoices enum"""
    from django.db import models
    assert issubclass(MarkStyle, models.TextChoices)


def test_markstyle_choices_method():
    """Test that choices() method returns proper tuples"""
    choices = MarkStyle.choices
    assert isinstance(choices, list)
    assert len(choices) == 5
    # Each choice should be a tuple of (value, label)
    assert all(isinstance(choice, tuple) and len(choice) == 2 for choice in choices)
