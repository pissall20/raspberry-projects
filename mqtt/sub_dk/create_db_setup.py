import psycopg2 as pg


class ConnectDatabase:

    def __init__(self, host, user, password, db_name=None, table_name=None):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.table_name = table_name
        self.connection = None
        self.cursor = None

        self.create_connection()
        self.create_cursor()

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

    def _create_cursor(self):
        connection = self.create_connection()
        self.cursor = connection.cursor()
        return self.cursor

    def create_cursor(self):
        if not self.cursor:
            self.cursor = self._create_cursor()
        return self.cursor

    def _create_db(self):
        """
        Creates a Postgresql database
        :return: None
        """
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        create_db_cmd = f"CREATE DATABASE {self.db_name};"

        try:
            self.cursor.execute(create_db_cmd)
        except (Exception, pg.Error) as e:
            print(e)
        self.connection.commit()

    def _create_table(self, table_name, ts_primary_key):
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
            try:
                self.cursor.execute(cmd)
                print(cmd)
            except (Exception, pg.Error, pg.DatabaseError) as e:
                print(e)
        self.connection.commit()

        get_table_list = """SELECT table_schema,table_name FROM information_schema.tables where table_schema='public' 
        ORDER BY table_schema,table_name;"""

        self.cursor.execute(get_table_list)
        tables = self.cursor.fetchall()

        for table in tables:
            print(table)

    def create_table(self, table_name, ts_primary_key):
        self._create_table(table_name, ts_primary_key)

    def stop_connection(self):
        self.connection.close()
