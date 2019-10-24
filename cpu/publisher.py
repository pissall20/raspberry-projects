import datetime
import psutil

from cpu.utils import get_ip


class StatsPublisher:
    def __init__(self):
        self.IP_ADDRESS = get_ip()
        self.n_cpu = psutil.cpu_count()
        self.cpu_ids = [f"cpu_{cpu_id}" for cpu_id in range(1, self.n_cpu + 1)]

    def get_cpu_stats(self):
        total_cpu_usage_time = psutil.cpu_times()
        per_cpu_usage_time = list(
            map(
                lambda x, y: {"id": y, "user": x.user, "system": x.system, "idle": x.idle},
                psutil.cpu_times(percpu=True),
                self.cpu_ids,
            )
        )

        total_cpu_usage_percent = psutil.cpu_percent()
        per_cpu_usage_percent_dict = {
            k: v for k, v in zip(self.cpu_ids, psutil.cpu_percent(percpu=True))
        }

        load_avg_dict = {
            k: v
            for k, v in zip(
                ["1_min", "5_min", "15_min"],
                [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()],
            )
        }

        return {
            "total_cpu_usage_time": total_cpu_usage_time,
            "total_cpu_usage_percent": total_cpu_usage_percent,
            "per_cpu_usage_time": per_cpu_usage_time,
            "per_cpu_usage_percent": per_cpu_usage_percent_dict,
            "load_avg": load_avg_dict
        }

    def get_memory_stats(self):
        virtual_memory_stats = {
            k: (v / (1024 * 1024)) if k != "percent" else v
            for (k, v) in psutil.virtual_memory()._asdict().items()
        }

        swap_memory_stats = {
            k: (v / (1024 * 1024)) if k != "percent" else v
            for (k, v) in psutil.swap_memory()._asdict().items()
            if k != "percent"
        }
        return {
            "virtual_memory": virtual_memory_stats,
            "swap_memory": swap_memory_stats
        }

    def get_network_stats(self):
        net_io = dict(psutil.net_io_counters()._asdict())
        return {
            "net_io": net_io
        }

    def get_storage_stats(self):
        disk_usage = {
            k: (v / (1024 * 1024)) if k != "percent" else v
            for k, v in psutil.disk_usage("/")._asdict().items()
            if k != "percent"
        }
        return {
            "disk_usage": disk_usage
        }

    def get_misc_stats(self):
        logged_users = list(map(lambda x: x.name, psutil.users()))
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        n_processes = len(psutil.pids())
        return {
            "logged_users": logged_users,
            "boot_time": boot_time,
            "n_processes": n_processes
        }
