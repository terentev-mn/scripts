#!/usr/bin/env python

import mysql.connector
import json
from mysql.connector import Error
import sqlite3


def connect_mysql(sql):
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='10.0.0.125',
                                       database='salt',
                                       user='salt',
                                       password='salt')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchall()
            for host in row:
                str_data = ''.join((host))
                parse_data = json.loads(str_data)
                #parse_invent(parse_data)
                #parse_state(parse_data)
                print(type(parse_data))
    except Error as e:
        print(e)

    finally:
        conn.close()


def parse_invent(parse_data):
    # str_data = ''.join((row))
    # parse_data = json.loads(str_data)
    return_data = parse_data['return']
    salt_info = ['id', 'nodename', 'saltversion', 'machine_id',
                 'kernelrelease', 'lsb_distrib_description',
                 'cpu_model', 'num_cpus', 'mem_total', 'biosversion',
                 'biosreleasedate', 'manufacturer', 'productname',
                 'serialnumber', 'gpus', 'SSDs', 'ip4_interfaces',
                 'hwaddr_interfaces', 'ipv4',
                 'domain', 'localhost', 'host', 'fqdn']
    si_inv = []

    for si in salt_info:
        si_inv.append(str(return_data.get(si)))
    # update_inv(si_inv)
    return si_inv


def update_inv(inv):
    conn = sqlite3.connect('test.sqlite')
    cursor = conn.cursor()
    sql = 'INSERT INTO inventory VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    conn.execute(sql, inv)
    # sql = 'INSERT INTO sorted SELECT * FROM inventory ORDER BY id'
    # conn.execute(sql)
    conn.commit()

    conn.close()
    return


def parse_state(parse_data):
    # str_data = ''.join((row))
    # parse_data = json.loads(str_data)
    # print(parse_data)
    return parse_data


sql_grains = "SELECT full_ret FROM salt_returns WHERE fun='grains.items' "
sql_states = "SELECT full_ret FROM salt_returns WHERE fun='state.apply' "
row_grains = connect_mysql(sql_grains)
row_states = connect_mysql(sql_states)
# grains = parse_invent(row_grains)
# states = parse_state(row_grains)

# update_inv(grains)
# update_sts(states)

