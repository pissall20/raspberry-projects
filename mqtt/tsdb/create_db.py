import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

db_name = "iot_mqtt_test"

con = pg.connect(user="postgres", password="postgres", host="localhost")
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

create_db_cmd = f"CREATE DATABASE {db_name};"
cur = con.cursor()

try:
    cur.execute(create_db_cmd)
except (Exception, pg.Error) as e:
    print(e)
cur.close()
con.close()
