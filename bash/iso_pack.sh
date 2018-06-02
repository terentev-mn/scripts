#!/bin/bash
# apt-get install dumpet xorriso squashfs-tools gddrescue
# check argument
if [ $# = 0 ]; then
    echo "Usage: $0 file.iso"
    exit 0
fi
dir=$(pwd)/livecdtmp
# check dir
if [ ! -d "$dir" ]; then
    echo "$dir not found!"
fi

#Regenerate manifest
echo "_____ Stage 1 _____"
echo "Regenerate manifest"
chmod +w $dir/extract-cd/casper/filesystem.manifest
chroot $dir/squashfs-root dpkg-query -W --showformat='${Package} ${Version}\n' > $dir/extract-cd/casper/filesystem.manifest
cp $dir/extract-cd/casper/filesystem.manifest $dir/extract-cd/casper/filesystem.manifest-desktop
sed -i '/ubiquity/d' $dir/extract-cd/casper/filesystem.manifest-desktop
sed -i '/casper/d' $dir/extract-cd/casper/filesystem.manifest-desktop
#Жмём фс:
echo "_____ Stage 2 _____"
echo "Make squashfs"
rm $dir/extract-cd/casper/filesystem.squashfs
mksquashfs $dir/squashfs-root $dir/extract-cd/casper/filesystem.squashfs -noappend
#Обновляем filesystem.size, нужен для инсталлятора:
printf $(du -sx --block-size=1 $dir/squashfs-root | cut -f1) > $dir/extract-cd/casper/filesystem.size
#Обновляем md5sum.txt:
echo "_____ Stage 3 _____"
echo "Update md5"
rm  $dir/extract-cd/md5sum.txt
cd $dir/extract-cd
find -type f -print0 | xargs -0 md5sum | grep -v $dir/extract-cd/isolinux/boot.cat | tee md5sum.txt

#Берём оригинальный загрузчик из образа:
# Current dir extract-cd
echo "_____ Stage 4 _____"
echo "Write iso"
cd $dir/extract-cd
dd if=../../$1 bs=512 count=1 of=isolinux/isohdpfx.bin
#Создаём ISO (точка в конце команды ОБЯЗАТЕЛЬНА):
xorriso -as mkisofs \
        -isohybrid-mbr isolinux/isohdpfx.bin \
        -c isolinux/boot.cat \
        -b isolinux/isolinux.bin \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-gpt-basdat \
        -o ../../custom-xubuntu.iso .
