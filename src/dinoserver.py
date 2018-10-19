import os
import configparser
from flask import Flask, request, g, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import threading
import time
import requests

app = Flask(__name__)
dir_name = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(dir_name, '../config.ini'))
port = int(config['server']['port'])
DATABASE = config['database']['db']


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
def close_connection(_):
    """
    Close connection after use
    :param _: exception to be ignored
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
        rows = [row[0] for row in rows]
        return list(rows)


def add_user(user_ip):
    """
    Add a user to database
    :param user_ip: ip address of the user
    :return: message
    """
    conn = None
    users = get_users_list()
    if user_ip == "127.0.0.1":
        msg = "localhost calls are ignored!"
        return msg, 304
    if (user_ip,) in users:
        msg = "%s: already connected!" % user_ip
        return msg, 304
    with app.app_context():
        try:
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


def remove_user(user_ip):
    """
    Removes a user from the database
    :param user_ip: ip of the user
    :return: message
    """
    conn = None
    msg = ""
    users = get_users_list()

    if user_ip not in users:
        msg = "%s: not connected!" % user_ip
        return msg
    with app.app_context():
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('DELETE FROM USERS WHERE IP = (?)', (user_ip,))
            conn.commit()
            msg = "%s: left" % user_ip
        except Exception as e:
            conn.rollback()
            msg = "%s: error deleting\n%s" % (user_ip, str(e))
        finally:
            conn.close()
            return msg


def poll():
    """
    Polls the current users and check if they are available
    """
    user_counter = {}
    while True:
        time.sleep(2)
        user_counter = {}
        users = get_users_list()
        for user in users:
            if not user_counter.get(user):
                user_counter[user] = 0
            url = "http://" + user + ":" + config['server']['port'] + "/join"
            try:
                requests.get(url, [], timeout=0.1)
            except Exception as e:
                user_counter[user] += 1
            if user_counter[user] > 3:
                print(remove_user(user))
                user_counter[user] = 0


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


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        path, filename = file.filename[1:].split('/')
        file.save(os.path.join('/'+path, secure_filename(filename)))
        msg = "file uploaded"
        status = 200
    else:
        msg = 'file not found'
        status = 500
    return jsonify({'message': msg}), status


if __name__ == "__main__":
    print("DINO server starting on port %d" % port)
    poller = threading.Thread(target=poll)
    poller.start()
    app.run(host="0.0.0.0", port=port)
