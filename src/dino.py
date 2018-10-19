import requests
import configparser
import os
import sqlite3
import click
import tempfile
from parser import parse
from dinoserver import add_user, remove_user


def get_base_url():
    """
    Get base url
    :return: server:port
    """
    dir_name = os.path.dirname(__file__)
    config = configparser.ConfigParser()
    config.read(os.path.join(dir_name, '../config.ini'))
    return config['server']['ip']+":"+config['server']['port']


def get_database():
    """
    Get database object
    :return: database object
    """
    dir_name = os.path.dirname(__file__)
    config = configparser.ConfigParser()
    config.read(os.path.join(dir_name, '../config.ini'))
    return sqlite3.connect(config['database']['db'])


def get_data(url, params=None, method=0):
    """
    get data from a url
    :param url: url
    :param params: parameters
    :param method: 0=GET, 1=POST
    :return: json data, status code
    """
    url = "http://" + url
    r = None
    if method == 0:
        try:
            r = requests.get(url, params, timeout=0.1)
        except Exception as e:
            return {'error': str(e)}, 400
    elif method == 1:
        try:
            r = requests.post(url, params)
        except Exception as e:
            return {'error': str(e)}, 400
    else:
        return r
    return r.text, r.status_code


def get_users_list():
    """
    :return: get users list
    """
    cur = get_database().cursor()
    cur.execute('SELECT ip FROM USERS')
    rows = cur.fetchall()
    rows = [row[0] for row in rows]
    return list(rows)


def check_server():
    """
    Check if the server is up
    :return:
    """
    data, status = get_data(get_base_url())
    if status == 200:
        return True
    return False


@click.group()
def cli():
    """Command line for dino"""
    pass


@cli.command()
def init():
    """Initialize the network and login"""
    """
    Logging in requires the following:
        1. Tell every node that you are here
        2. Update your own host file
        3. Exchange keys with new nodes
    """
    if not check_server():
        click.echo("Dino server is not running currently.")
        click.echo("Start the server and retry.")
        return
    # ping everyone
    print("Scanning network...")
    counter = 0
    for i in range(0, 256):
        my_ip, port = get_base_url().split(":")
        new_url = ".".join(my_ip.split('.')[0:3]) + "." + str(i) + ":" + port
        if new_url == get_base_url():
            continue
        data, status = get_data(new_url+"/join")
        if status in (201, 304):
            # active node
            add_user(new_url.split(":")[0])
            counter += 1
    print("Scan complete. Found %d node(s)." % counter)


@cli.command()
def listall():
    """Print the list of IPs connected"""
    users = get_users_list()
    click.echo("Total IPs connected: %d" % len(users))
    for user in users:
        click.echo(user)


@cli.command()
def reset():
    """Reset the connected users"""
    users = get_users_list()
    for user in users:
        click.echo(remove_user(user))
    click.echo("Reset successful.")


@cli.command()
@click.argument('filename')
def mpirun(filename):
    """Run MPI files"""
    # configure
    dir_name = os.path.dirname(__file__)
    config = configparser.ConfigParser()
    config.read(os.path.join(dir_name, '../config.ini'))
    # create temp file
    print("Compiling...")
    tfile = tempfile.NamedTemporaryFile('w+', delete=False)
    tfile.write(parse(filename))
    print("File saved as: %s" % tfile.name)
    # synchronize
    print("Synchronizing...")
    upload_dict = {'file': (tfile.name, tfile, '', {'Expires': '0'})}
    users = get_users_list()
    for user in users:
        requests.post("http://%s:5321/upload" % user, files=upload_dict)
    users.append(config['server']['ip'])
    tfile.close()
    # run
    print("Running...")
    user_string = ",".join(users)
    command = "mpirun.openmpi -np %d -H %s python3 %s" % (len(users), user_string, tfile.name)
    print(command)
    os.system(command)


if __name__ == "__main__":
    cli()
