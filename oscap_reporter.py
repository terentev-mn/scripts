#!/usr/bin/env python3

import subprocess as sp
import os
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime

"""
wget -O {filename_bz2} f"https://security-metadata.canonical.com/oval/com.ubuntu.{codename}.usn.oval.xml.bz2"
f"bzip2 -d {filename_bz2}"
f"oscap oval eval --results {report_xml} {xml_file}"


wget https://www.debian.org/security/oval/oval-definitions-$(lsb_release -cs).xml.bz2
bunzip oval-definitions-$(lsb_release -cs).xml.bz2

oscap oval eval --report report.html oval-definitions-$(lsb_release -cs).xml
"""


def run_cmd(cmd_: str) -> dict:
    """ Выполняет команду в bash
    """
    ret = {'stdout': '', 'stderr': ''}
    # print(f"bash: {cmd_}")
    try:
        if sys.version_info > (3, 9):
            # result = sp.run(cmd_, capture_output=True, encoding='utf-8', shell=True, user=user, env={'HOME': home})
            result = sp.run(cmd_, capture_output=True, encoding='utf-8', shell=True)
            ret['stdout'] = result.stdout.strip().split('\n')[0]
            ret['stderr'] = result.stderr.strip()

        elif sys.version_info > (3, 8):
            result = sp.run(cmd_, capture_output=True, encoding='utf-8', shell=True)
            ret['stdout'] = result.stdout.strip().split('\n')[0]
            ret['stderr'] = result.stderr.strip()
        else:
            result = sp.Popen(cmd_.split(), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, encoding='utf-8')
            ret['stdout'], ret['stderr'] = result.communicate()
            ret['stdout'] = ret['stdout'].strip().split('\n')[0]
    except Exception as err:
        ret['stderr'] = err
        print(ret)

    return ret


def get_os_info() -> (str, str):
    """Получает кодовое имя Ubuntu (например, focal, jammy)."""
    cn = run_cmd("lsb_release -cs")['stdout'].lower()
    osid = run_cmd("lsb_release -is")['stdout'].lower()
    return cn, osid


def download_and_extract_oval(codename: str, os_id: str) -> str:
    """Скачивает и распаковывает OVAL-файл."""
    url = {
        'ubuntu': f'https://security-metadata.canonical.com/oval/com.ubuntu.{codename}.usn.oval.xml.bz2',
        'debian': f'https://www.debian.org/security/oval/oval-definitions-{codename}.xml.bz2'
    }
    filename_bz2 = f"{codename}.oval.xml.bz2"
    run_cmd(f"wget -O {filename_bz2} {url[os_id]}")
    run_cmd(f"bzip2 -d {filename_bz2}")
    print('Сигнатуры скачаны и распакованы')

    return filename_bz2.replace('.bz2', '')


def check_deps(deb_pkg: str) -> bool:
    ret = True
    check_cmd = 'oscap -h'
    if run_cmd(check_cmd)['stderr']:
        run_cmd(f"apt install {deb_pkg} -y")
        if run_cmd(check_cmd)['stderr']:
            ret = False

    check_cmd = 'bzip2 -h'
    if run_cmd(check_cmd)['stderr']:
        run_cmd('apt install bzip2 -y')

    return ret


def run_oscap_eval(xml_file, hostname, codename):
    """Запускает oscap и генерирует отчет."""
    report_xml = "oval-results.xml"
    run_cmd(f"oscap oval eval --report {hostname}-{codename}.html --results {report_xml} {xml_file}")
    print('oscap запущен')
    return report_xml


def parse_oval_results(xml_file):
    """Парсит XML-результаты и возвращает список найденных уязвимостей (status == 'false')."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    ns = {
        "oval": "http://oval.mitre.org/XMLSchema/oval-results-5",
        'def': 'http://oval.mitre.org/XMLSchema/oval-definitions-5',
    }
    # Найдем <results>
    results = root.find('oval:results', ns)
    # Найдем <system> внутри <results>
    system = results.find('oval:system', ns)
    # Найдем <definitions> внутри <system>
    definitions = system.find('oval:definitions', ns)

    results = []
    for definition in definitions.findall('oval:definition', ns):
        def_id = definition.get('definition_id')
        res = definition.get('result')
        # ver = definition.get('version')
        if res == 'true':
            # print(definition.keys())
            # print(f"ID: {def_id}, Result: {res} Version: {ver}")
            path = f".//def:definition[@id='{def_id}']"
            element = root.find(path, ns)
            # element = defs.find(path, ns)

            if element is not None and element.get('class') != 'inventory':
                # print(element.attrib)
                title = element.find(".//def:title", ns)
                adv = element.find(".//def:advisory", ns)
                if adv:
                    severity = adv.find(".//def:severity", ns)
                    # <issued date="2025-06-09"/>
                    issued_date = adv.find(".//def:issued", ns)
                    if isinstance(issued_date, ET.Element):
                        issued_date = issued_date.get('date')
                    else:
                        issued_date = None
                    cve_ = adv.find(".//def:cve", ns)
                    if isinstance(cve_, ET.Element):
                        cve = cve_.get('href')
                    else:
                        cve = None
                else:
                    # debian
                    issued_date = element.find(".//def:date", ns)
                    if issued_date:
                        issued_date = issued_date.text
                    # issued_date = issued_date.text
                    cve_ = element.find(".//def:reference", ns)
                    if isinstance(cve_, ET.Element):
                        cve = cve_.get('ref_url')
                    else:
                        cve = None
                    severity = None

                if title is not None:
                    t = title.text
                else:
                    t = ''
                if severity is not None:
                    s = severity.text
                else:
                    s = ''

                # if isinstance(cve, ET.Element):
                print(f"{issued_date}\t[{s}]\t{cve}\t{t}")
                # else:
                #     print(f"{issued_date}\t[{s}]\t\t{t}")


def main():
    codename, os_id = get_os_info()
    hostname = run_cmd("hostname")['stdout']

    print(f"Сервер: {hostname}, ось: {os_id}, версия: {codename}")
    oval_xml = download_and_extract_oval(codename, os_id)
    dep_pkg = 'openscap-scanner' if codename == 'noble' or os_id == 'debian' else 'libopenscap8'
    print(f"Зависимость: {dep_pkg}")
    if check_deps(dep_pkg):
        print('oscap установлен')
        report_xml = run_oscap_eval(oval_xml, hostname, codename)
        parse_oval_results(report_xml)
        print('-' * 30)
        print('обработка завершена')
    else:
        print('Ошибка! Зависимости не установлены')


if __name__ == "__main__":
    main()
