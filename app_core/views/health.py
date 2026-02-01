#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
health.py
app_core.health
/srv/django/MikesLists_dev/app_core/health.py



    this file will return a json string which will let you know that:
        - the database connection is good
        - the database is connecting to the correct database (.i.e. MikesLists_dev )
        - checks disk available (storage)



"""
__version__ = "0.0.0.000025-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-31 19:53:26"
###############################################################################

import shutil
import time
import psutil
import os
import subprocess
import threading
import re
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
from dataclasses import dataclass, asdict


@dataclass
class CheckResult:
    name: str
    status: str  # "ok", "warn", "fail", 'unknown'
    message: str
    raw_value: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    def to_dict(self):
        return asdict(self)




def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if abs(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n




def health(request):
    """
    Detailed health check returning a status list for all core components.
    """


    checks: list[CheckResult] = []

    # Start the clock
    start_time = time.perf_counter()

    # 2. Raspberry Pi Voltage/Throttling Check
    # This command returns a hex code; 0x0 means everything is fine.
    try:
        throttle_cmd = subprocess.check_output(['vcgencmd', 'get_throttled']).decode()
        chk = 'ok' if '0xe0000' in throttle_cmd else 'power_issue'
        checks.append(CheckResult(name = 'throttling', status =chk, message= '', raw_value = throttle_cmd))
    except Exception:
        # checks['throttling'] = 'n/a (non-pi)'
        checks.append(CheckResult(name = 'throttling', status ='warn', message ='n/a (non-pi)', raw_value = throttle_cmd))

    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
        temp_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", temp)[0])
        chk = "ok" if temp_val <= 80 else "warn" if temp_val <= 100 else "hot"
        checks.append(CheckResult(name = 'measure temp', status  = chk, message=str(temp_val), raw_value = temp))
    except Exception as e:
        checks.append(CheckResult(name = 'measure temp', status  = 'fail', message=str(e), raw_value = temp))

    try:
        v_raw = subprocess.check_output(['vcgencmd', 'measure_volts']).decode().strip()
        v_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", v_raw)[0])
        chk = "ok" if v_val >= 0.85 else "warn" if v_val >= 0.80 else "fail"
        checks.append(CheckResult(name = 'measure_volts', status  = chk, message=str(v_val), raw_value = v_raw))
    except Exception as e:
        checks.append(CheckResult(name = 'measure_volts', status  = 'fail', message=str(e), raw_value = v_raw))

    try:
        gpu =subprocess.check_output(['vcgencmd', 'get_mem gpu']).decode()
        g = int(re.findall(r"[-+]?\d*\.\d+|\d+", gpu)[0])
        chk = 'ok' if g>=4 else 'fail'
        checks.append(CheckResult(name = 'gpu mem', status  = chk, message=str(g), raw_value = gpu))
    except Exception as e:
        checks.append(CheckResult(name = 'gpu mem', status  = 'fail', message=str(e), raw_value = gpu))

    try:
        arm =subprocess.check_output(['vcgencmd', 'get_mem arm']).decode()
        a = int(re.findall(r"[-+]?\d*\.\d+|\d+", arm)[0])
        chk = 'ok' if a>=1000 else 'fail'
        checks.append(CheckResult(name = 'arm mem', status  = chk, message=str(a), raw_value = arm))
    except Exception as e:
        checks.append(CheckResult(name = 'arm mem', status  = 'unknown', message=tr(e), raw_value = arm))

    try:
        reloc =subprocess.check_output(['vcgencmd', 'get_mem reloc']).decode()
        r =  int(re.findall(r"[-+]?\d*\.\d+|\d+", reloc)[0])
        chk = "ok" if r in (4, 8) else "fail"
        checks.append(CheckResult(name = 'gpu reloc', status  = 'FAIL', message=r, raw_value = reloc))
    except Exception as e:
        checks.append(CheckResult(name = 'gpu reloc', status  = 'unknown', message=str(e), raw_value = reloc))


    # 1. Check Database
    try:
        db_conn = connections['default']
        current_db = db_conn.settings_dict.get('NAME', 'unknown')
        env_name = getattr(settings, 'ENV_NAME', 'unknown')

        # Logic check: Does the DB name match our expected environment?
        if env_name.lower() in current_db.lower():
            # Check if connection is actually alive
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()[0]

            checks.append(CheckResult(name = 'database', status  = 'ok', message=' select 1', raw_value = str(result)))
        else:
            checks.append(CheckResult(name = 'database', status  = 'fail', message='bad env', raw_value = str(result)))

    except Exception as e:
        checks.append(CheckResult(name = 'database', status  = 'fail', message='exception', raw_value = str(result)))

    #  Check Disk Space (Threshold: 100MB)
    # Using getattr for the path allows you to change it in settings.py if needed
    try:
        disk_path = getattr(settings, 'HEALTH_CHECK_DISK_PATH', '/')
        _, _, free = shutil.disk_usage(disk_path)
        free_mb = free // (1024 * 1024)
        # free_gb = free_mb //(1024)
        chk = 'ok' if free_mb > 100 else f'low_space_{free_mb}MB'
        checks.append(CheckResult(name = 'storage', status  = chk, message=bytes2human(free)+ ' free', raw_value = bytes2human(free)))
    except Exception as e:
        checks.append(CheckResult(name = 'storage', status  = 'fail', message=str(e), raw_value = bytes2human(free)))

    #  RAM Check (New)
    try:
        memory = psutil.virtual_memory()
        chk = 'ok' if memory.percent < 85 else 'high_usage'
        checks.append(CheckResult(name = 'ram status', status  = chk, message='', raw_value = str(memory)))
    except Exception as e:
        checks.append(CheckResult(name = 'ram status', status  = 'fail', message=str(e), raw_value = bytes2human(memory)))

    # CPU Check (New - 1 second average)
    cpu_usage = psutil.cpu_percent(interval=1)
    chk = 'ok' if cpu_usage < 90 else 'stressed'
    checks.append(CheckResult(name = 'cpu usage', status  = chk, message='', raw_value = str(cpu_usage)))


    # CPU Temperature (Raspberry Pi specific)
    try:
        # psutil.sensors_temperatures() returns a dict
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for t in entries:
                label = t.label or name

                if 'Composite' in label:
                    label += ' (nvme)'
                current = t.current

                # classify using your 3‑range logic
                status = "ok" if current <= 80 else "warn" if current <= 83 else "hot"

                checks.append(
                    CheckResult(
                        name=f"temp_{label}",
                        status=status,
                        message=str(current),
                        raw_value=str(t)
                    )
                )
    except Exception as e:
        checks.append(CheckResult(name = 'rp1_adc', status  = 'fail', message= str(e),
                            raw_value = str(temps)))

    # Check for Zombie Processes
    zombie_list = [p for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_ZOMBIE]
    # checks['zombies'] = len(zombie_list)
    chk = 'ok' if len(zombie_list) <= 1 else 'warn'
    checks.append(CheckResult(name = 'zombi processes', status  = chk, message=str(len(zombie_list)), raw_value = str(zombie_list)))

    # Check for I/O Wait (Wait percentage)
    # On Linux, this is the 4th value in cpu_times_percent
    try:
        iwait = psutil.cpu_times_percent().iowait
        chk = 'ok' if 0 == iwait else 'fail'
        checks.append(CheckResult(name = 'i/o wait percent', status  = chk, message='', raw_value = str(iwait)))
    except AttributeError:
        # checks['io_wait'] = 0 # Fallback for non-Linux or old versions
        checks.append(CheckResult(name = 'i/o wait percent', status  = 'fail', message='exception', raw_value = str(iwait)))


    #  Hardware Metrics
    memory = psutil.virtual_memory()
    memory_usage = f"{memory.percent}%"
    chk = 'ok' if memory.percent < 80 else 'warn'
    checks.append(CheckResult(name = 'virtual memory', status  = chk, message='', raw_value = str(memory)))

    cpu_load = psutil.cpu_percent()
    chk = 'ok' if cpu_load < 24 else 'warn'
    checks.append(CheckResult(name = 'cpu load', status  = chk, message='', raw_value = str(cpu_load) ))

    # Active Django/Python Threads
    active_threads = threading.active_count()
    chk = 'ok' if active_threads< 50 else 'warn'
    checks.append(CheckResult(name = 'active threads', status  = chk, message='', raw_value = str(active_threads)))


    # 4. SD Card Latency Test (Write 1KB)
    try:
        io_start = time.perf_counter()
        with open('/tmp/health_test.tmp', 'wb') as f:
            f.write(os.urandom(1024))
        io_duration = (time.perf_counter() - io_start) * 1000
        #disk_latency = f"{io_duration:.2f}ms"
        chk = 'ok' if  io_duration < 100.0 else 'warn'
        checks.append(CheckResult(name = 'disk_latency', status  = chk, message='', raw_value = str(io_duration)))
        os.remove('/tmp/health_test.tmp')
    except Exception:
        checks['disk_latency'] = 'error'
        checks.append(CheckResult(name = 'disk_latency', status  = fail, message='exception', raw_value = str(io_duration)))


    # 5. Network Check (Ping Google DNS)
    try:
        # -c 1 (1 packet), -W 1 (1 second timeout)
        subprocess.check_call(['ping', '-c', '1', '-W', '1', '8.8.8.8'], stdout=subprocess.DEVNULL)
        checks.append(CheckResult(name = 'network check', status  = 'ok', message='ping google 8.8.8.8', raw_value = ''))
    except Exception:
        checks['internet'] = 'disconnected'
        checks.append(CheckResult(name = 'network check', status  = 'fail', message='FAILED to ping google 8.8.8.8', raw_value = ''))


    cpu_c = psutil.cpu_count()
    chk = 'ok' if cpu_c > 1 else 'warn'
    checks.append(CheckResult(name = 'cpu count', status  = chk, message='', raw_value = str(cpu_c) ))


    cpu_cx = psutil.cpu_count(True)
    chk = 'ok' if cpu_cx > 1 else 'warn'
    checks.append(CheckResult(name = 'cpu count hyper', status  = chk, message='', raw_value = str(cpu_cx) ))




    # Determine overall status
    # is_healthy = all(v == 'ok' for v in checks.values())
    is_healthy = all(c.status == 'ok' for c in checks)

    overall_status = 'ok' if is_healthy else 'issues_detected'

    # Calculate Latency
    duration_ms = (time.perf_counter() - start_time) * 1000

    return JsonResponse({
        'status': overall_status,
        'latency_ms': round(duration_ms, 2),
        'details':  [asdict(c) for c in checks],
        'environment': env_name,
        'host': request.META.get('HTTP_HOST', 'unknown')
    },
    status=200
    )
