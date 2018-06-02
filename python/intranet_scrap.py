#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import csv

url = 'http://10.0.0.110'

page = urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
offices = soup.findAll('a', href=re.compile("users.*office"))
data = []
tables = []
for office in offices:
    #print(office['href'])
    #print(office.getText())
    data.append([office.getText()])
    page = urlopen(url + office['href'])
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.findAll('table', attrs={'border':'0', 'cellpadding':"3", 'cellspacing':"1", 'width':"1160"})
    tables.append(table[0])
    # mining data for csv file
    rows = table[0].findAll('tr')
    for row in rows:
        cols = row.find_all('td')
        #cols = [ele.text.strip() for ele in cols]
        cols = [ele.text for ele in cols]
        data.append([ele for ele in cols if ele])

with open('intranet.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(d for d in data )

with open('intranet.html', 'w') as f:
    for t in tables:
        f.write(str(t))
