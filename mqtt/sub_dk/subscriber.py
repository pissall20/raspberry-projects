import paho.mqtt.client as paho
import time
import sys
from datetime import datetime
import json
#from kafka import KafkaProducer
import psycopg2

broker = "172.16.18.71"
topic = "mqtt-test"

bootstap_server_ip = "kafka"

kafka_topic = "xyz-temp"

#producer = KafkaProducer(
#        bootstap_servers=f"{bootstrap_server_ip}:9092",
#        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
#        request_timeout_ms=10000
#    )

def on_message(client, userdata, message):
    print("Recieved data is:")
    print(json.loads(message.payload))
    recv_data = json.loads(message.payload)
    # producer.send(kafka_topic, recv_data)

client = paho.Client("user")
client.on_message = on_message

print(f"Connecting to broker: {broker}")
client.connect(broker)

client.subscribe(topic)

while True:
    client.loop_start()
