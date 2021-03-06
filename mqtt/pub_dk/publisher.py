import paho.mqtt.client as paho
import os
import json
import time
import numpy as np
from datetime import datetime

broker = "mqtt-broker"
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
        "temperature": np.random.randint(20, 45),
        "humidity": np.random.randint(60, 100)
    }
    ret = client_1.publish(topic, json.dumps(payload))
    print(payload)
    time.sleep(3)
