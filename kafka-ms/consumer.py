import json
from kafka import KafkaConsumer

consumer = KafkaConsumer("temp-hum",
                         bootstrap_servers="localhost:9092",
                         value_deserializer=lambda x: json.loads(x.decode("ascii"))
                         )

for msg in consumer:
    print(msg.value)
    