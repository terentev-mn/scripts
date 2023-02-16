#!/usr/bin/env python3

import sqlite3
import os
import argparse

"""
Собирает инфу о каталоге, пишет в базу полный путь к файлу и его размер

SELECT sum(fsize/1024/1024/1024) from files where fpath like '%20201103.gz'
"""


class Flist:
    def __init__(self, filedb="flist.db"):
        self.filedb = filedb
        self.con, self.db = self._condb()
        self.insert_batch_size = 100000
        self.services = []

    def _condb(self):
        con = sqlite3.connect(self.filedb)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS files (
                      fpath TEXT NOT NULL UNIQUE,
                      service VARCHAR(30),
                      host VARCHAR(20),
                      year VARCHAR(20),
                      month VARCHAR(20),
                      fsize INT)''')
        return con, cur

    def __del__(self):
        self.con.close()

    def walk(self, directory: str, write_size: bool) -> (int, int):
        """Рекурсивно проходит по каталогу вызывает insert2db

        возвращает количество файлов и общий размер в Гб
        """
        total_size = 0
        cnt = 0
        cur_files = []
        for root, dirs, files in os.walk(directory):
            if not self.services:
                self.services = dirs
            # срезы - чтобы избежать исключения и сработал "or"
            service = root.split('/')[3:4] or ["none"]
            host = root.split('/')[4:5] or ["none"]
            year = root.split('/')[5:6] or ["none"]
            month = root.split('/')[6:7] or ["none"]

            len_files = len(files)
            for i, _file in enumerate(files):
                file_path = os.path.join(root, _file)
                try:
                    if write_size:
                        size = int(os.path.getsize(file_path))
                    else:
                        size = 0
                    total_size += size
                    cnt += 1
                    # cur_files.update({file_path: size})
                    cur_files.append((file_path, service[0], host[0], year[0], month[0], size))
                    if len(cur_files) >= self.insert_batch_size or i == len_files - 1:
                        self.insert2db(cur_files)
                        cur_files = []

                except Exception as err:
                    print(err)
                    continue
        return int(total_size / 1024 ** 3), cnt

    def insert2db(self, cur_files: list):
        """Пишет в базу один INSERT"""
        vals = ''
        for f in cur_files:
            vals += f"('{f[0]}', '{f[1]}', '{f[2]}', '{f[3]}', '{f[4]}', {f[5]}),"

        self.db.execute(f"INSERT OR REPLACE INTO files VALUES {vals[:-1]}")
        self.con.commit()

    def stats(self):
        """1 - по сервисам
           2 - по хостам
           3 - по сервисам хостов из топа 2

           ./flist.py|sort -k2 -nr
           SELECT sum(fsize)/1024/1024/1024 FROM files WHERE year='2021' and month='06'
        """
        stat1 = {}
        lim = 10

        for s in self.services:
            stat1[s] = self.db.execute(f"""SELECT sum(fsize)/1024/1024/1024
                                           FROM files
                                           WHERE service='{s}'""").fetchone()
        print("Stats by service:")
        for k, v in stat1.items():
            try:
                print(f"{k} {int(v[0])} Gb")
            except:  # noqa
                continue

        stat2 = self.db.execute(f"""SELECT host, SUM(fsize)/1024/1024 as s
                                    FROM files GROUP BY host
                                    ORDER BY s DESC
                                    LIMIT {lim}""").fetchall()

        print(f"Stats by host, top {lim}:")
        for c, host in enumerate(stat2):
            print(f"{c + 1}. {host[0]} {host[1]} Mb")

            stat3 = self.db.execute(f"""SELECT service, SUM(fsize)/1024/1024 as s
                                        FROM files WHERE host='{host[0]}' GROUP BY service
                                        ORDER BY s DESC LIMIT {lim}""").fetchall()
            for cs, service in enumerate(stat3):
                print(f"    {cs + 1}. {service[0]} {service[1]} Mb")


def parse_args() -> dict:
    parser = argparse.ArgumentParser(description='Собирает статистику по занимаемому логами месту')
    parser.add_argument("-c", "--collect", action="store_true", default=False, help="Произвести обработку каталога")
    parser.add_argument("-w", "--write_size", action="store_true", default=False,
                        help="Писать размер файлов (медленно)")
    parser.add_argument("-d", "--dir", default="/mnt/log", help="Каталог для обработки")
    parser.add_argument("-f", "--filedb", default="flist.db", help="Имя файла для базы")
    parser.add_argument("-s", "--stats", action="store_true", default=False, help="Вывести статистику по занимаемому месту")
    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args()
    f = Flist(args['filedb'])
    if args['collect']:
        f.walk(args['dir'], args['write_size'])
    if args['stats']:
        f.stats()
