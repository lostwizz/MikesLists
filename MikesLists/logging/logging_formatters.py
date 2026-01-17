import logging
import sqlparse
import re


# class PrettySQLFormatter(logging.Formatter):
#     def format(self, record):
#         raw_sql = getattr(record, "sql", record.getMessage())
#         duration = getattr(record, "duration", "0.0")

#         # 1. Standardize spacing
#         clean_sql = " ".join(raw_sql.split())

#         # 2. Add a newline before the first parenthesis to prevent horizontal drift
#         # This makes 'CREATE TABLE name' its own line and '(' start at col 0
#         clean_sql = clean_sql.replace(" (", "\n(", 1)

#         # 3. Format with sqlparse
#         formatted_sql = sqlparse.format(
#             clean_sql,
#             reindent=True,
#             indent_width=4,
#             keyword_case="upper",
#         )

#         # 4. Cleanup any lingering weirdness
#         # Ensure no line has more than 4-8 spaces of indentation
#         final_lines = []
#         for line in formatted_sql.splitlines():
#             stripped = line.lstrip()
#             if stripped:
#                 # If the line starts with a column definition or constraint, indent it
#                 if stripped.startswith("`") or stripped.startswith("PRIMARY"):
#                     final_lines.append("    " + stripped)
#                 else:
#                     final_lines.append(stripped)

#         record.sql = "\n".join(final_lines)
#         record.duration = duration

#         return super().format(record)


class PrettySQLFormatter(logging.Formatter):
    def format(self, record):
        raw_sql = getattr(record, "sql", record.getMessage())
        duration = getattr(record, "duration", "0.0")

        # 1. Collapse whitespace
        clean_sql = " ".join(raw_sql.split())

        # 2. Force a newline after the table name and BEFORE the parenthesis
        # This prevents the first column from being on the same line as CREATE TABLE
        clean_sql = clean_sql.replace(" (", "\n(", 1)

        # 3. Format with sqlparse
        formatted_sql = sqlparse.format(
            clean_sql,
            reindent=True,
            indent_width=4,
            keyword_case="upper",
        )

        final_lines = []
        for line in formatted_sql.splitlines():
            stripped = line.lstrip()
            if not stripped:
                continue

            # If line starts with a column (backtick) or constraint, give it 4 spaces
            if (
                stripped.startswith("`") or stripped.startswith("PRIMARY") or stripped.startswith("CONSTRAINT")
            ):
                final_lines.append("    " + stripped)
            # If it's the closing paren, keep it flush left or slightly indented
            elif stripped == ")":
                final_lines.append(stripped)
            else:
                final_lines.append(stripped)

        record.sql = "\n".join(final_lines)
        record.duration = duration

        return super().format(record)
