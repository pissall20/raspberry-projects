import socket
import time
import datetime
import json
from gpiozero import CPUTemperature, LoadAverage

cpu = CPUTemperature()
la = LoadAverage()

port = 12345

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print(err)

s.connect(("127.0.0.1", port))

while True:
    temp = cpu.temperature
    load_avg = la.load_average
    data = {
        "temperature": temp,
        "load_avg": load_avg,
        "time": str(datetime.datetime.now())
    }
    s.send(json.dumps(data))
    time.sleep(1)

