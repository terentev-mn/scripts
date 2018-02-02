#!/usr/bin/env python

import mysql.connector
import json
from mysql.connector import Error
import sqlite3


def connect():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='10.0.0.125',
                                       database='salt',
                                       user='salt',
                                       password='salt')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("""SELECT full_ret FROM salt_returns WHERE 
                           fun='grains.items' ORDER BY id LIMIT 3""")
                           #AND 
                           #id='mbl-spb-228.corp.utsrus.com'""")
            row = cursor.fetchone()
            parse_invent(row)
            
    except Error as e:
        print(e)

    finally:
        conn.close()

def parse_invent(row):
    str_data = ''.join((row))
    parse_data = json.loads(str_data)
    return_data = parse_data['return']
    
    hardware = ['cpu_model', 'num_cpus', 'mem_total', 'biosversion', 
                'biosreleasedate', 'manufacturer', 'productname', 
                'serialnumber', 'gpus', 'SSDs']
    salt_info = ['id', 'nodename', 'saltversion', 'machine_id', 
                 'kernelrelease', 'lsb_distrib_description']
    network = ['ip4_interfaces', 'hwaddr_interfaces', 'ipv4', 
               'domain', 'localhost', 'host', 'fqdn']
    hw_inv = {}
    si_inv = []
    nw_inv = {}
    #i = -1
    #for data in return_data:
    #    print(data, return_data[data])
    #    if type(return_data[data]) is dict:
    #        for data_dict in return_data[data]:
    #            print(data_dict, return_data[data][data_dict])
    #    elif type(return_data[data]) is list:
    #        for data_list in return_data[data]:
    #            print(data_list)
    for hw in hardware:
		#print(hw, str(return_data[hw]))
		hw_inv[hw] = str(return_data[hw])
    print('----------------------------')
    for si in salt_info:
		
		#print(si, type(return_data[si]))
		si_inv.append(str(return_data[si]))
		#i += 1
		#print(si_inv)
    print('----------------------------')
    for nw in network:
		#print(nw, str(return_data[nw]))
		nw_inv[nw] = str(return_data[nw])
    #print(hw_inv)
    #print(si_inv)
    #print(nw_inv)
    update_inv(si_inv)
    return

def update_inv(inv):
    conn = sqlite3.connect('test.sqlite')
    cursor = conn.cursor()
    #for item in inv.items():
    #    print(item[0], item[1])
    #    cursor.execute("INSERT INTO inventory VALUES (:key, :item)", {"key": item[0], "item": item[1]})
    #params = ['?' for item in inv.items]
    print(inv)
    #sql    = 'INSERT INTO inventory (id, nodename, saltversion, machine_id, kernelrelease, lsb_distrib_description) VALUES (%s);' % ','.join(inv.values())
    #conn.execute(sql, inv)
    
    conn.execute('INSERT INTO inventory VALUES (?,?,?,?,?,?)', inv)
    conn.commit()
    
    conn.close()
    return






if __name__ == '__main__':
    connect()


