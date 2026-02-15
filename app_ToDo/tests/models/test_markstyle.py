import pytest
from app_ToDo.models.markstyle import MarkStyle


def test_markstyle_values_and_labels():
    assert MarkStyle.USERSCOPE.value == "user"
    assert MarkStyle.USERSCOPE.label == "User Scope"

    assert MarkStyle.TIMESCOPEUSER.value == "timeUSER"
    assert MarkStyle.TIMESCOPEUSER.label == "Time Limits Scope"

    assert MarkStyle.TIMESCOPELIST.value == "timeLIST"
    assert MarkStyle.TIMESCOPELIST.label == "Time Limits Scope"

    assert MarkStyle.THELISTSCOPE.value == "thelist"
    assert MarkStyle.THELISTSCOPE.label == "List Scope"

    assert MarkStyle.ITEMSCOPE.value == "theitem"
    assert MarkStyle.ITEMSCOPE.label == "Item Scope"
