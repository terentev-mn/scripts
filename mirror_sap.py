#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python 3
from bs4 import BeautifulSoup
import urllib.request,urllib.error
import os.path
from datetime import datetime, date, timedelta
import shutil


local_path = "/var/www/srv-spb-010/sap/172.26.15.2"
url = "http://172.26.15.2"
dirs = ("/bel/","/dir/","/kaz/","/rus/","/ukr/")
const_local_dir = "/var/www/srv-spb-010/sap"
const_files = {'BEL_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'DIR_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'KAZ_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'RUS_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'UKR_KOU_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'E03-1.Accounts_Receivable_Rosneft.xls':'http://172.26.15.2/accounts_receivable_rosneft',\
               '010.Supplier_Payment_Terms.xls':'http://172.26.15.2/supplier_payment_terms_report'}

def download_file(path_from, path_to):
    full_local_path = path_to
    full_from_path = path_from
    if not os.path.isfile(full_local_path):
        # create dir if absent
        os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
    try:
      with urllib.request.urlopen(full_from_path) as response, open(full_local_path, 'wb') as file_download:
        shutil.copyfileobj(response, file_download)
        print("Success".ljust(40, '.'), path_to)
    except Exception as e: print(str(e).ljust(40, '.'), full_from_path); response = ''

def folders_links(root_folder):
    folders = []
    with urllib.request.urlopen(root_folder + "/") as root_content:
        links = BeautifulSoup(root_content)

    for link in links.findAll('a')[1:]:
        folder = link.get('href')
        if folder.endswith('web.config'):
            continue
        folders.append(folder)
    return folders

def files_links(folder):
    files = []
    url = "http://172.26.15.2"
    url2 = url + str(folder)
    local_dir = "/var/www/srv-spb-010/sap/172.26.15.2"
    old_date = datetime.today() - timedelta(days=365)

    with urllib.request.urlopen(url2) as folder_content:
        links = BeautifulSoup(folder_content)
    for link in links.findAll('a')[1:]:
        file = link.get('href')
        if file.endswith('.msg') or file.endswith('.log'):
          continue
        full_local_path = local_dir.replace("%20"," ").replace("%25","%") + file.replace("%20"," ").replace("%25","%")
        full_url = url + file
        date_file_str = link.previous[:10].strip()
        date_file = datetime.strptime(date_file_str, '%m/%d/%Y')
        # check file's date and Availability (todo: change to one if)
        if old_date < date_file:
          if not os.path.isfile(full_local_path):
            files.append(file)
    return files

# 1. download root index.html
download_file(url + '/', local_path + '/index.html')
for dir in dirs:
    full_path = url + dir
    full_local_path = local_path + dir
    # 2. download other index.html
    download_file(full_path, full_local_path + 'index.html')
    for folder in folders_links(full_path):
        for file in files_links(folder):
            # 3. download absent files
            download_file(url + file, local_path + file)

# download const files
for c_file, c_url in const_files.items():
    download_file(c_url + '/' + c_file, const_local_dir + '/' + c_file)

