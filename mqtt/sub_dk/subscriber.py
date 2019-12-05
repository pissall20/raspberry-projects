import json
from datetime import datetime

import paho.mqtt.client as paho
from create_db_setup import ConnectDatabase

broker = "172.16.18.71"
topic = "mqtt-test"

db_params = {
    "db_name": "iot_mqtt_test",
    # "host": "timescaledb",
    "host": "localhost",
    "user": "postgres",
    "password": "postgres",
    "table_name": "temp_humidity"
}

time_pk = "datetime"
# table_name = "temp_hum"

db_conn = ConnectDatabase(**db_params)
db_conn.create_table(db_params.get("table_name"), time_pk)


def on_message(client, userdata, message):
    print("Recieved data is:")
    print(json.loads(message.payload))
    recv_data = json.loads(message.payload)

    insert_stmt = "INSERT INTO temp_humidity (temperature,humidity,datetime) VALUES (%s,%s,%s)"
    data = (recv_data["temperature"], recv_data["humidity"], datetime.now())
    cursor = db_conn.connection.cursor()
    cursor.execute(insert_stmt, data)
    db_conn.connection.commit()


client = paho.Client("user")
client.on_message = on_message

print(f"Connecting to broker: {broker}")
client.connect(broker)

client.subscribe(topic)

while True:
    client.loop_start()
