import sqlite3

with sqlite3.connect('users.db') as conn:
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE USERS (IP TEXT NOT NULL UNIQUE)')