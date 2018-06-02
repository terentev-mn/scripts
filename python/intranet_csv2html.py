#!/usr/bin/python3
# -*- coding: utf-8 -*-

def csv_to_html_table(fname,headers=None,delimiter=","):
    with open(fname) as f:
        content = f.readlines()
    #reading file content into list
    rows = [x.strip() for x in content]
    table = "<table>"
    #creating HTML header row if header is provided 
    if headers:
        table += "".join(["<th>"+cell+"</th>" for cell in headers.split(delimiter)])
    else:
        table += "".join(["<th>"+cell+"</th>" for cell in rows[0].split(delimiter)])
        rows=rows[1:]
    #Converting csv to html row by row
    for row in rows:
        table += "<tr>" + "".join(["<td>"+cell+"</td>" for cell in row.split(delimiter)]) + "</tr>" + "\n"
    table +="</table><br>"
    return table

filename="intranet.csv"
myheader='ФИО, Местный_телефон, Мобильный_телефон, E-mail, Имя_пользов, Компьютер'
html_table=csv_to_html_table(filename, myheader)

with open('intranet.html', 'w') as f:
    f.write(html_table)
