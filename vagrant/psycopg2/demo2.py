import psycopg2

conn = psycopg2.connect('dbname=fyyur '
                        'user=postgres '
                        'password=password')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS table1;')
cur.execute('''
            CREATE TABLE table1 (
            id INTEGER PRIMARY KEY,
            completed BOOLEAN NOT NULL DEFAULT False);
            ''')

SQL = 'INSERT INTO table1 (id, completed) VALUES (%s, %s);'
data = (1, True)
cur.execute(SQL, data)

SQL = 'INSERT INTO table1 (id, completed) VALUES (%(id)s, %(completed)s);'
data = {'id': 2,
        'completed': False}
cur.execute(SQL, data)

conn.commit()
conn.close()
cur.close()
