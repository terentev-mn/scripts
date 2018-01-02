#!/usr/bin/python3

from bs4 import BeautifulSoup
import urllib.request,urllib.error
import os.path
from datetime import datetime, date, timedelta
import shutil


old_date = datetime.today() - timedelta(days=365)
local_dir = "/var/www/srv-spb-010/sap/172.26.15.2"
url = "http://172.26.15.2"
dirs = ["bel","dir","kaz","rus","ukr"]

def dw_const_files():
    const_local_dir = "/var/www/srv-spb-010/sap"
    const_files = {'BEL_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'DIR_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'KAZ_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'RUS_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'UKR_KOU_Open_Orders_New.xls':'http://172.26.15.2/Shanghai/Open_Orders_Reports',\
               'E10.accounts_receivable_rosneft.xls':'http://172.26.15.2/accounts_receivable_rosneft',\
               '010.Supplier_Payment_Terms.xls':'http://172.26.15.2/supplier_payment_terms_report'}
    # download const_files
    for c_file, c_url in const_files.items():
        try:
            with urllib.request.urlopen(c_url + '/' + c_file) as response, open(const_local_dir + '/' + c_file, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except urllib.error.HTTPError:
            print('HTTP Error 404: Not Found ' + c_url + '/' + c_file)
            response = ''

def work(dir):
    global url, local_dir
    # dowload root index.html
    try:
        with urllib.request.urlopen(url + '/' + dir + '/') as response, open(local_dir + '/' + dir + '/index.html', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except:
        print('error download index.html')
        response = ''
    with urllib.request.urlopen(url + "/" + dir + "/") as root_content:
        folder_links = BeautifulSoup(root_content)
    # find folder links
    for link in folder_links.findAll('a')[1:]:
        folder_link = link.get('href')
        if "web" in folder_link:
            continue
        # print(folder_link)
        # dowload folder/index.html (error when folder older than old_date)
        # don't use. link!=filename fucking umlyaut.
        # try:
        #     with urllib.request.urlopen(url + folder_link) as response, open(local_dir + folder_link + 'index.html', 'wb') as out_file:
        #         shutil.copyfileobj(response, out_file)
        # except:
        #    print('error download folder/index.html')
        #    response = ''
        url2 = url + str(folder_link)
        with urllib.request.urlopen(url2) as folder_content:
            file_links = BeautifulSoup(folder_content)
        # find file links
        for f_link in file_links.findAll('a')[1:]:
            file_link = f_link.get('href')
            if ".msg" in file_link:
                continue
            full_local_path = local_dir.replace("%20"," ").replace("%25","%") + file_link.replace("%20"," ").replace("%25","%")
            full_url = url + file_link
            date_file_str = f_link.previous[:10].strip()
            date_file = datetime.strptime(date_file_str, '%m/%d/%Y')
            # check file's date and Availability (todo: change to one if)
            if old_date < date_file:
                if not os.path.isfile(full_local_path):
                    print ('file absent ',full_local_path)
                    # create dir if absent
                    os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
                    # download file
                    try:
                        with urllib.request.urlopen(full_url) as response, open(full_local_path, 'wb') as out_file:
                            shutil.copyfileobj(response, out_file)
                    except urllib.error.HTTPError:
                        print('HTTP Error 401: Unauthorized')
                        response = ''
                    except IsADirectoryError:
                        print('IsADirectoryError: Is a directory')
                        response = ''

for dir in dirs:
    work(dir)

dw_const_files()

