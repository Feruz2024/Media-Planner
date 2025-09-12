import psycopg

conn = psycopg.connect(host='localhost', user='postgres', password='Fera2014')
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute('CREATE DATABASE "Media Planner"')
    print('Database created')
except Exception as e:
    print('Error:', e)
finally:
    cur.close()
    conn.close()
