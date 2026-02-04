#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health_service.py
health_service
/srv/django/MikesLists_dev/app_core/services/health_service.py



"""
__version__ = "0.0.1.000005-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-02-03 20:38:13"
###############################################################################


import shutil
import time
import psutil
import os
import subprocess
import threading
import re
import json
import logging
import importlib


from app_core.logging.decorators import log_function_call
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
from dataclasses import dataclass, asdict

# from app_core.logging.logging import logger

from django.db import connections  # Add this line
from app_core.logging.logging import logger

from app_core.logging.logging import logger


from typing import Union

# logger.dump_all_loggers()


# =================================================================
@dataclass
class CheckResult:
    name: str
    status: str  # "ok", "warn", "fail", 'unknown'
    message: str
    raw_value: str

    # -----------------------------------------------------------------
    def to_json(self) -> str:
        return json.dumps(asdict(self))

    # -----------------------------------------------------------------
    def to_dict(self) -> dict:
        return asdict(self)


# -----------------------------------------------------------------
# @log_function_call
# -----------------------------------------------------------------
def bytes2human(n) -> str:
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'

    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if abs(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.1f%s" % (value, s)
    return "%sB" % n


# -----------------------------------------------------------------
def _safe_decode(value: Union[str, bytes]) -> str:
    if isinstance(value, bytes):
        return value.decode()
    return value


# -----------------------------------------------------------------
def run_cmd(cmd) -> str:
    raw = subprocess.check_output(cmd)
    return _safe_decode(raw)


# -----------------------------------------------------------------
def normalize_details(raw_details: dict[str, dict]) -> dict[str, CheckResult]:
    normalized: dict[str, CheckResult] = {}

    for key, data in raw_details.items():
        normalized[key] = CheckResult(
            name=data.get("name", key),
            status=data.get("status", "unknown"),
            message=data.get("message", ""),
            raw_value=data.get("raw_value", ""),
        )

    return normalized


# -----------------------------------------------------------------
def run_dynamic(module_name: str, func_name: str, *args, **kwargs):
    # logger.traceu(f"{module_name=}   {func_name=}")
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    return func(*args, **kwargs)


# -----------------------------------------------------------------
def run_health_psutil_check(name, spec) -> CheckResult:
    # logger.purple(f"<===={spec=}")
    try:
        module_name, func_name = spec["cmd"]
        output = run_dynamic(module_name, func_name)
        # logger.green(f"{output=}")

        status, message, raw_value = spec["parser"](output)
        return CheckResult(
            name=name, status=status, message=message, raw_value=raw_value
        )

    except Exception as e:
        return CheckResult(name=name, status="fail", message=str(e), raw_value="")


# -----------------------------------------------------------------
def run_health_check(name, spec) -> CheckResult:
    # logger.traces(f"{name=} {spec=}" )
    try:
        output = run_cmd(spec["cmd"])
        status, message, raw_value = spec["parser"](output)
        return CheckResult(
            name=name, status=status, message=message, raw_value=raw_value
        )

    except Exception as e:
        return CheckResult(name=name, status="fail", message=str(e), raw_value="")


# -----------------------------------------------------------------
def parse_throttling(output) -> tuple[str, str, str]:

    # THROTTLE_FLAGS = {
    #     0x1:      ("fail", "Under‑voltage detected now"),
    #     0x2:      ("fail", "ARM frequency capped now"),
    #     0x4:      ("fail", "Currently throttled"),
    #     0x8:      ("fail", "Soft temperature limit active now"),
    #     0x10000:  ("warn", "Under‑voltage has occurred"),
    #     0x20000:  ("warn", "Frequency capping has occurred"),
    #     0x40000:  ("warn", "Throttling has occurred"),
    #     0x80000:  ("warn", "Soft temperature limit has occurred"),
    # }
    THROTTLE_FLAGS = {
        0x1: ("fail", "now Under‑voltage"),
        0x2: ("fail", "ARM frequency capped now"),
        0x4: ("fail", "Currently throttled"),
        0x8: ("fail", "Soft temperature limit active now"),
        0x10000: ("warn", "pastUV"),
        0x20000: ("warn", "pastFC"),
        0x40000: ("warn", "pastTH"),
        0x80000: ("warn", "pastSTL"),
    }
    result = output
    # Expect "throttled=0x12345"
    if "=" not in result:
        return ("fail", f"unexpected output: {result}", "")

    _, hex_value = result.split("=")

    # Convert hex → int
    try:
        value = int(hex_value, 16)
    except Exception:
        return ("fail", f"invalid hex value: {hex_value}", hex_value)

    messages = []
    status = "ok"

    # Evaluate all bits
    for bit, (severity, text) in THROTTLE_FLAGS.items():
        if value & bit:
            messages.append(text)
            if severity == "fail":
                status = "fail"
            elif severity == "warn" and status != "fail":
                status = "warn"

    # No bits set → OK
    if not messages:
        messages.append("No throttling or undervoltage detected")

    return (status, ", ".join(messages), hex_value)


# -----------------------------------------------------------------
def parse_temperature(output) -> tuple[str, str, str]:
    temp_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", output)[0])
    status = "ok" if temp_val <= 80 else "warn" if temp_val <= 100 else "hot"
    return status, str(temp_val), output


# -----------------------------------------------------------------
def parse_voltage(output) -> tuple[str, str, str]:
    v_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", output)[0])
    status = "ok" if v_val >= 0.85 else "warn" if v_val >= 0.80 else "fail"
    return status, str(v_val), output


# -----------------------------------------------------------------
def parse_gpu_mem(output) -> tuple[str, str, str]:
    vgpu = int(re.findall(r"[-+]?\d*\.\d+|\d+", output)[0])
    status = "ok" if vgpu >= 4 else "fail"
    return status, str(vgpu), output


# -----------------------------------------------------------------
def parse_arm_mem(output) -> tuple[str, str, str]:
    varm = int(re.findall(r"[-+]?\d*\.\d+|\d+", output)[0])
    status = "ok" if varm >= 1000 else "fail"
    return status, str(varm), output


# -----------------------------------------------------------------
def parse_reloc_mem(output) -> tuple[str, str, str]:
    reloc = int(re.findall(r"[-+]?\d*\.\d+|\d+", output)[0])
    status = "ok" if reloc in (4, 8) else "fail"
    return status, str(reloc), output


# -----------------------------------------------------------------
def parse_iowait(output) -> tuple[str, str, str]:
    """
    0 • 	 – time spent in user mode
    1 • 	 – time spent in kernel mode
    2 • 	 – idle time
    3 • 	 – user mode with low priority
    4 • 	 – waiting for I/O
    5 • 	 – hardware interrupts
    6 • 	 – software interrupts
    7 • 	 – time stolen by hypervisor
    8 • 	 – guest OS
    9 • 	 – low‑priority guest OS
     Not all fields appear on all platforms, but the structure is consistent
    """
    iwait = output[4]
    status = "ok" if (iwait <= 0.9) else "fail"
    return status, str(iwait), output


# -----------------------------------------------------------------
def parse_virtual_mem(output) -> tuple[str, str, str]:
    virt_mem = output[0]
    status = "ok" if virt_mem < 80 else "warn"
    return status, bytes2human(virt_mem), output


# -----------------------------------------------------------------
def parse_cpu_load(output) -> tuple[str, str, str]:
    try:
        a = str(output)
        cpu = float(a)
        status = "ok" if cpu < 80.0 else "warn"
        return status, str(cpu) + "%", output
    except Exception:
        logger.exception("why")


# -----------------------------------------------------------------
def parse_threads(output) -> tuple[str, str, str]:
    # logger.yellow(f"{output=}")

    th = output
    status = "ok" if th < 20 else "warn"
    return status, str(th), output


# -----------------------------------------------------------------


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
def run_database_check() -> dict[str, CheckResult]:

    try:
        db_conn = connections["default"]
        # Check if connection is actually alive
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]

        return {
            "database": CheckResult(
                name="database", status="ok", message=" select 1", raw_value=str(result)
            )
        }
    except Exception as e:
        return {
            "database": CheckResult(
                name="database", status="fail", message=str(e), raw_value=str(result)
            )
        }


# -----------------------------------------------------------------
def run_disk_check() -> dict[str, CheckResult]:
    return {
        "storage": CheckResult(name="storage", status="fail", message="", raw_value="")
    }


# -----------------------------------------------------------------
def run_disk_check() -> dict[str, CheckResult]:
    try:
        disk_path = getattr(settings, "HEALTH_CHECK_DISK_PATH", "/")
        _, _, free = shutil.disk_usage(disk_path)
        free_mb = free // (1024 * 1024)

        status = "ok" if free_mb > 100 else f"low_space_{free_mb}MB"

        return {
            "storage": CheckResult(
                name="storage",
                status=status,
                message=f"{bytes2human(free)} free",
                raw_value=bytes2human(free),
            )
        }

    except Exception as e:
        return {
            "storage": CheckResult(
                name="storage",
                status="fail",
                message=str(e),
                raw_value="",
            )
        }


# -----------------------------------------------------------------
def run_ram_check() -> dict[str, CheckResult]:
    try:
        mem = psutil.virtual_memory()
        status = "ok" if mem.percent < 85 else "high_usage"

        return {
            "memory": CheckResult(
                name="ram status",
                status=status,
                message=str(mem.percent),
                raw_value=str(mem),
            )
        }

    except Exception as e:
        return {
            "memory": CheckResult(
                name="ram status",
                status="fail",
                message=str(e),
                raw_value="",
            )
        }


# -----------------------------------------------------------------
def run_cpu_check() -> dict[str, CheckResult]:
    try:
        cpu = psutil.cpu_percent(interval=1)
        status = "ok" if cpu < 90 else "stressed"

        return {
            "cpu_usage": CheckResult(
                name="cpu usage",
                status=status,
                message=str(cpu),
                raw_value=str(cpu),
            )
        }

    except Exception as e:
        return {
            "cpu_usage": CheckResult(
                name="cpu usage",
                status="fail",
                message=str(e),
                raw_value="",
            )
        }


# -----------------------------------------------------------------
def run_temp_sensors_check() -> dict[str, CheckResult]:
    results = {}

    try:
        temps = psutil.sensors_temperatures()

        for name, entries in temps.items():
            for t in entries:
                label = t.label or name
                if "Composite" in label:
                    label += " (nvme)"

                current = t.current
                status = "ok" if current <= 80 else "warn" if current <= 83 else "hot"

                key = f"temp_{label}"
                results[key] = CheckResult(
                    name=key,
                    status=status,
                    message=str(current),
                    raw_value=str(t),
                )

    except Exception as e:
        results["temp_sensors"] = CheckResult(
            name="temp_sensors",
            status="fail",
            message=str(e),
            raw_value="",
        )

    return results


# -----------------------------------------------------------------
def run_zombie_check() -> dict[str, CheckResult]:
    try:
        zombies = [
            p.pid
            for p in psutil.process_iter(["status"])
            if p.info["status"] == psutil.STATUS_ZOMBIE
        ]

        count = len(zombies)
        status = "ok" if count == 0 else "warn"
        msg = "No zombies found" if count == 0 else f"Found {count}: {zombies}"

        return {
            "zombie": CheckResult(
                name="zombie processes",
                status=status,
                message=msg,
                raw_value=str(zombies),
            )
        }

    except Exception as e:
        return {
            "zombie": CheckResult(
                name="zombie processes",
                status="fail",
                message=str(e),
                raw_value="",
            )
        }


# -----------------------------------------------------------------
def run_sd_latency() -> dict[str, CheckResult]:
    try:
        io_start = ""
        io_start = time.perf_counter()
        with open("/tmp/health_test.tmp", "wb") as f:
            f.write(os.urandom(1024))
        io_duration = (time.perf_counter() - io_start) * 1000
        # disk_latency = f"{io_duration:.2f}ms"
        chk = "ok" if io_duration < 100.0 else "warn"
        return {
            "sd_latency": CheckResult(
                name="sd_latency", status=chk, message="", raw_value=str(io_duration)
            )
        }
    except Exception as e:
        return {
            "sd_latency": CheckResult(
                name="sd_latency", status="fail", message=str(e), raw_value=""
            )
        }


# -----------------------------------------------------------------
def run_ping_test() -> dict[str, CheckResult]:
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "-W", "1", "8.8.8.8"], stdout=subprocess.DEVNULL
        )
        return {
            "network_check": CheckResult(
                name="network check",
                status="ok",
                message="ping google 8.8.8.8",
                raw_value="",
            )
        }
    except Exception as e:
        return {
            "network_check": CheckResult(
                name="network_check", status="fail", message=str(e), raw_value=""
            )
        }


# -----------------------------------------------------------------
# -----------------------------------------------------------------
# -----------------------------------------------------------------
CHECKS = {
    "throttling": {
        "cmd": ["vcgencmd", "get_throttled"],
        "parser": parse_throttling,
    },
    "measure_temp": {
        "cmd": ["vcgencmd", "measure_temp"],
        "parser": parse_temperature,
    },
    "measure_volts": {
        "cmd": ["vcgencmd", "measure_volts"],
        "parser": parse_voltage,
    },
    "gpu_mem": {
        "cmd": ["vcgencmd", "get_mem gpu"],
        "parser": parse_gpu_mem,
    },
    "arm_mem": {
        "cmd": ["vcgencmd", "get_mem arm"],
        "parser": parse_arm_mem,
    },
    "reloc_mem": {
        "cmd": ["vcgencmd", "get_mem reloc"],
        "parser": parse_reloc_mem,
    },
    "active_threads": {
        "cmd": ["threading", "active_count"],
        "parser": parse_threads,
    },
    "io_wait": {
        "cmd": ["psutil", "cpu_times_percent"],
        "parser": parse_iowait,
    },
    "virtual_memory": {
        "cmd": ["psutil", "virtual_memory"],
        "parser": parse_virtual_mem,
    },
    "cpu_load": {
        "cmd": ["psutil", "cpu_percent"],
        "parser": parse_cpu_load,
    },
}


# -----------------------------------------------------------------
def health_service():
    """
    Detailed health check returning a status list for all core components.
    """

    env_name = getattr(settings, "ENV_NAME", "unknown")

    # checks: list[CheckResult] = []
    checks: dict[str, CheckResult] = {}

    # Run all declarative checks
    for name, spec in CHECKS.items():
        module_name = spec["cmd"][0]

        if module_name == "psutil" or module_name == "threading":
            checks[name] = run_health_psutil_check(name, spec)
        else:
            checks[name] = run_health_check(name, spec)
        # logger.mark("")

    # Add non-command checks (database, RAM, CPU, zombies, etc.)
    checks.update(run_database_check())
    checks.update(run_disk_check())
    checks.update(run_ram_check())
    checks.update(run_cpu_check())
    checks.update(run_temp_sensors_check())
    checks.update(run_zombie_check())
    checks.update(run_sd_latency())
    checks.update(run_ping_test())

    # logger.info( f" about to exit health_services.py {checks=},   {env_name=}")

    return checks, env_name
