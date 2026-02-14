from unittest.mock import MagicMock
from app_core.views.debug import DebugViewMiddleware


def test_process_view_with_valid_resolver_match(capsys):
    request = MagicMock()
    request.resolver_match.view_name = "my_view"

    mw = DebugViewMiddleware(lambda req: "OK")
    result = mw.process_view(request, view_func="func", view_args=(), view_kwargs={})

    captured = capsys.readouterr()
    assert "[DEBUG] VIEW FUNC: func | VIEW NAME: my_view" in captured.out
    assert result is None


def test_process_view_with_missing_resolver_match(capsys):
    request = MagicMock()

    # Force attribute access to raise
    class ExplodingResolver:
        def __getattr__(self, name):
            raise Exception("boom")

    request.resolver_match = ExplodingResolver()

    mw = DebugViewMiddleware(lambda req: "OK")
    result = mw.process_view(request, view_func="func", view_args=(), view_kwargs={})

    captured = capsys.readouterr()
    assert "[DEBUG] VIEW FUNC: func | VIEW NAME: None" in captured.out
    assert result is None
