#!/bin/bash
# script for nagios
# 
if [ "$1" = "-w" ] && [ "$2" -gt "0" ] && \
    [ "$3" = "-c" ] && [ "$4" -gt "0" ]; then

    mem=0
    for pid in `pidof $5`
	do
	memRSS=`grep 'VmRSS:' /proc/$pid/status | awk -F' ' '{print $2}'`
	mem=$(($mem+$memRSS))
    done
    mem=$(($mem/1024))
    echo $mem "Mb"

    if [ "$mem" -ge "$4" ]; then
        echo "Memory: CRITICAL Res: $mem MB"
        $(exit 2)
    elif [ "$mem" -ge "$2" ]; then
        echo "Memory: WARNING Res: $mem MB"
        $(exit 1)
    else
        echo "Memory: OK Res: $mem MB"
        $(exit 0)
    fi


else
    echo "check_salt_mem v1.0"
    echo ""
    echo "Usage:"
    echo "check_salt -w <warn_MB> -c <criti_MB> <pattern>"
    echo ""
    echo "check_salt -w 1024 -c 2048 python"
    exit
fi
