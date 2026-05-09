import sqlite3

conn = sqlite3.connect("bass.db")

cursor = conn.cursor()

query = """
CREATE TABLE IF NOT EXISTS bass (
id integer primary key autoincrement,
name TEXT,
pickup TEXT,
strings INTEGER,
frets INTEGER,
score INTEGER,
price REAL,
image TEXT);
"""

cursor.execute(query)
conn.commit()
conn.close()