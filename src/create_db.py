import sqlite3
import configparser
import os


dir_name = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(dir_name, '../config.ini'))

with sqlite3.connect(config['database']['db']) as conn:
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE USERS (IP TEXT NOT NULL UNIQUE)')