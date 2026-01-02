# /usr/bin/env bash
#
# Install usbrecord package on a Raspberry Pi

# In case we are updating: shut down the running version
sudo systemctl stop usbrecord

# Prerequisites
sudo apt update -y && sudo apt upgrade -y
sudo apt-get -y install sox libsox-fmt-all
sudo apt-get -y install python-pip3

# *** START OF support for USB RTC
#
# This package uses timestamps to name the recording files. Raspberry Pi does not have a battery backed up clock, it assumes that
# it is connected to a network and can use NTP. It is possible (likely) that the WiFi router on an XR18 does not have an Internet connection
# This means that the recording files will potentially hbe timestamped with the wrong date. 
#
# To avoid this, the following code supports the SBC USB RTC clock - https://github.com/sbcshop/USB-C-RTC-Software
#
# Note that installing this is harmless on a system which does not have a USB RTC plugged in
# the code will silently sleep 

# Install SBC Computing PyMCP2221A if using SBC USB RTC
sudo pip install PyMCP2221A --break-system-packages

if [ ! -d ~/bin ]; then
  mkdir ~/bin
fi
# Grab a copy of the app to read the USB RTC
( cd ~/bin; 
  wget https://raw.githubusercontent.com/sbcshop/USB-RTC-Software/refs/heads/main/Examples/Set_Time_Boot.py
  wget https://raw.githubusercontent.com/sbcshop/USB-RTC-Software/refs/heads/main/Examples/Set_Time_From_Sysclock.py
  chmod +x *.py

  cat > Set_Time_From_RTC << EOF
#! /bin/bash
exec > /dev/null 2>&1
while true; do
   sudo ~/bin/Set_Time_Boot.py
   if [ "\$?" = "0" ] ; then
       break
   else
       # Repeat until set time succeeds
       sleep 300
  fi
done
logger "Set System Clock from USB RTC: \`date\`"
EOF
chmod +x Set_Time_From_RTC

echo Edit crontab to add : @reboot /home/`whoami`/bin/Set_Time_From_RTC
)

# *** END OF Support for USB RTC

#
# If not already installed, Install automount package so that USB drives are automatically mounted on connect
# this is only required on systems without a desktop, should we check for that?
#
if [ ! -d /etc/pi-usb-automount ]; then
  wget https://github.com/fasteddy516/pi-usb-automount/releases/latest/download/pi-usb-automount.deb
  sudo dpkg -i pi-usb-automount.deb
  cat > exfat <<EOF
# -*- sh -*-

# Options to use for auto-mounting devices detected with a exfat filesystem
AUTOMOUNT_OPTS='uid=1000,gid=1000,rw,nosuid,nodev,noexec,relatime,fmask=0000,dmask=0000,iocharset=utf8,errors=remount-ro'
EOF
  sudo mv exfat /etc/pi-usb-automount.d
fi

# Check whether companion is installed and running. If not, install it
systemctl status companion > /dev/null
if [ "$?" != 0 ]; then
  curl https://raw.githubusercontent.com/bitfocus/companion-pi/main/install.sh | sudo bash
fi

#
# if you want to be appropriately paranoid, run pyinstaller on USBRecord-Control.spec
# to make sure that the executable matches the sources before running this script
#
sudo mkdir -p /etc/usbrecord
sudo cp dist/USBRecord-Control /etc/usbrecord
sudo chmod +x /etc/usbrecord/USBRecord-Control

# Substitute the current user in the systemd file
sed s/USER/`whoami`/ < usbrecord.service > /tmp/usbrecord.service
sudo cp /tmp/usbrecord.service /etc/systemd/system
sudo systemctl enable usbrecord
sudo systemctl start usbrecord


