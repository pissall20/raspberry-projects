import datetime
import time

import psutil

from cpu.utils import get_ip

IP_ADDRESS = get_ip()

"""
CPU
"""
n_cpu = psutil.cpu_count()

cpu_ids = [f"cpu_{id}" for id in range(1, n_cpu + 1)]

total_cpu_usage_time = psutil.cpu_times()
all_cpu_usage_time = list(
    map(
        lambda x, y: {"id": y, "user": x.user, "system": x.system, "idle": x.idle},
        psutil.cpu_times(percpu=True),
        cpu_ids,
    )
)

total_cpu_usage_percent = psutil.cpu_percent()
all_cpu_usage_percent_dict = {
    k: v for k, v in zip(cpu_ids, psutil.cpu_percent(percpu=True))
}

load_avg_dict = {
    k: v
    for k, v in zip(
        ["1_min", "5_min", "15_min"],
        [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()],
    )
}

"""
MEMORY
"""
virtual_memory_stats = {
    k: (v / (1024 * 1024)) if k != "percent" else v
    for (k, v) in psutil.virtual_memory()._asdict().items()
}

swap_memory_stats = {
    k: (v / (1024 * 1024)) if k != "percent" else v
    for (k, v) in psutil.swap_memory()._asdict().items()
    if k != "percent"
}

"""
NETWORK
"""
net_io = dict(psutil.net_io_counters()._asdict())


def get_network_bandwidth():
    old_value = 0

    def convert_to_gbit(value):
        return value / 1024. / 1024. / 1024. * 8

    def send_stat(value):
        print("%0.3f" % convert_to_gbit(value))

    while True:
        new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        if old_value:
            send_stat(new_value - old_value)
        old_value = new_value
        time.sleep(1)


"""
STORAGE
"""
disk_usage = {
    k: (v / (1024 * 1024)) if k != "percent" else v
    for k, v in psutil.disk_usage("/")._asdict().items()
    if k != "percent"
}

"""
SENSOR
"""
try:
    temp = psutil.sensors_temperatures()
    fans = psutil.sensors_fans()
except AttributeError:
    pass

try:
    battery = psutil.sensors_battery()
except AttributeError:
    pass

"""
OTHER
"""
logged_users = list(map(lambda x: x.name, psutil.users()))

boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
    "%Y-%m-%d %H:%M:%S"
)

n_processes = len(psutil.pids())

"""
Get list of processes sorted by memory used
"""


def process_sorted_by_memory():
    """
    Get list of running processes sorted by Memory Usage
    """
    list_of_processes = []
    # Iterate over the list
    for proc in psutil.process_iter():
        try:
            # Fetch process details as dict
            pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
            pinfo['memory_used'] = proc.memory_info().vms / (1024 * 1024)
            # Append dict to list
            list_of_processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort list of dict by key vms i.e. memory usage
    list_of_process_objs = sorted(list_of_processes, key=lambda process: process['memory_used'], reverse=True)

    return list_of_process_objs
