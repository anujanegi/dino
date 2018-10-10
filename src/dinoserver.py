import os
import configparser
from flask import Flask, request, g, jsonify
import sqlite3

DATABASE = None
app = Flask(__name__)


def get_db():
    """
    get database instance
    :return: database object
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    """
    Close connection after use
    :param exception: to be ignored
    :return: None
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_users_list():
    """
    Get users from database
    :return: list of users
    """
    with app.app_context():
        cur = get_db().cursor()
        cur.execute('SELECT ip FROM USERS')
        rows = cur.fetchall()
        return list(rows)


def add_user(user_ip):
    """
    Add a user to database
    :param user_ip: ip address of the user
    :return: message
    """
    conn = None
    users = get_users_list()
    if (user_ip,) in users:
        msg = "%s: already connected!" % user_ip
        return msg, 304
    try:
        with app.app_context():
            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO USERS (ip) VALUES (?)', (user_ip,))
            conn.commit()
            msg = "%s: connected" % user_ip
            return msg, 201
    except Exception as e:
        conn.rollback()
        msg = "%s: error inserting\n%s" % (user_ip, str(e))
        return msg, 500


"""
Routes
"""


@app.route("/")
def hello():
    users = get_users_list()
    return jsonify(users), 200


@app.route("/join")
def join():
    ip = request.remote_addr
    msg, status = add_user(ip)
    print(ip)
    return jsonify({'message': msg}), status


if __name__ == "__main__":
    dir_name = os.path.dirname(__file__)
    config = configparser.ConfigParser()
    config.read(os.path.join(dir_name, '../config.ini'))
    port = int(config['server']['port'])
    DATABASE = config['database']['db']
    print("DINO server starting on port %d" % port)
    app.run(host="0.0.0.0", port=port)
