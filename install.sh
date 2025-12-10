# /usr/bin/env bash
#
# Install usbrecord package on a Raspberry Pi

# In case we are updating: shut down the running version
sudo systemctl stop usbrecord

# Prerequisites
sudo apt update -y && sudo apt upgrade -y
sudo apt-get install sox libsox-fmt-all

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


