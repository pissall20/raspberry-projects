import paho.mqtt.client as paho
import os
import json
import time
import psutil
from datetime import datetime

broker = "172.16.6.57"
port = 1883
topic = "mqtt-test"
ACCESS_TOKEN = "something-secret"

def on_publish(client, userdata, result):
    print("Following is the published data:")
    pass

client_1 = paho.Client("control_1")
client_1.on_publish = on_publish

client_1.username_pw_set(ACCESS_TOKEN)
client_1.connect(broker, port, keepalive=60)

while True:
    payload = {
        "temperature": 34,
        "humidity": 80
    }
    ret = client_1.publish(topic, json.dumps(payload))
    print(payload)
    time.sleep(3)
