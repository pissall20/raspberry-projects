import datetime
import json
import socket

import psutil
from kafka import KafkaProducer


class KafkaStatsPublisher:
    """
    A Kafka Publisher to send data about the system statistics, gathered by using psutil package.
    """

    def __init__(self):
        self.IP_ADDRESS = self.get_ip()
        self.n_cpu = psutil.cpu_count()
        self.cpu_ids = [f"cpu_{cpu_id}" for cpu_id in range(1, self.n_cpu + 1)]
        self.kafka_conn = None

        # For network bandwidth
        self.processed_bytes = 0

    def kafka_connection(self, ip_address, port):
        if not self.kafka_conn:
            producer = KafkaProducer(
                bootstrap_servers=f"{ip_address}:{port}",
                value_serializer=lambda x: json.dumps(x).encode("utf-8"),
                request_timeout_ms=10000,
            )
            self.kafka_conn = producer
        return self.kafka_conn

    def get_cpu_stats(self):
        total_cpu_usage_time = dict(psutil.cpu_times()._asdict())
        per_cpu_usage_time = list(
            map(
                lambda x, y: {
                    "id": y,
                    "user": x.user,
                    "system": x.system,
                    "idle": x.idle,
                },
                psutil.cpu_times(percpu=True),
                self.cpu_ids,
            )
        )

        total_cpu_usage_percent = psutil.cpu_percent()
        per_cpu_usage_percent_dict = [
            {"id": cpu_id, "percent": percent}
            for cpu_id, percent in zip(self.cpu_ids, psutil.cpu_percent(percpu=True))
        ]

        load_avg_dict = {
            k: v
            for k, v in zip(
                ["min_1", "min_5", "min_15"],
                [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()],
            )
        }

        return {
            "total_cpu_usage_time": total_cpu_usage_time,
            "total_cpu_usage_percent": total_cpu_usage_percent,
            "per_cpu_usage_time": per_cpu_usage_time,
            "per_cpu_usage_percent": per_cpu_usage_percent_dict,
            "load_avg": load_avg_dict,
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
            "swap_memory": swap_memory_stats,
        }

    @staticmethod
    def convert_to_gbit(value):
        return round(value / 1024. / 1024. / 1024. * 8, 3)

    def get_network_bandwidth(self):
        new_reading = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        if self.processed_bytes:
            bandwidth = self.convert_to_gbit(new_reading - self.processed_bytes)
            return bandwidth
        self.processed_bytes = new_reading
        return self.processed_bytes

    def get_network_stats(self):
        return {"net_io": self.get_network_bandwidth()}

    def get_storage_stats(self):
        disk_usage = {
            k: (v / (1024 * 1024)) if k != "percent" else v
            for k, v in psutil.disk_usage("/")._asdict().items()
            if k != "percent"
        }
        return {"disk_usage": disk_usage}

    def get_process_sorted_by_memory(self, top_n):
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
        if top_n:
            list_of_process_objs = list_of_process_objs[:top_n]
        return list_of_process_objs

    def get_misc_stats(self):
        logged_users = list(map(lambda x: x.name, psutil.users()))
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        n_processes = len(psutil.pids())
        return {
            "logged_users": logged_users,
            "boot_time": boot_time,
            "n_processes": n_processes,
        }

    def get_all_stats(self):
        cpu_stats = self.get_cpu_stats()
        memory_stats = self.get_memory_stats()
        network_stats = self.get_network_stats()
        storage_stats = self.get_storage_stats()
        misc_stats = self.get_misc_stats()
        process_stats = self.get_process_sorted_by_memory(top_n=10)
        return {
            **cpu_stats,
            **memory_stats,
            **network_stats,
            **storage_stats,
            **misc_stats,
            "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unique_id": self.IP_ADDRESS,
            "n_cpus": self.n_cpu,
            "processes_by_mem": process_stats
        }

    def publish_to_kafka(self, ip_address, port, topic, keep_alive=True):
        kafka_conn = self.kafka_connection(ip_address, port)
        while keep_alive:
            kafka_conn.send(topic, self.get_all_stats())
            psutil.time.sleep(1)

        kafka_conn.send(topic, self.get_all_stats())
        return

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(("1.0.0.1", 1))
            IP = s.getsockname()[0]
        except:
            IP = "127.0.0.1"
        finally:
            s.close()
        return IP
