#
# Paths to data files, as needed for pyinstaller
#
from os import path

runrecord = path.abspath(path.join(path.dirname(__file__), 'run_usbrecord'))
killrecord = path.abspath(path.join(path.dirname(__file__), 'kill_usbrecord'))
