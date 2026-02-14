import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings

import app_core.services.health_service as hs
from app_core.services.health_service import (
    CheckResult,
    health_service,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fake_temp():
    class T:
        current = 50
    return {"cpu": [T()]}


# ---------------------------------------------------------------------------
# Disk Check
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("shutil.disk_usage", return_value=(100, 50, 200 * 1024 * 1024))
def test_check_disk_ok(_mock):
    result = hs.check_disk()
    assert result.status == "ok"
    assert "free" in result.message


# ---------------------------------------------------------------------------
# RAM Check
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("psutil.virtual_memory")
def test_check_ram_ok(mock_vm):
    mock_vm.return_value.percent = 40
    mock_vm.return_value._asdict.return_value = {"percent": 40}
    result = hs.check_ram()
    assert result.status == "ok"


@override_settings(TESTING=True)
@patch("psutil.virtual_memory")
def test_check_ram_warn(mock_vm):
    mock_vm.return_value.percent = 90
    mock_vm.return_value._asdict.return_value = {"percent": 90}
    result = hs.check_ram()
    assert result.status == "warn"


# ---------------------------------------------------------------------------
# CPU Check
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("psutil.cpu_percent", return_value=10)
def test_check_cpu_ok(_mock):
    result = hs.check_cpu()
    assert result.status == "ok"


@override_settings(TESTING=True)
@patch("psutil.cpu_percent", return_value=95)
def test_check_cpu_warn(_mock):
    result = hs.check_cpu()
    assert result.status == "warn"


# ---------------------------------------------------------------------------
# Temperature Sensors
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("psutil.sensors_temperatures", return_value=fake_temp())
def test_check_temp_ok(_mock):
    result = hs.check_temp_sensors()
    assert result.status == "ok"


@override_settings(TESTING=True)
@patch("psutil.sensors_temperatures", return_value={"cpu": []})
def test_check_temp_skip(_mock):
    result = hs.check_temp_sensors()
    assert result.status == "skip"


# ---------------------------------------------------------------------------
# Zombie Check
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("psutil.process_iter")
def test_check_zombies_ok(mock_iter):
    mock_iter.return_value = []
    result = hs.check_zombies()
    assert result.status == "ok"


@override_settings(TESTING=True)
@patch("psutil.process_iter")
def test_check_zombies_warn(mock_iter):
    class P:
        info = {"status": "zombie"}
        pid = 123
    mock_iter.return_value = [P()]
    result = hs.check_zombies()
    assert result.status == "warn"


# ---------------------------------------------------------------------------
# SD Latency
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("builtins.open", new_callable=MagicMock)
def test_check_sd_latency_ok(_mock):
    result = hs.check_sd_latency()
    assert result.status in ("ok", "warn")  # timing varies but always valid


@override_settings(TESTING=True)
@patch("builtins.open", side_effect=Exception("disk error"))
def test_check_sd_latency_fail(_mock):
    result = hs.check_sd_latency()
    assert result.status == "fail"


# ---------------------------------------------------------------------------
# Ping Check
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
def test_check_ping_test_mode():
    result = hs.check_ping()
    assert result.status == "ok"
    assert result.message == "test-mode"


# ---------------------------------------------------------------------------
# Database Check
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
@patch("django.db.connections.__getitem__", side_effect=Exception("db error"))
def test_check_database_fail(_mock):
    result = hs.check_database()
    assert result.status == "fail"


# ---------------------------------------------------------------------------
# Full Health Service
# ---------------------------------------------------------------------------

@override_settings(TESTING=True)
def test_health_service_runs_all_checks():
    results = health_service()

    # Ensure all registered checks are present
    for key in hs.CHECK_REGISTRY.keys():
        assert key in results
        assert isinstance(results[key], CheckResult)



def test_safe_run_exception():
    def bad_check():
        raise RuntimeError("boom")

    result = hs.safe_run(bad_check)

    assert isinstance(result, hs.CheckResult)
    assert result.status == "fail"
    assert result.message == "boom"
    assert result.name == "bad_check"


def test_bytes2human_fallback():
    result = hs.bytes2human(512)
    assert result == "512B"



@override_settings(TESTING=True)
@patch("psutil.sensors_temperatures", return_value=None)
def test_check_temp_sensors_none(_mock):
    result = hs.check_temp_sensors()
    assert result.status == "skip"
    assert result.message == "no sensors"

@override_settings(TESTING=True)
@patch("psutil.sensors_temperatures", return_value={})
def test_check_temp_sensors_empty_dict(_mock):
    result = hs.check_temp_sensors()
    assert result.status == "skip"
    assert result.message == "no sensors"
