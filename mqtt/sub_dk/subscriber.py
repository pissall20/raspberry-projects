import json
from datetime import datetime

import paho.mqtt.client as paho

from .create_db_setup import ConnectDatabase

broker = "172.16.18.71"
topic = "mqtt-test"

db_params = {
    "db_name": "iot_mqtt_test",
    "host": "timescaledb",
    "user": "postgres",
    "password": "postgres",
    "db_table_name": "temp_humidity"
}

time_pk = "datetime"
table_name = "temp_hum"

db_conn = ConnectDatabase(**db_params)
db_conn.create_table(time_pk, table_name)


def on_message(client, userdata, message):
    print("Recieved data is:")
    print(json.loads(message.payload))
    recv_data = json.loads(message.payload)
    recv_data['datetime'] = datetime.now()
    columns = ",".join(recv_data.keys())
    values = "VALUES({})".format(",".join(recv_data.values()))
    insert_stmt = "INSERT INTO {} ({}) {}".format(table_name, columns, values)
    cursor = db_conn.connection.cursor()
    cursor.execute(insert_stmt)


client = paho.Client("user")
client.on_message = on_message

print(f"Connecting to broker: {broker}")
client.connect(broker)

client.subscribe(topic)

while True:
    client.loop_start()
