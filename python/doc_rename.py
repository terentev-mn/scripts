#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" doc_rename.py 2018-03-13

Этот скрипт предназначен для переименования файлов

При запуске скрипта без параметров будет выведена справка:
    Использование: ./doc_rename.py /путь/к/каталогу

"""

import os
import sys
import re


def rename_files(dir):
    """ Функция переименовывает файлы

    get_file получает путь к каталогу

    результатом выполнения функции является новое имя файла,
    со следующими изменениями:
    было          стало
    '    '   -->  ' '
    '....'   -->  '.'
    ',,,,'   -->  ','
    ' .pdf'  -->  '.pdf'
    ',.pdf'  -->  '.pdf'
    '".pdf'  -->  '.pdf'

    Сделать:
           + поиск каталогов оканчивающихся точкой, убрать точку.
           - поиск файлов без расширений, определение типа файла, переименование.
    """
    dirs_list = []
    for root, dirs, files in os.walk(dir):
        try:
            if root.endswith('.'):
                #os.rename(root, root_new)
                dirs_list.append(root)
            for file_name in files:
                try:
                    # заменяем повторения одним знаком
                    file_newname = re.sub(' +', ' ', file_name)
                    file_newname = re.sub('\,+', ',', file_newname)
                    file_newname = re.sub('\.+', '.', file_newname)
                    # заменяем сочетание знака и точки на точку
                    # повторяем 3 раза  тк после одного повторения может
                    # остаться нереализованный случай
                    file_newname = re.sub('[ ,"]\.', '.', file_newname)
                    file_newname = re.sub('[ ,"]\.', '.', file_newname)
                    file_newname = re.sub('[ ,"]\.', '.', file_newname)
                    if file_name != file_newname:
                        print(' ' + root + '/' + file_name, '-->\n', root + '/' + file_newname)
                        os.rename(root + '/' + file_name, root + '/' + file_newname)
                except Exception as e:
                    print('Files level:', e)
                    print(root, '/' + file_name)
                    continue
        except Exception as e:
            print('Dirs level:', e)
            print(root + '/' + file_name)
            continue
    if len(dirs_list):
        rename_dirs(dirs_list)
    return

def help_usage():
    print("Использование:   ", sys.argv[0], " /путь/к/каталогу")
    sys.exit()


def rename_dirs(dirs_list):
    """ Функция переименовывает каталоги

    rename_dirs получает список каталогов

    разбиваем полный путь на подкаталоги и
    проверяем если оканчивается на:
    - пробел
    - запятая
    - точка
    то убираем последний знак в имени
    и прерываем цикл, тк в случае если в пути несколько исправлений
         - имеем ошибку No such file or directory
    из этого следует, что иногда нужно несколько раз запускать скрипт.
    """
    print('_____________Renaming dirs________________')
    for dir in dirs_list:
        try:
            print("dir:", dir)
            dir_split = dir.split(os.sep)
            for i, sub_dir in enumerate(dir_split):
                if sub_dir.endswith('.') or sub_dir.endswith(' ') or sub_dir.endswith(','):
                    dir_split[i] = sub_dir[:-1]
                    break
            dir_new = '/'.join(dir_split)
            print("new:", dir_new)
            os.rename(dir, dir_new)
        except Exception as e:
            print('Error renaming:', e)
            continue


#####################################################
if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
    rename_files(sys.argv[1])
else:
    print("Каталог задан неверно")
    help_usage()
