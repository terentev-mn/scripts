#!/bin/bash
#apt-get install dumpet xorriso squashfs-tools gddrescue
# check argument
if [ $# = 0 ]; then
    echo "Usage: $0 file.iso"
    exit 0
fi
dir=$(pwd)/livecdtmp
# check dir
if [ -d "$dir" ]; then
    rm -rf $dir
fi
mkdir $dir
#mv $1 $dir
cd $dir

# Распаковываем образ в директорию
xorriso -osirrox on -indev ../$1 -extract / extract-cd
# перед этим удалить каталог если он есть squashfs-root
unsquashfs extract-cd/casper/filesystem.squashfs
cp /etc/resolv.conf squashfs-root/etc/
mount --bind /dev/ squashfs-root/dev
echo "Before exit from chrooting do: umount /proc || umount -lf /proc; umount /sys; umount /dev/pts; exit"
chroot squashfs-root mount none -t proc /proc
chroot squashfs-root mount none -t sysfs /sys
chroot squashfs-root mount none -t devpts /dev/pts
chroot squashfs-root
umount $dir/squashfs-root/dev
echo "Ready to pack iso!"
