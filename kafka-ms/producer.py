import time
import json
import datetime
from gpiozero import CPUTemperature, LoadAverage
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    request_timeout_ms=10000
    )

while True:
    cpu = CPUTemperature()
    la = LoadAverage()
    producer.send("temp-hum", {
        "temp": cpu.temperature,
        "load": la.load_average,
        "time": str(datetime.datetime.now())
        })
    time.sleep(1)

