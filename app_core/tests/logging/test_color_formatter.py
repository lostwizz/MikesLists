import logging
from unittest.mock import patch

from app_core.logging.color_formatter import ColorFormatter


def make_record(levelname: str, msg: str = "hello"):
    """
    Create a LogRecord with the given level.
    """
    return logging.LogRecord(
        name="test",
        level=getattr(logging, levelname, logging.INFO),
        pathname=__file__,
        lineno=10,
        msg=msg,
        args=(),
        exc_info=None,
    )


# ----------------------------------------------------------------------
# Custom log level (from CUSTOM_LOG_LEVELS)
# ----------------------------------------------------------------------
@patch("app_core.logging.color_formatter.CUSTOM_LOG_LEVELS", {
    "TRACE": (99, "\x1b[95m", "🔍"),
})
def test_color_formatter_custom_level():
    fmt = ColorFormatter("%(levelname)s %(message)s")
    record = make_record("INFO", "trace message")
    record.levelname = "TRACE"  # simulate custom level

    out = fmt.format(record)

    # Custom color + prefix applied
    assert "\x1b[95m" in out
    assert "🔍 trace message" in out
    assert out.endswith(ColorFormatter.RESET)


# ----------------------------------------------------------------------
# Standard base color fallback
# ----------------------------------------------------------------------
def test_color_formatter_standard_level():
    fmt = ColorFormatter("%(levelname)s %(message)s")
    record = make_record("WARNING", "warn message")

    out = fmt.format(record)

    assert ColorFormatter.BASE_COLORS["WARNING"] in out
    assert "WARNING warn message" in out
    assert out.endswith(ColorFormatter.RESET)


# ----------------------------------------------------------------------
# Unknown level → fallback to RESET + no prefix
# ----------------------------------------------------------------------
def test_color_formatter_unknown_level():
    fmt = ColorFormatter("%(levelname)s %(message)s")
    record = make_record("INFO", "msg")
    record.levelname = "NOPE"

    out = fmt.format(record)

    # Unknown levels fall back to RESET as the color
    assert out.startswith(ColorFormatter.RESET)
    assert out.endswith(ColorFormatter.RESET)

    # Message preserved
    assert "NOPE msg" in out

    # No prefix added
    assert "NOPE  msg" not in out  # no double-space prefix injection


# ----------------------------------------------------------------------
# Prefix modifies record.msg
# ----------------------------------------------------------------------
@patch("app_core.logging.color_formatter.CUSTOM_LOG_LEVELS", {
    "SUCCESS": (25, "\x1b[92m", "✔"),
})
def test_color_formatter_prefix_modifies_message():
    fmt = ColorFormatter("%(levelname)s %(message)s")
    record = make_record("INFO", "done")
    record.levelname = "SUCCESS"

    out = fmt.format(record)

    assert "✔ done" in out
    assert "\x1b[92m" in out
    assert out.endswith(ColorFormatter.RESET)


# ----------------------------------------------------------------------
# Ensure super().format(record) is respected
# ----------------------------------------------------------------------
def test_color_formatter_preserves_formatting():
    fmt = ColorFormatter("%(levelname)s|%(message)s")
    record = make_record("ERROR", "boom")

    out = fmt.format(record)

    assert "ERROR|boom" in out
    assert ColorFormatter.BASE_COLORS["ERROR"] in out
    assert out.endswith(ColorFormatter.RESET)
