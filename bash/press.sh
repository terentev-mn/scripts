#!/bin/bash
#aptitude install imagemagick
ME=`basename $0`
if [ -z "$3" ]; then
    res=100
else
    res=$3
fi
#######################################################
function shrink {
    gs					\
      -q -dNOPAUSE -dBATCH -dSAFER		\
      -sDEVICE=pdfwrite			\
      -dCompatibilityLevel=1.6		\
      -dPDFSETTINGS=/screen			\
      -dColorImageResolution=$2		\
      -dGrayImageResolution=$2		\
      -dMonoImageResolution=$2		\
      -sOutputFile="$3"			\
      "$1"
}
#######################################################
function scan {
# Если скрипту передан параметр scan то обрабатываем весь каталог scanner
    scan_dir="/home/Exchange/scanner"
    pressed="Сжатые_документы"
    hires="Hi_res"
    if [ ! -d "$scan_dir/$pressed" ]; then
        mkdir $scan_dir/$pressed
    fi

    if [ ! -d "$scan_dir/$hires" ]; then
        mkdir $scan_dir/$hires
    fi

    for f in $scan_dir/*.pdf
        do
          directory=$(dirname "$f")
          filename=$(basename "$f")
          echo "Processing $f"
          shrink "$f" "$res" "$directory/$pressed/$filename"
          mv $f "$directory/$hires/$filename"
        done
}
#########################################################
function pdf {
    directory=$(dirname "$1")
    filename=$(basename "$1")
    fname="${filename%.*}"
    ext="${filename##*.}"
    shrink "$1" $res /tmp/$fname"_small."$ext
    cp /tmp/$fname"_small."$ext $directory/$fname"_small."$ext
}
############################################################
function jpg {
    directory=$(dirname "$1")
    filename=$(basename "$1")
    fname="${filename%.*}"
    ext="${filename##*.}"
    convert -quality 90 -resize 50% $1 /tmp/$fname"_small."$ext
    cp /tmp/$fname"_small."$ext $directory/$fname"_small."$ext
}
############################################################
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
while [ $# -gt 0 ];
do
    case $1 in
        -scan) scan;
            ;;
        -pdf) pdf $2;
            ;;
        -jpg) jpg $2
            ;;
        *) echo "Неправильный параметр";
            exit 1
            ;;
        esac
IFS=$SAVEIFS
exit 0
done

