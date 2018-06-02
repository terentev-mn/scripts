#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" dump_acl.py 2018-03-10

Этот скрипт предназначен для копирования и восстановления
acl в samba шарах. Хотя, будет работать и с обычными юниксовыми
файлами и каталогами.

При запуске скрипта без параметров будет выведена справка:
    Использование:
    Для создания копии (dump) acl:    ./dump_acl2.py -d /путь/к/каталогу
    Для восстановления (restore) acl: ./dump_acl2.py -r /путь/к/каталогу
    Файл с acl'ами (acl.json) хранится в том же каталоге

Скрипт использует внешнюю библиотеку pylibacl,
в debian/ubuntu её можно установить командой
   # apt install python3-pylibacl

На момент написания скрипта версия pylibacl 0.5.3-1

"""


import os
import json
import sys
import re
try:
    import posix1e
except ImportError:
    print("Модуль 'posix1e' не найден")
    print("Установите пакет: apt install python3-pylibacl")
    sys.exit()


def check_acl(raw, err_acl, val_acl):
    """ Функция проверки валидности acl

    check_acl получает аргументы:
              raw     - строка непроверенных пользователей или групп
              err_acl - множество невалидных пользователей или групп
              val_acl - множество валидных пользователей или групп

    возвращает:
              valid_acls - строка проверенных пользователей или групп
              err_acl - тоже что и на входе (с дополнением)
              val_acl - тоже что и на входе (с дополнением)

    строку raw разбиваем на список acls, чтобы проверить каждого пользователя/группу
    acl_clear - очищенное от прав имя пользователя/группы
        проверяем был ли acl_clear уже проверен (входит в одно из множеств err_acl/val_acl)
        если входит в err_acl, то исключаем его из списка: acls.pop(i)
        если входит в val_acl, то переходим к следующему элементу
        если не входит не в одно из множеств, то проверяем валидность и
        вносим в соответствующее множество

    собираем из списка acls строку valid_acls

    """
    acls = []
    acls = raw.split(',')
    for i, acl in enumerate(acls):
        try:
            start = acl.find(':')
            end = acl.find(':', start + 1)
            acl_clear = acl[start + 1:end]
            if acl_clear in val_acl or acl_clear in err_acl:
                continue
            d = posix1e.ACL(text = acl)
            val_acl.add(acl_clear)
        except Exception as e:
            print('check_acl: Нет такого пользователя/группы:', acl_clear)
            err_acl.add(acl_clear)
            acls.pop(i)
    valid_acls = ','.join(acls)
    return valid_acls, err_acl, val_acl


def dump_acl(dir):
    """ Функция копирует права доступа указанного каталога (рекурсивно)
        и записывает их в файл acl.json

    dump_acl получает путь к каталогу

    результатом выполнения функции является словарь acl_dict,
    который затем пишется в файл acl.json в указанном каталоге.

    Обходим каталог рекурсивно,
    так как у каталогов acl присутствуют default права
    записываем их с префиксом 'default_'

    Формат хранения данных в словаре:
         {'путь':'права', 'default_путь':'права'}

    """
    acl_dict = {}
    for root, dirs, files in os.walk(dir):
        try:
            path = root.split(os.sep)
            root_acl = str(posix1e.ACL(file=root))
            root_def_acl = str(posix1e.ACL(filedef=root))
            acl_dict[root] = root_acl
            acl_dict["default_" + root] = root_def_acl
            for file_name in files:
                try:
                    if 'acl.json' in file_name:
                        continue
                    file_path = root + "/" + file_name
                    file_acl = str(posix1e.ACL(file=file_path))
                    acl_dict[file_path] = file_acl
                except Exception as e:
                    print('Files level:', e)
                    print(root, '/' + file_name)
                    continue
        except Exception as e:
            print('Dirs level:', e)
            print(root + '/' + file_name)
            continue

    with open(dir + '/acl.json', 'bw') as f:
        f.write(json.dumps(acl_dict, ensure_ascii=False).encode('utf8'))
    return


def recovery_acl(dir):
    """ Функция recovery_acl восстанавливает права доступа
        указанного каталога (рекурсивно) из файла acl.json

    recovery_acl получает путь к каталогу

    результатом выполнения функции является отчет о восстановлении,
    в котором указываются:
             - пользователи/группы не прошедшие проверку в функции
               check_acl
             - количество и список каталогов неудавшихся операций

    """
    err_acl = set()
    val_acl = set()
    err_path = set()
    with open(dir + '/acl.json', 'r') as f:
        acl_dict = json.load(f)
    for file_path, file_acl in acl_dict.items():
        try:
            if not os.path.exists(file_path) and not file_path.startswith('default_'):
                err_path.add(file_path)
                continue
            file_acl = file_acl.replace('\n', ',', file_acl.count('\n') -1)
            if 'effective' in file_acl:
                file_acl = file_acl.replace('\t', '')
                file_acl = re.sub('#effective:[r,w,x,-]{3}', '', file_acl)
            if file_path.startswith('default_'):
                file_path = file_path.replace('default_', '', 1)
                if not os.path.exists(file_path):
                    err_path.add(file_path)
                    continue
                valid_acl, err_acl, val_acl = check_acl(file_acl, err_acl, val_acl)
                posix1e.ACL(text = valid_acl).applyto(file_path, posix1e.ACL_TYPE_DEFAULT)
                continue
            if 'acl.json' in file_path:
                continue
            valid_acl, err_acl, val_acl = check_acl(file_acl, err_acl, val_acl)
            posix1e.ACL(text = valid_acl).applyto(file_path)
        except Exception as e:
            print('---------------recovery_acl--------------')
            print(e)
            print(file_path)
            print('Valid ACL:\n', valid_acl)
            print('-----------------------------------------')
    print('Путь не найден',len(err_path),'раз')
    for path in sorted(err_path):
        print(path)
    print('=============================')
    print('Не прошли проверку (удалены?):')
    print('=============================')
    for entry in sorted(err_acl):
        print(entry)
    return

def help_usage():
    print("Использование:")
    print("Для создания копии (dump) acl:   ", sys.argv[0], "-d /путь/к/каталогу")
    print("Для восстановления (restore) acl:", sys.argv[0], "-r /путь/к/каталогу")
    print("Файл с acl\'ами (acl.json) хранится в том же каталоге")
    sys.exit()


if len(sys.argv) == 3 and os.path.isdir(sys.argv[2]):
    if sys.argv[1] == '-d':
        dump_acl(sys.argv[2])
    elif sys.argv[1] == '-r':
        if os.path.exists(sys.argv[2] + '/acl.json'):
            recovery_acl(sys.argv[2])
        else:
            print("Отсутствует файл:", sys.argv[2] + '/acl.json')
else:
    help_usage()

