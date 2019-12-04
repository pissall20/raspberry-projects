import psycopg2 as pg


class ConnectDatabase:

    def __init__(self, host, user, password, db_name=None, table_name=None):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.table_name = table_name
        self.connection = self.create_connection()

    def _create_connection(self):
        connection = pg.connect(
            user=self.user,
            host=self.host,
            password=self.password,
            database=self.db_name
        )
        return connection

    def create_connection(self):
        if not self.connection:
            self.connection = self._create_connection()
        return self.connection

    def _create_db(self):
        """
        Creates a Postgresql database
        :return: None
        """
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        psql_conn = pg.connect(
            user=self.user,
            host=self.host,
            password=self.password
        )
        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        create_db_cmd = f"CREATE DATABASE {self.db_name};"
        psql_cursor = psql_conn.cursor()

        try:
            psql_cursor.execute(create_db_cmd)
        except (Exception, pg.Error) as e:
            print(e)
        psql_cursor.close()
        psql_conn.close()

    def _create_table(self, ts_primary_key, table_name):
        connection = self.create_connection()

        cursor = connection.cursor()

        create_table_cmd = f"""CREATE TABLE IF NOT EXISTS {table_name} (
        {ts_primary_key} timestamp PRIMARY KEY,
        temperature double precision,
        humidity double precision
        );
        """
        commands = (
            create_table_cmd,
            f"SELECT create_hypertable('{table_name}', '{ts_primary_key}');"
        )
        for cmd in commands:
            cursor.execute(cmd)
        connection.commit()

        get_table_list = """SELECT table_schema,table_name FROM information_schema.tables where table_schema='public' 
        ORDER BY table_schema,table_name;"""

        cursor.execute(get_table_list)
        tables = cursor.fetchall()

        for table in tables:
            print(table)

    def create_table(self, ts_primary_key, table_name):
        self.create_table(ts_primary_key, table_name)
