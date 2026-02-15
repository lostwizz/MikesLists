from app_ToDo.models.visibiliy import MarkStyle


def test_visibility_markstyle_values_and_labels():
    assert MarkStyle.GLOBAL.value == "global"
    assert MarkStyle.GLOBAL.label == "Global Visibility"

    assert MarkStyle.USER.value == "user"
    assert MarkStyle.USER.label == "User Visibility"

    assert MarkStyle.GROUPS.value == "group"
    assert MarkStyle.GROUPS.label == "Group(s) Visibility"
