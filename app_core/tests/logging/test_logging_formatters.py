import logging
from app_core.logging.logging_formatters import PrettySQLFormatter

def test_pretty_sql_formatter_indents_columns():
    formatter = PrettySQLFormatter("%(sql)s")

    sql = "CREATE TABLE x (`id` INT, `name` VARCHAR(20), CONSTRAINT pk PRIMARY KEY (`id`))"

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=sql,
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    assert "    `id` INT" in formatted
    assert "    `name` VARCHAR(20)" in formatted
    assert "    CONSTRAINT pk PRIMARY KEY (`id`)" in formatted



def test_pretty_sql_formatter_skips_blank_lines():
    formatter = PrettySQLFormatter("%(sql)s")

    sql = "SELECT 1;\n\nSELECT 2;"  # <-- blank line in the middle

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=sql,
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    # The blank line should be skipped, so only two lines remain
    assert "SELECT 1;" in formatted
    assert "SELECT 2;" in formatted


def test_pretty_sql_formatter_skips_empty_column_line():
    formatter = PrettySQLFormatter("%(sql)s")

    # Note the ", ," which produces an empty column after splitting
    sql = "CREATE TABLE x (`id` INT, , `name` VARCHAR(20))"

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=sql,
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    # The empty column line should be skipped by the `continue`
    assert "`id` INT" in formatted
    assert "`name` VARCHAR(20)" in formatted
