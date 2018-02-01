#!/usr/bin/env python

import mysql.connector
import json
from mysql.connector import Error


def connect():
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='10.0.0.125',
                                       database='salt',
                                       user='salt',
                                       password='salt')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT full_ret FROM salt_returns WHERE fun='grains.items'")
            row = cursor.fetchone()

            str_data = ''.join((row))
            parse_data = json.loads(str_data)

            return_data = parse_data['return']
            for data in return_data:
                print(data, return_data[data])
                if type(return_data[data]) is dict:
                    for data_dict in return_data[data]:
                        print(data_dict, return_data[data][data_dict])
                elif type(return_data[data]) is list:
                    for data_list in return_data[data]:
                        print(data_list)
    except Error as e:
        print(e)

    finally:
        conn.close()

if __name__ == '__main__':
    connect()


