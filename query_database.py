import psycopg2

class DatabaseQuery:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port = self.port,
            database=self.database,
            user=self.user,
            password=self.password

        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results

    def disconnect(self):
        self.cursor.close()
        self.conn.close()