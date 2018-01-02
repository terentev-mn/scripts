#!/bin/bash
 
IFS_old=$IFS
IFS=''
if [ -z $1 ];then echo Give target directory; exit 0;fi
 
find "$1" -depth -name '*' | while read file ; do
        directory=$(dirname "$file")
        oldfilename=$(basename "$file")
        newfilename=$(echo "$oldfilename" |tr ',' '.' |sed 's/\.\./\./g'|sed 's/\ \ /\ /g'|sed 's/__/_/g'|sed 's/\"//g'|sed 's/\ \./\./g')
        if [ "$oldfilename" != "$newfilename" ]; then
                # Renaming
                mv -v "$directory/$oldfilename" "$directory/$newfilename"
                # Printing 
#                echo ""$directory/$oldfilename" ---> "$directory/$newfilename""
        fi
        done
exit 0
IFS=$IFS_old