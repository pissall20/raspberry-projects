import psycopg2 as pg

db_name = "iot_mqtt_test"
table_name = "temp_hum"

connection = pg.connect(user="postgres", password="postgres", database=db_name, host="localhost")
cursor = connection.cursor()

create_table_cmd = f"""CREATE TABLE IF NOT EXISTS {table_name} (
datetime timestamp PRIMARY KEY,
temperature double precision,
humidity double precision
);
"""

cursor.execute(create_table_cmd)
connection.commit()

sqlGetTableList = "SELECT table_schema,table_name FROM information_schema.tables where table_schema='public' ORDER BY table_schema,table_name;"

cursor.execute(sqlGetTableList)
tables = cursor.fetchall()

for table in tables:
    print(table)
