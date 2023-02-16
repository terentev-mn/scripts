#!/bin/bash

# скрипт сжимает логи и отправляет на $DST сервер
#
# Процесс разбит на этапы:
# 1. Поиск и составление списка файлов
# 2. Сжатие. TODO: если gz файл уже есть, то происходит добавление обычным gzip. Возможно ли использовать pigz ?
# 3. Копирование на $DST при помощи rsync
set -eE
trap 'sentry $?' ERR

sentry_key="qqqqqqqqqq"
project_id=1111111111111111

function sentry {
  if [ "${1}" != "0" ]; then
    msg="$(caller): ${BASH_COMMAND}"
    echo ${msg}

    data="{ \"exception\": [{ \"type\": \"$(hostname) ${0}\", \
                              \"value\": \"${msg}\"}] }"

    curl -X POST --data "${data}" \
         -H 'Content-Type: application/json' \
         -H "X-Sentry-Auth: Sentry sentry_version=7, sentry_key=${sentry_key}, sentry_client=raven-bash/0.1" \
         https://sentry-local.company.net:4443/api/${project_id}/store/
  fi
}

function help_msg {
  echo "Usage: ${0} [start|compress|copy]"
  echo "      start    - find + compress + copy to sb2"
  echo "      compress - compress files (from list ${TOTAL}) + copy to ${DST}"
  echo "      copy     - rsync files (from list ${TOTAL}) to ${DST}(can continue after breaking)"
}

function find_log {
  echo "$(date) find begin" >> ${LOGFILE}
  # исключаем логи за сегодняшний день и все архивы *.gz/zst
  /usr/bin/find ${LOGDIR} \
                    -type f \
                    ! -name '*\.gz' \
                    ! -name '*\.zst' \
                    ! -name "*-${CURRENT_DATE}*" >> ${TOTAL}
  echo "$(date) find end. Total files: $(cat ${TOTAL} | wc -l)" >> ${LOGFILE}
}

function compress_log {
  # Проверяем что переменная не пустая, файл существует
  if [ ! -z "${1}" ] && [ -f "${1}" ];then
    if [ $(grep -c ${1} ${ZIPPED}) -eq 0 ]; then
      # Если файл уже есть, дописываем
      if [ -f "${1}.gz" ]; then
        cat ${1} | /bin/gzip >> ${1}.gz && rm ${1}
      elif [ -f "${1}.zst" ]; then
        cat ${1} | /usr/bin/zstd -14T9q --rm >> ${1}.zst
      else  # Иначе создаем новый архив
        /usr/bin/zstd -14T9q --rm ${1} 2>> ${LOGFILE}
      fi
      echo ${1} >> ${ZIPPED}
    fi
  fi
}

function copy_log {
  Fgz="${1}.gz"
  Fzst="${1}.zst"
  # Проверяем что переменная не пустая и не начинается с /mnt/log/log/
  if [ ! -z "${1}" ]; then
      # файл gz/zst существует
      if [ -f "${Fgz}" ]; then
        # проверяем что файл еще не обрабатывали
        if [ $(grep -c ${Fgz} ${SYNCED}) -eq 0 ]; then
          # синкаем и пишем ошибки в лог
          rsync -aR --ignore-existing ${Fgz} ${DST}:/ >> ${LOGFILE} 2>&1
          echo ${Fgz} >> ${SYNCED}
        fi

      elif [ -f "${Fzst}" ]; then
        # проверяем что файл еще не обрабатывали
        if [ $(grep -c ${Fzst} ${SYNCED}) -eq 0 ]; then
          # синкаем и пишем ошибки в лог
          rsync -aR --ignore-existing ${Fzst} ${DST}:/ >> ${LOGFILE} 2>&1
          echo ${Fzst} >> ${SYNCED}
        fi
      fi
  fi
}

function compress_log_wrapper {
  echo "$(date) compress begin" >> ${LOGFILE}
  if [ ! -f "${ZIPPED}" ]; then
    touch ${ZIPPED}
  fi
  while read f; do
    echo ${f}
    compress_log ${f}
  done < ${TOTAL}
  echo "$(date) compress end" >> ${LOGFILE}
}

function copy_log_wrapper {
  if [ "${DST}" != "$(hostname -s)" ]; then
    if [ ! -f "${SYNCED}" ]; then
      touch ${SYNCED}
    fi
    echo "$(date) copy to ${DST} begin" >> ${LOGFILE}
    while read f; do
      copy_log "${f}"
    done < ${TOTAL}
    echo "$(date) copy to ${DST} end" >> ${LOGFILE}
  else
    echo "$(date) DST=${DST} it is me, skipping" >> ${LOGFILE}
  fi
}


############################################
# kill prevous compress proc
pids=$(pgrep -f $0| grep -v $$)
if [[ ! -z ${pids} ]]; then
  for p in ${pids}; do
    if ps -p ${p} > /dev/null; then
      kill -9 ${p}
    fi
  done
fi

LOGFILE="/var/log/compress-errors.log"
TOTAL="/tmp/compress_old_logs_total.list"
SYNCED="/tmp/compress_old_logs_synced.list"
ZIPPED="/tmp/compress_old_logs_zipped.list"
LOGDIR="/mnt/log/"
DST="sb2"
CURRENT_DATE=$(date '+%Y%m%d')

echo "$(date) start" >> ${LOGFILE}

case ${1} in
  "start")
    > ${TOTAL}
    find_log
    > ${ZIPPED}
    compress_log_wrapper
    > ${SYNCED}
    copy_log_wrapper
    ;;
  "compress")
    compress_log_wrapper
    > ${SYNCED}
    copy_log_wrapper
    ;;
  "copy")
    copy_log_wrapper
    ;;
  *)
    help_msg
    ;;
esac

echo "$(date) finish" >> ${LOGFILE}
