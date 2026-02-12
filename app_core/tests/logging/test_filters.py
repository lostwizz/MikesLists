import logging
from app_core.logging.filters import ExcludeLevelFilter


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
# Test: filter excludes specified levels
# ----------------------------------------------------------------------
def test_exclude_level_filter_excludes_levels():
    flt = ExcludeLevelFilter(levels_to_exclude=["DEBUG", "WARNING"])

    rec_debug = make_record("DEBUG")
    rec_warning = make_record("WARNING")
    rec_info = make_record("INFO")

    assert flt.filter(rec_debug) is False
    assert flt.filter(rec_warning) is False
    assert flt.filter(rec_info) is True


# ----------------------------------------------------------------------
# Test: default constructor (no exclusions)
# ----------------------------------------------------------------------
def test_exclude_level_filter_default_allows_all():
    flt = ExcludeLevelFilter()  # no levels excluded

    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        rec = make_record(level)
        assert flt.filter(rec) is True


# ----------------------------------------------------------------------
# Test: works with arbitrary custom level names
# ----------------------------------------------------------------------
def test_exclude_level_filter_custom_level_name():
    flt = ExcludeLevelFilter(levels_to_exclude=["CUSTOM"])

    rec = make_record("INFO")
    rec.levelname = "CUSTOM"  # simulate custom level

    assert flt.filter(rec) is False
