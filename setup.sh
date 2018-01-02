#!/bin/bash
 
nano /etc/hostname
nano /etc/hosts
 
wget ftp://10.0.0.134/apt && sh apt
wget ftp://10.0.0.134/salt_16 && sh salt_16
apt update
apt install salt-minion -y
sleep 10
 
salt_server="10.0.0.134"
if ( getent hosts $(hostname) | awk '{print $1}' |grep "192.168.0." -q) then
    salt_server="192.168.0.108"
fi
echo "master: $salt_server">/etc/salt/minion
nano /etc/salt/minion_id
 
apt install aptitude ssh mc htop
aptitude install -f -y
 
reboot
