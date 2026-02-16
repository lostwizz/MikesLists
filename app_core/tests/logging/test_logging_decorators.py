import logging
from unittest.mock import patch, MagicMock

from app_core.logging.decorators import log_function_call


# ----------------------------------------------------------------------
# Helper: create a fake logger to capture calls
# ----------------------------------------------------------------------
class DummyLogger:
    def __init__(self):
        self.debug_calls = []
        self.error_calls = []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def error(self, msg):
        self.error_calls.append(msg)


# ----------------------------------------------------------------------
# Test: normal function call
# ----------------------------------------------------------------------
def test_log_function_call_success():
    dummy_logger = DummyLogger()

    with patch("app_core.logging.decorators.logger", dummy_logger):

        @log_function_call
        def add(a, b):
            return a + b

        result = add(2, 3)

        # Function executed correctly
        assert result == 5

        # Two debug logs: entry + return
        assert len(dummy_logger.debug_calls) == 2

        assert "Calling add(2, 3)" in dummy_logger.debug_calls[0]
        assert "add' returned 5" in dummy_logger.debug_calls[1]


# ----------------------------------------------------------------------
# Test: kwargs + argument formatting
# ----------------------------------------------------------------------
def test_log_function_call_with_kwargs():
    dummy_logger = DummyLogger()

    with patch("app_core.logging.decorators.logger", dummy_logger):

        @log_function_call
        def greet(name, title=None):
            return f"Hello {title} {name}"

        greet("Mike", title="Dr")

        assert "Calling greet('Mike', title='Dr')" in dummy_logger.debug_calls[0]


# ----------------------------------------------------------------------
# Test: exception logging + re-raise
# ----------------------------------------------------------------------
def test_log_function_call_exception():
    dummy_logger = DummyLogger()

    with patch("app_core.logging.decorators.logger", dummy_logger):

        @log_function_call
        def explode():
            raise ValueError("boom")

        try:
            explode()
        except ValueError:
            pass
        else:
            assert False, "Exception should have been re-raised"

        # Should log an error
        assert len(dummy_logger.error_calls) == 1
        assert "explode' raised error: boom" in dummy_logger.error_calls[0]


# ----------------------------------------------------------------------
# Test: wraps preserves metadata
# ----------------------------------------------------------------------
def test_log_function_call_preserves_metadata():
    @log_function_call
    def sample(x):
        """Docstring here"""
        return x

    assert sample.__name__ == "sample"
    assert sample.__doc__ == "Docstring here"
