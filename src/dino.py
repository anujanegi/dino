from flask import Flask, request, g, jsonify
import sqlite3


DATABASE = 'users.db'
app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_users_list():
    with app.app_context():
        cur = get_db().cursor()
        cur.execute('SELECT ip FROM USERS')
        rows = cur.fetchall()
        return list(rows)


def add_user(user_ip):
    conn = None
    msg = ""
    users = get_users_list()
    if (user_ip,) in users:
        msg = "%s: already connected!" % user_ip
        return msg
    try:
        with app.app_context():
            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO USERS (ip) VALUES (?)', (user_ip,))
            conn.commit()
            msg = "%s: connected" % user_ip
    except:
        conn.rollback()
        msg = "%s: error inserting" % user_ip
    finally:
        return msg


def remove_user(user_ip):
    conn = None
    msg = ""
    users = get_users_list()
    if (user_ip,) not in users:
        msg = "%s: not connected!" % user_ip
        return msg
    try:
        with app.app_context():
            conn = get_db()
            cur = conn.cursor()
            cur.execute('DELETE FROM USERS WHERE IP = (?)', (user_ip,))
            conn.commit()
            msg = "%s: left" % user_ip
    except:
        conn.rollback()
        msg = "%s: error deleting" % user_ip
    finally:
        return msg


@app.route("/")
def hello():
    return "dino is running..."


@app.route("/join")
def join():
    if 'ip' not in request.args:
        return 'missing parameter: [ip]'
    ip = request.args['ip']
    return add_user(ip)


@app.route("/remove")
def remove():
    if 'ip' not in request.args:
        return 'missing parameter: [ip]'
    ip = request.args['ip']
    return remove_user(ip)


@app.route("/get-users")
def get_users():
    users = get_users_list()
    return jsonify(users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5321)