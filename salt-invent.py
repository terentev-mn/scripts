#!/usr/bin/env python

import mysql.connector
import json
from mysql.connector import Error
import sqlite3


def connect_mysql():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='10.0.0.125',
                                       database='salt',
                                       user='salt',
                                       password='salt')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT full_ret FROM salt_returns WHERE 
                           fun='grains.items' """)
                           #AND 
                           #id='mbl-spb-193.corp.utsrus.com'""")
            row = cursor.fetchall()
            for host in row:
                parse_invent(host)
            
    except Error as e:
        print(e)

    finally:
        conn.close()

def parse_invent(row):
    str_data = ''.join((row))
    parse_data = json.loads(str_data)
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
		#print(si, type(return_data[si]))
		#if si == 'manufacturer':
		#	print(return_data['id'], return_data.get(si))
		#	continue
		si_inv.append(str(return_data.get(si)))
    update_inv(si_inv)
    return

def update_inv(inv):
    conn = sqlite3.connect('test.sqlite')
    cursor = conn.cursor()
    #print(inv)
    conn.execute('INSERT INTO inventory VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', inv)
    conn.commit()
    
    conn.close()
    return





if __name__ == '__main__':
    connect_mysql()


