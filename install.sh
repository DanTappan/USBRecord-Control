# /usr/bin/env bash
#
# Install usbrecord package on a Raspberry Pi

# In case we are updating: shut down the running version
sudo systemctl stop usbrecord

# Prerequisites
sudo apt update -y && sudo apt upgrade -y
sudo apt-get -y install sox libsox-fmt-all

#
# Install automount package so that USB drives are automatically mounted on connect
# this is only required on systems without a desktop, should we check for that?
#
wget https://github.com/fasteddy516/pi-usb-automount/releases/latest/download/pi-usb-automount.deb
sudo dpkg -i pi-usb-automount.deb
cat > exfat <<EOF
# -*- sh -*-

# Options to use for auto-mounting devices detected with a exfat filesystem
AUTOMOUNT_OPTS='uid=1000,gid=1000,rw,nosuid,nodev,noexec,relatime,fmask=0000,dmask=0000,iocharset=utf8,errors=remount-ro'
EOF
sudo mv exfat /etc/pi-usb-automount.d

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


