from unittest.mock import patch
from django.db.utils import OperationalError
import app_core.services.status_service as status_service

@patch("app_core.services.status_service.connections")
def test_collect_checks_database_operational_error(mock_connections):
    # Make connections["default"].cursor() raise OperationalError
    mock_connections.__getitem__.return_value.cursor.side_effect = OperationalError("DB down")

    checks = status_service.collect_checks()

    db_check = next(c for c in checks if c.name == "Database connectivity")
    assert db_check.status == "fail"
    assert "DB down" in db_check.message



from unittest.mock import patch, MagicMock
from django.db.utils import OperationalError
import app_core.services.status_service as status_service

@patch("app_core.services.status_service.connections")
@patch("app_core.services.status_service.run")
def test_collect_checks_migrations_fail(mock_run, mock_connections):
    # Prevent real DB access
    mock_connections.__getitem__.return_value.cursor.return_value = None

    # Simulate migrations command failure
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "boom"

    checks = status_service.collect_checks()
    mig = next(c for c in checks if c.name == "Migrations")

    assert mig.status == "fail"
    assert mig.message == "boom"


@patch("app_core.services.status_service.connections")
@patch("app_core.services.status_service.run")
def test_collect_checks_disk_ok(mock_run, mock_connections):
    # Prevent real DB access
    mock_connections.__getitem__.return_value.cursor.return_value = None

    # First call: migrations
    mig = MagicMock(returncode=0, stdout="[X] 0001\n")
    # Second call: disk
    disk = MagicMock(returncode=0, stdout="Filesystem\n/dev/sda1 10G 5G 5G 50% /")
    # Third call: load
    load = MagicMock(returncode=0, stdout="0.10 0.20 0.30")
    # Fourth call: memory
    mem = MagicMock(returncode=0, stdout="Mem:\n 1G 500M 500M")

    mock_run.side_effect = [mig, disk, load, mem]

    checks = status_service.collect_checks()
    disk_check = next(c for c in checks if c.name == "Disk on /")

    assert disk_check.status == "ok"
    assert "used" in disk_check.message



@patch("app_core.services.status_service.net.get_interface_ips")
def test_get_interfaces(mock_fn):
    mock_fn.return_value = {"eth0": ["192.168.1.10"]}
    result = status_service.get_interfaces()
    assert result == {"eth0": ["192.168.1.10"]}
    mock_fn.assert_called_once()


@patch("app_core.services.status_service.net.get_host_identity")
def test_get_host_identity(mock_fn):
    mock_fn.return_value = {"hostname": "mypi", "ip": "10.0.0.9"}
    result = status_service.get_host_identity()
    assert result["hostname"] == "mypi"
    assert result["ip"] == "10.0.0.9"
    mock_fn.assert_called_once()


@patch("app_core.services.status_service.ip.get_client_ip")
def test_get_client_ip(mock_fn):
    mock_fn.return_value = "203.0.113.5"
    fake_request = object()  # anything works, it's passed through
    result = status_service.get_client_ip(fake_request)
    assert result == "203.0.113.5"
    mock_fn.assert_called_once_with(fake_request)


def test_get_remote_ip():
    class FakeReq:
        META = {"REMOTE_ADDR": "198.51.100.77"}

    req = FakeReq()
    result = status_service.get_remote_ip(req)
    assert result == "198.51.100.77"


def test_get_remote_ip_unknown():
    class FakeReq:
        META = {}

    req = FakeReq()
    result = status_service.get_remote_ip(req)
    assert result == "unknown"
