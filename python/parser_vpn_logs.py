#!/usr/bin/env python3

import os
import sys
import json
from signal import signal, SIGINT
"""
   Парсер-прокладка между openvpn и syslog
   Нужен потому что логи конекта могут быть не последовательными и перемешаны между собой.
   Скрипт грепает лог по конекту и парсит переменные. Результат пишет в %исходный_файл%.json

   Пример запуска:  parser_vpn_logs.py /var/log/openvpn/openvpn.log
"""

LOG_FILE = sys.argv[1]
LOCK_FILE = f"{LOG_FILE}.lock"
JSON_FILE = f"{LOG_FILE}.json"
START_CONNECT_PAT = "TCP connection established with [AF_INET]"


def get_data(last_connect: dict) -> list:
    """ Читаем лог с места последнего конекта
    если в строке дата и ip последнего конекта, то считаем что это и есть последний конект - пропускаем его.
    """
    match = False
    ret = []
    if last_connect:
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                for l in lines:
                    if not match and last_connect['TIME'] in l and last_connect['IP'] not in l:
                        match = True
                    if match and last_connect['IP'] not in l:
                        ret.append(l.strip())
        except Exception as err:
            print(f"get_data: {err}")
            print("Try change encoding to ISO-8859-1")
            with open(LOG_FILE, 'r', encoding="ISO-8859-1") as f:
                lines = f.readlines()
                for l in lines:
                    if not match and last_connect['TIME'] in l and last_connect['IP'] not in l:
                        match = True
                    if match and last_connect['IP'] not in l:
                        ret.append(l.strip())
    # после ротирования лога(новый месяц) дату не найдет, надо обрабатывать весь файл
    if not ret:
        with open(LOG_FILE, 'r', encoding="ISO-8859-1") as f:
            ret = [l.strip() for l in f.read().splitlines()]
    return ret


def get_connects(data: list) -> list:
    """ Собираем конекты
        конект это ip:port (1.1.1.1:42310)
        Возвращаем список из (конект, дата)
    """

    ret = [(d[d.index('[AF_INET]') + 9:], d[:19]) for d in data if START_CONNECT_PAT in d]
    return ret


def fill_connects(connects: list):
    """ Заполняем конекты данными

    c = ('11.11.11.11:28782', 'Sep 13 21:03:07 2022')
    """
    ret = []
    cnt = 0
    l = len(connects)
    for c in connects:
        cnt += 1
        tmp = {}
        tmp = {'IP': c[0].split(':')[0],
               'TIME': c[1]}
        print(f"обработано {cnt} из {l} ({round((100*cnt)/l)}%)   {c}", tmp)
        c_data = [d for d in data if c[0] in d]

        for d in c_data:
            # fill failed conn info
            # VERIFY OK: depth=1, CN=vpn.company.net
            # VERIFY OK: depth=0, CN=a.vasin
            if 'VERIFY OK: depth=0' in d:
                tmp['CERT_CN'] = d.split('CN=')[1]
            # VERIFY ERROR: depth=0, error=certificate revoked: CN=a.vasin, serial=2450853..
            if 'VERIFY ERROR: depth=0' in d:
                try:
                    tmp['CERT_CN'] = d[d.index("CN=") + 3:d.index(", serial=")]
                except: # noqa
                    pass
                tmp['CONNECT_STATUS'] = d.split('error=')[1]
            # TLS Auth Error: Auth Username/Password verification failed for peer
            if 'TLS Auth Error: ' in d:
                tmp['CONNECT_STATUS'] = d.split('TLS Auth Error: ')[1]
            if 'peer info' in d:
                t = d.split()[-1]
                tt = t.split('=')
                tmp[tt[0]] = tt[1]
            # fill success conn info
            # TLS: Username/Password authentication succeeded for username 'a.vasin' [CN SET]
            if 'authentication succeeded' in d:
                tmp['CONNECT_STATUS'] = d.split('TLS: ')[1]
                tmp['LOGIN_LDAP'] = d[d.index(" '") + 2:d.index("' ")]
            # MULTI_sva: pool returned IPv4=10.8.0.21, IPv6=(Not enabled)
            if 'MULTI_sva' in d:
                tmp['IP_VPN'] = d[d.index('IPv4=') + 5:d.index(', ')]

        ret.append(tmp)
        # пишем каждые 500 записей или если это последний конект
        if (cnt % 500) == 0 or c == connects[-1]:
            write_data(ret)
            ret = []


def write_data(data: list):
    """ Пишем в файл json по одному конекту в строку
    """
    print("Запись")
    with open(JSON_FILE, 'a') as f:
        for c in data:
            json.dump(c, f)
            f.write("\n")


def get_last_connect() -> dict:
    """ Находим дату последнего обработанного конекта
    Ожидаемый пример строки:
    {"IP": "1.1.1.1", "TIME": "Sep 16 06:10:18 2022", "CERT_CN": "a.vasin", "CONNECT_STATUS": "certificate revoked: CN=a.vasin"}
    """
    # после ротации файл пустой
    if os.stat(JSON_FILE).st_size == 0:
        return {}

    with open(JSON_FILE, 'r') as f:
        last_line = f.readlines()[-1]
        ret = json.loads(last_line)
    return ret


def check_lock() -> bool:
    ret = False
    if os.path.exists(LOCK_FILE):
        ret = True
        os.remove(LOCK_FILE)
    return ret


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    _exit()


def _exit():
    os.remove(LOCK_FILE)
    exit(0)


if __name__ == '__main__':
    if check_lock():
        raise Exception(f"LOCK file present({LOCK_FILE}), exit.")

    signal(SIGINT, handler)
    with open(LOCK_FILE, 'w') as f:
        f.write('')
    last_connect = {}
    if os.path.exists(JSON_FILE):
        last_connect = get_last_connect()

    data = get_data(last_connect)
    connects = get_connects(data)

    if connects:
        fill_connects(connects)
    _exit()
