#!/bin/bash

quota_all="/tmp/quota_all.txt"
quota_limit="/tmp/quota_limit.txt"
mail_tmp="/tmp/mail.tmp"
###################################################
function quota_list {
>$quota_all
# Ищем папки почтовых аккаунтов (из них будет список адресов)
for i in `find /home/vpopmail/domains/$1 -maxdepth 2 -name "*\.*" -type d`
  do
    uname=$(basename $i)
    umail=$uname"@$1"
    # Если в список адресатов попадает  utsrus.com, исключаем его
    if [ $uname = "$1" ]
      then
        continue
    fi
    quota=`/home/vpopmail/bin/vuserinfo $umail | grep quota|grep -o '[0-9]*'`
    used=`/home/vpopmail/bin/vuserinfo $umail  | grep usage|grep -o '[0-9]*'`
    # quota_g размер в Гигабайтах
    if [ "$quota" -gt 0 ]
       then quota_g=$(($quota / 10**9))
       else quota_g=0
    fi
    # пишем во временный файл"
    echo -e "$uname\t$quota_g\t$used">>$quota_all
    quota=0
    used=0
done
}
#################################################
function mail_to_user {
#domain=$1
mail_dir="/home/vpopmail/domains/$1"
grep 9[7-9] $quota_all> $quota_limit
if [ ! -s $quota_limit ]; then
  return 1
fi
#                       mail  q   used
while IFS=$'\t' read -r col1 col2 col3
  do
  #   find big_dir
    cd -- "$(find $mail_dir -mindepth 1 -maxdepth 2 -name "$col1" -type d)/Maildir"
    big_dir=$(du -a | sort -n -r | head -n 2|sed -n 2p|awk '{print $2}')
    case "$big_dir" in
      "./.Sent")
          big_dir="Отправленные"
          ;;
      "./cur")
          big_dir="Входящие"
          ;;
      *)
          big_dir=$(echo $big_dir|sed 's/\&/\+/g' |sed  's/\,/\//g'|iconv -f UTF-7 -t UTF-8|sed 's/INBOX/Входящие/'|sed 's,./.,,')
          ;;
    esac

    # Mail to user
    >$mail_tmp
    subject="Ваш почтовый ящик заполнен на $col3%"
    encoded_subject="=?utf-8?B?$(base64 --wrap=0 <<< "$subject")?="
    echo "To: <$col1@$1>">>$mail_tmp
    echo "From: <admin@$1>">>$mail_tmp
    echo "Subject: $encoded_subject">>$mail_tmp
    echo 'MIME-Version: 1.0'>>$mail_tmp
    echo 'Content-Type: text/plain; charset=utf-8; format=flowed'>>$mail_tmp
    echo 'Content-Transfer-Encoding: 8bit'>>$mail_tmp
    echo 'Content-Language: ru-RU'>>$mail_tmp
    echo ''>>$mail_tmp
    echo 'Размер вашего почтового ящика достиг критического уровня.'>>$mail_tmp
    echo 'В ближайшее время вы не сможете получать письма.'>>$mail_tmp
    echo ''>>$mail_tmp
    echo "Вам нужно почистить папку **\"$big_dir\"**">>$mail_tmp
    echo 'А также удалить старые письма (особенно со вложениями).'>>$mail_tmp
    cat $mail_tmp | /var/qmail/bin/sendmail $col1@utsrus.com
  done < $quota_limit
  mail_to_admin $1
}
######################################################
function mail_to_admin {
## Mail to admin
## $1 domain
>$mail_tmp
subject="$1 заканчивается квота"
encoded_subject="=?utf-8?B?$(base64 --wrap=0 <<< "$subject")?="
echo 'To: <mks@utsrus.com>'>>$mail_tmp
echo 'From: <admin@utsrus.com>'>>$mail_tmp
echo "Subject: $encoded_subject">>$mail_tmp
echo 'MIME-Version: 1.0'>>$mail_tmp
echo 'Content-Type: text/plain; charset=utf-8; format=flowed'>>$mail_tmp
echo 'Content-Transfer-Encoding: 8bit'>>$mail_tmp
echo 'Content-Language: ru-RU'>>$mail_tmp
echo ''>>$mail_tmp
cat $quota_limit>>$mail_tmp
cat $mail_tmp | /var/qmail/bin/sendmail mks@utsrus.com
rm $mail_tmp
}
#######################################################
for domain in $(ls /home/vpopmail/domains)
  do
  quota_list $domain
  mail_to_user $domain
  done
