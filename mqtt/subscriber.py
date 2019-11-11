import paho.mqtt.client as paho
import time
import sys
from datetime import datetime
import json

broker = "172.16.6.57"
topic = "mqtt-test"

def on_message(client, userdata, message):
    print("Recieved data is:")
    print(json.loads(message.payload))

client = paho.Client("user")
client.on_message = on_message

print(f"Connecting to broker: {broker}")
client.connect(broker)

client.subscribe(topic)

while True:
    client.loop_start()
