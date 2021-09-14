import psycopg2


class Pgdb:
    def __init__(self, host = 'localhost', db = 'test', user = None, passwd = None, table = None):
        self.conn = psycopg2.connect(
            host = host,
            database = db,
            user = user,
            password = passwd
        )

        self.cursor = self.conn.cursor()
        self.table = table

    
    def createTable(self, name, query):
        self.table = name
        self.cursor.execute(f"create table {self.table}({query})")
        self.conn.commit()

    def useTable(Self, name):
        Self.table = name
        return

    def insert(self, values):
        if self.table is None:
            print('choose the table ...')
            return 

        values = tuple(values)
        # query = f"insert into {self.table} values {values};"
        self.cursor.execute("insert into details values (%s,%s,%s);", values)
        # try:
        #     self.cursor.execute(query)
        # except psycopg2.errors.UndefinedColumn:
        #     print(query)
        self.conn.commit()

    def fetchall(self):
        if self.table is None:
            print('choose the table ...')
            return 

        self.cursor.execute(f'select * from {self.table};')
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        self.cursor.close()
        self.conn.close()
        return
