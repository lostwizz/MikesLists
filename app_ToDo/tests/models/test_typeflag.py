from app_ToDo.models.typeflag import TypeFlags


def test_typeflags_values_and_labels():
    assert TypeFlags.CHECKMARK.value == "CHECKMARK"
    assert TypeFlags.CHECKMARK.label == "Checkmark"

    assert TypeFlags.RADIO.value == "RADIO"
    assert TypeFlags.RADIO.label == "Radio Buttons"

    assert TypeFlags.MULTICHOICE.value == "MULTICHOICE"
    assert TypeFlags.MULTICHOICE.label == "Multi-Choice"

    assert TypeFlags.HYPERLINK.value == "HYPERLINK"
    assert TypeFlags.HYPERLINK.label == "Hyperlink"
