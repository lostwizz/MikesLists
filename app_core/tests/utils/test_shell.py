import subprocess
from unittest.mock import patch, MagicMock

import app_core.utils.shell as shell


def test_run_calls_subprocess_run():
    mock_proc = MagicMock()
    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        result = shell.run(["echo", "hi"], timeout=5)

    mock_run.assert_called_once_with(
        ["echo", "hi"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5,
    )
    assert result is mock_proc


def test_run_shell_calls_subprocess_run_with_shell_true():
    mock_proc = MagicMock()
    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        result = shell.run_shell("echo hi", timeout=3)

    mock_run.assert_called_once_with(
        "echo hi",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=3,
    )
    assert result is mock_proc


def test_run_checked_calls_subprocess_run_with_check_true():
    mock_proc = MagicMock()
    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        result = shell.run_checked(["ls", "-l"], timeout=2)

    mock_run.assert_called_once_with(
        ["ls", "-l"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=2,
        check=True,
    )
    assert result is mock_proc
