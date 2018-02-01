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

            s = ''.join((row))
            obj = json.loads(s)

            s2 = obj['return']
            for i in s2:
                print(i, s2[i])
                if type(s2[i]) is dict:
                    for i2 in s2[i]:
                        print(i2, s2[i][i2])
                elif type(s2[i]) is list:
                    for i3 in s2[i]:
                        print(i3)
    except Error as e:
        print(e)

    finally:
        conn.close()

if __name__ == '__main__':
    connect()


