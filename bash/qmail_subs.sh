#!/bin/bash

ME=`basename $0`
function print_help() {
    echo "Управление рассылками в qmail"
    echo
    echo "Использование: $ME параметры [email_1] [email_2]"
    echo "Параметры:"
    echo "  -l,  --list                     Вывести список рассылок."
    echo "  -l,  --list email               Вывести список рассылок, на которые подписан email."
    echo "  -a,  --add email sub_name       Подписать email на рассылку sub_name."
    echo "  -d,  --del email sub_name       Отписать email от рассылки sub_name."
    echo "  -d,  --del email all            Отписать email от всех рассылок."
    echo "  -c,  --copy email_1 email_2     Копировать рассылки с email_1 на email_2."
    echo "  -m,  --move email_1 email_2     Отписать email_1 от всех рассылок и подписать на них email_2."
    echo "  -h,  --help                     Эта справка."
}
################################
function sub_list {
# $1 email
sub_path="/home/vpopmail/uts-mail-lists"
sub_dirs=`ls -d $sub_path/*/`
for sub_dir in $sub_dirs
	do
	    sub_name=$(basename $sub_dir)
            if [ $# -ne 1 ]; then
               echo "__________________"
               echo $sub_name
               echo "------------------"
               /usr/local/bin/ezmlm/ezmlm-list $sub_dir
               continue
	    elif (/usr/local/bin/ezmlm/ezmlm-list $sub_dir|grep $1 -q) then echo $sub_name
	    fi
	done
}
################################
function sub_list_header {
# $1 email
sub_path="/home/vpopmail/uts-mail-lists"
sub_dirs=`ls -d $sub_path/*/`
echo "_________________________"
echo $1
echo "-------------------------"
sub_list $1
}
################################
function sub_add {
# $1 email $2 sub_name
sub_path="/home/vpopmail/uts-mail-lists"
sub_dirs=`ls -d $sub_path/*/`

if [ $# -ne 2 ]
   then echo "Укажите email и рассылку";
   exit 0;
fi

for sub_dir in $sub_dirs
	do
            sub_name=$(basename $sub_dir)
	    if [ $2 = $sub_name ]
               then /usr/local/bin/ezmlm/ezmlm-sub $sub_dir $1
	    fi
	done
#sub_list $1
}
################################
function sub_del {
# $1 email $2 sub_name
sub_path="/home/vpopmail/uts-mail-lists"
sub_dirs=`ls -d $sub_path/*/`

if [ $# -ne 2 ]
   then echo "Укажите email и рассылку";
   exit 0;
fi
#if [ $2 = "all" ]
#   then
#   exit 0
#fi
for sub_dir in $sub_dirs
        do
            sub_name=$(basename $sub_dir)
            if [ $2 = "all" ]
               then /usr/local/bin/ezmlm/ezmlm-unsub $sub_dir $1
               continue
            elif [ $2 = $sub_name ]
               then /usr/local/bin/ezmlm/ezmlm-unsub $sub_dir $1
            fi
        done
#sub_list $1
}
################################
function sub_copy {
# $1 email_1 $2 email_2
sub_path="/home/vpopmail/uts-mail-lists"
sub_dirs=`ls -d $sub_path/*/`

if [ $# -ne 2 ]
         then echo "Укажите email_1 и email_2";
        exit 0;
fi

for sub_name in $(sub_list $1)
        do
           sub_add $2 $sub_name
        done
}
##################################
function sub_move {
# $1 email_1 $2 email_2
sub_path="/home/vpopmail/uts-mail-lists"
sub_dirs=`ls -d $sub_path/*/`

if [ $# -ne 2 ]
         then echo "Укажите email_1 и email_2";
        exit 0;
fi

sub_copy $1 $2
sub_del $1 "all"
}
##################################
if [ $# = 0 ]; then
    print_help
fi
##################################
while [ $# -gt 0 ];
do
    case $1 in
        -l|--list) sub_list $2;
            ;;
        -a|--add) sub_add $2 $3;sub_list_header $2
            ;;
        -d|--del) sub_del $2 $3;sub_list_header $2
            ;;
        -c|--copy) sub_copy $2 $3;sub_list_header $2;sub_list_header $3
            ;;
        -m|--move) sub_move $2 $3;sub_list_header $2;sub_list_header $3
            ;;
        -h|--help) print_help
            ;;
        *) echo "Неправильный параметр";
            echo "Для вызова справки запустите $ME -h";
            exit 1
            ;;
        esac
exit 0
done
