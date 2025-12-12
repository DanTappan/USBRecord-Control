# USBRecord-Control

A Raspberry Pi based USB audio recorder controlled through [BitFocus Companion](https://bitfocus.io)

This is intended to be installed on a dedicated Raspberry Pi which is also running [BitFocus Companion](https://bitfocus.io). The canonical configuration would be to connect this to a [Behringer XR18 mixer](https://www.behringer.com/product.html?modelCode=0605-AAD) to support 
recording some or all of the 18 input channels.

## Setup
Raspberry Pi 4 or 5 with at least 4GB of memory and [BitFocus Companion](https://bitfocus.io) installed
- USB connected audio interface (e.g. XR18)
- USB disk. This is expected to be mounted on /media/*user* and contain a directory called **RECORD**. Files will be saved in Apple Core Audio Format (CAF) using names of the for *yyyy*-*mm*-*dd*-*hh*-*mm*-*ss*.caf
- Optional [Elgato Stream Deck](https://www.elgato.com/us/en/s/explore-stream-deck) for control

## Use

The recorder can be controlled either through a Stream Deck or through the web based emulator Companion.

The file [USBRecord.companionconfig](USBRecord.companionconfig) can be imported into Bitfocus Companion to set up the default set of buttons, which currently provides the following:

### Main Page
- **Record/Stop** (this button will be labeled **Record** when the recorder is idle and **Stop** when it is active)
- Below the **Record/Stop** button is a display-only button which dynamically displays the size of the current file when recording is active
- **Channels: n** - selects the number of channels to record, between 2 and 18. A short press on the button increments the number of channels, a long press decrements.
- **Control Page**: Switches to a page of buttons with control functions

### Control Page
- **Main Page**: Switches back to the main page of buttons
- **Reset** - this button resynchronizes Companion with the recorder, it should only be needed if the **usbrecord** service is restarted
- **Shutdown**: A long press on this button shuts down and powers off the recorder Pi


## Debugging

The recorder program will try to log errors, for example a failure to start the record process, to the Companion custom variable **custom:record_log**

## Installation

The installation script does the following
- installs BitFocus Companion (if not already running)
- installs a service '[pi-usb-automount](https://github.com/fasteddy516/pi-usb-automount/)' which automounts USB drives on systems which are not 
running a desktop
- creates a new systemctl service **usbrecord** which will run at system startup as the current user

Currently, you have to import the **USBRecord.companionconfig** by hand to set up the buttons

The Quick Install procedure below uses a copy of the application from the repository, which was pre-built for ARM64 Debian based systems (e.g. Raspian, Armbian) using pyinstaller. Alternatively you can clone the repository and build your own copy 
prior to running the install script

### Quick Install

```
rm -rf USBRecord-Control; git clone https://github.com/DanTappan/USBRecord-Control; ( cd USBRecord-Control; bash ./install.sh )
```




