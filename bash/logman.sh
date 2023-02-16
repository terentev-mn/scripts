#!/bin/bash

set -e

function init_vars {
  # $1 action: rezip
  case ${1} in
     rezip)
          NUMPR=200
          ;;
     copy)
          NUMPR=500
          ;;
     *)
          NUMPR=100
          ;;
  esac
  LOGFILE="./${1}.log"
  SYNCED="./${1}_synced.log"
  cores=$(nproc)
  LA_LIMIT=$[cores*2]
  DST="storage-sb"
  SIZELIMIT=52428800

  if [ ! -f "${SYNCED}" ]; then
    touch ${SYNCED}
  fi

  # Если ${SYNCED} не пустой (те мы продолжаем), то вычисляем место откуда продолжить
  if [ -s "${SYNCED}" ]; then
    # более точный способ
    #start_line=$(grep -n $(tail -n1 ${SYNCED}) ${1} | cut -f1 -d:)
    START_LINE=$(cat ${SYNCED} | wc -l)
  # или начинаем с начала
  else
    START_LINE="1"
  fi
}


function check_nproc {
    # проверяем сколько в фоне процессов, если много ждем и сбрасываем счетчик
    if [ "${numpr_cnt}" -ge "${NUMPR}" ]; then
      numpr_cnt=0
      sleep 1
    fi

}


function check_la {
    # на всякий случай проверям LA
    upt=$(uptime)
    la=$(echo ${upt#*average:}|cut -f1 -d",")
    #echo "la=${la}, upt=${upt}"
    if [ "${la}" -ge "${LA_LIMIT}" ];then
        echo "Achtung! LA ! Sleep 10"
        sleep 10
    fi
}


function main_loop {
  # $1 файл:  rezip.list
  # $2 имя функции: rezip
  total_0=$(cat ${1}|wc -l)
  cnt=0
  total=$((total_0-START_LINE+1))
  numpr_cnt=0


  # sed магия - читать файл ${1} со START_LINE до конца
  sed -n "${START_LINE}"',$p' ${1} |
  while read f; do
    cnt=$((cnt+1))
    elapsed=$((total-cnt))
    pcnt=$((100*cnt/total))
    echo -e "Total: ${total}  elapsed: ${elapsed}  done: ${cnt}(${pcnt}%) \t${f}"

    if [ -f "${f}" ] || [ -f "${f}.gz" ] || [ -f "${f}.bz2" ] || [ -f "${f}.zst" ];then
      # проверяем что файл еще не обрабатывали
      if [ "$(grep -c "${f}" ${SYNCED})" -eq 0 ]; then
        echo ${f} >> ${SYNCED}
        # угадываем имя файла, gz/bz2,zst
        # вызываем action, берем первый, поэтому аргумент не надо брать в кавычки
        action_${2} $(ls ${f}*)
      fi
    else
      # если файл не существует, считаем что его обработали
      echo ${f} >> ${SYNCED}
      if [ "$2" == "check" ]; then
        echo "WARNING_file_absent ${f}" >> ${LOGFILE}
      fi
    fi
    check_nproc
    check_la

  done
}


function action_copy {
  # $1 путь к файлу: /mnt/log/httpd_access/bitrix272/2019/05/bitrix272-20190530.gz

  # Если файл меньше 50мб то обрабатывать в фоне, но не больше NUMPR экземпляров скрипта
  # TODO размер файлов брать из flist
  FILESIZE=$(stat -c%s ${1})

  if [ "${FILESIZE}" -lt "${SIZELIMIT}" ]; then
      rsync -aR --ignore-existing ${1} ${DST}:/ &
      numpr_cnt=$((numpr_cnt+1))
  else
      rsync -aR --ignore-existing ${1} ${DST}:/
  fi
}


function action_rezip {
  # $1 путь к файлу: /mnt/log/httpd_access/bitrix272/2019/05/bitrix272-20190530.gz
  # обрабатываем только gz файлы
  set +e
  if [ "${1##*.}" = "gz" ]; then
    # Если файл меньше 5мб то обрабатывать в фоне, но не больше NUMPR экземпляров скрипта
    # TODO размер файлов брать из flist
    SIZELIMIT=5242880
    FILESIZE=$(stat -c%s ${1})
    if [ "${FILESIZE}" -lt "${SIZELIMIT}" ]; then
      # после --rm  модное  $(echo ${1} | sed 's|\.gz||')
      pigz -d ${1} && zstd -14T18q --rm "${1//.gz/}" &
      numpr_cnt=$((numpr_cnt+1))
    else
      pigz -d ${1} && zstd -14T18q --rm "${1//.gz/}"
    fi
  # сжимаем если это не архив
  elif [ "$(file -b ${1}| grep -c zip)" -eq 0 ]; then
    zstd -14T$(nproc)q --rm "${1}"
  else
    echo "Unknown archive, skip ${1}" >> ${LOGFILE}
  fi
}


function action_remove {
  # $1 путь к файлу: /mnt/log/httpd_access/bitrix272/2019/05/bitrix272-20190530.gz
  rm "${1}"
}


function action_check {
  # $1 путь к файлу: /mnt/log/httpd_access/bitrix272/2019/05/bitrix272-20190530.gz
  # проверяет, что тип файла - архив, если не так пишет в лог
  set +e
  check=$(file -b "${1}" | grep -c 'compressed data')
  if [ "${check}" -eq 0 ]; then
    echo $check
    echo "check_fail file not archive ${1}" >> ${LOGFILE}
  fi
}


function action_help {
  echo "Этот скрипт позволяет:
  - выполнять действия над большим количеством файлов
  - контролирует LA (sleep 10 при LA=cores*2)
  - после прерывания продолжает обработку с того же места
  - пишет лог в %действие%.log

Для запуска нужно указать файл со списком логов и действие
Пример:    ${0} rezip.list rezip   (rezip.log)


Возможные действия:
rezip  - пережимает логи из gz в bzip2
copy   - копирует логи на другой сервер (переменная DST)
remove - удаляет логи
check  - проверяет что файлы являются архивами, не архивные пишет в лог check.log
  "
}


###################################
if [ $# -eq 2 ]; then
  init_vars ${2}
  echo "$(date) Start" >> ${LOGFILE}
  main_loop ${1} ${2}
  echo "$(date) End" >> ${LOGFILE}

else
  action_help
  exit 1
fi
