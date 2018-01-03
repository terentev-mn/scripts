#!/bin/bash

IFS_old=$IFS
IFS=''

if [ $# -ne 1 ]; then
        echo "Enter directory"
    	exit 0;
fi

find "$1" -depth -name '*' | while read file ; do
        directory=$(dirname $file)
        oldfilename=$(basename $file)
        newfilename=$(echo $oldfilename | tr -s [:punct:]| tr -s [:blank:]| sed 's/\ \./\./g'| sed 's/\"//g')
        if [ "$oldfilename" != "$newfilename" ]; then
                # Renaming
                mv -v "$directory/$oldfilename" "$directory/$newfilename"
                # Printing
                 echo ""$directory/$oldfilename" ---> "$directory/$newfilename""
        fi
        done
exit 0
IFS=$IFS_old
