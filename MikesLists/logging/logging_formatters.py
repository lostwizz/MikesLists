import sqlparse
import logging

class PrettySQLFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "sql"):
            record.sql = sqlparse.format(
                record.sql,
                reindent=True,
                keyword_case="upper"
            )
        return super().format(record)
