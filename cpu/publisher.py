import datetime
import json
import socket

import psutil
from kafka import KafkaProducer
from multiprocessing import Process


class KafkaStatsPublisher:
    """
    A Kafka Publisher to send data about the system statistics, gathered by using psutil package.
    """

    def __init__(self):
        self.IP_ADDRESS = self.get_ip()
        self.n_cpu = psutil.cpu_count()
        self.cpu_ids = [f"cpu_{cpu_id}" for cpu_id in range(1, self.n_cpu + 1)]
        self.kafka_conn = None

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

    def get_network_stats(self):
        net_io = dict(psutil.net_io_counters()._asdict())
        return {"net_io": net_io}

    def get_storage_stats(self):
        disk_usage = {
            k: (v / (1024 * 1024)) if k != "percent" else v
            for k, v in psutil.disk_usage("/")._asdict().items()
            if k != "percent"
        }
        return {"disk_usage": disk_usage}

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
        return {
            **cpu_stats,
            **memory_stats,
            **network_stats,
            **storage_stats,
            **misc_stats,
            "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "unique_id": self.IP_ADDRESS,
            "n_cpus": self.n_cpu,
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


stats = KafkaStatsPublisher()
from time import time

start = time()
stats.publish_to_kafka("localhost", 9092, "system_stats", keep_alive=False)
end = time()

abcd = stats.get_all_stats()

print(f"{end-start} seconds")
