#! /usr/bin/env python3
#
# Control program for Recording from an attached USB interface
# This is intended to be used with, for example, a Behringer XR18 mixer to
# record (some subset of) the input channels.
# The number of input channels can be set to less than the maximum on the device
# but it is up to the operator to make sure that the USB interface is configured to
# map the required inputs to the channels on the USB interface
#
# Loop:
# - run a separate thread for OSC commands
# - on command, start up a 'rec' subprocess to record audio data
# --  TODO: monitor parse status lines from rec
# -- terminate 'rec' (SIGINT) on command
# - TODO: add a keepalive function?
#
# TODO - add an audio player
#
#import io
#import os
import time
import re
import threading
import subprocess
import data_files
import osc

Debug = False

#
usbrecord_terminate_process = False
usbrecord_active = False
usb_channels = 4

# rec_parse - parse the output of 'rec'
#
rec_parse_prog = None
def rec_parse(line):
    global rec_parse_prog

    if rec_parse_prog is None:
        rec_parse_prog = re.compile("In:.+ Out:([0-9.]+[kMG]) .+")
    match = rec_parse_prog.match(line)
    if match:
        osc_task.set_custom("/custom-variable/record_bytes/value", match.group(1))

    return match

def record_status(onoff):
    """ Change in recording status. """
    global usbrecord_active

    onoff = bool(onoff) # Make sure value is a boolean

    usbrecord_active = onoff
    osc_task.set_custom("/custom-variable/record_status/value", onoff)

def setchannels(num):
    global usb_channels
    """"Set the number of channels to record"""
    usb_channels = num

def run_usbrecord():
    global usb_channels

    if Debug:
        print(f"runrecord: {data_files.runrecord}")

    args = [
        data_files.runrecord,
        "--channels",
        str(usb_channels)
    ]

    try:
        popen = subprocess.Popen(args,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True)
    except (PermissionError, FileNotFoundError):
        popen = None

    return popen

def kill_usbrecord():
    args = [
        data_files.killrecord
    ]
    subprocess.run(args)

def usbrecord_thread():
    global usbrecord_terminate_process, usbrecord_active

    popen = None

    while True:
        if popen is None:
            if not usbrecord_active:
                time.sleep(2)
                continue

            else:   # usb_acive true, try to run record

                popen = run_usbrecord()

                if popen is None:
                    time.sleep(10)
                    record_status(False)

        else:   # popen not None, subprocess is active
            popen.poll()
            if popen.returncode is not None:
                popen = None
                record_status(False)
            else:
                if not usbrecord_active or usbrecord_terminate_process:
                    # try to shut it down
                    kill_usbrecord()

                if usbrecord_terminate_process:
                    try:
                        popen.wait(2)
                    except subprocess.TimeoutExpired:
                        pass
                    popen.terminate()
                    return

                # Otherwise try to read a line of output
                line = popen.stdout.readline()
                if line:
                    line = line.strip("\n")
                    if not rec_parse(line):
                        print(f'usbrecord: {line}')

def do_record(onoff):
    """"Start/Stop recording"""

    record_status(bool(onoff))


if __name__ == '__main__' :
    threading.Thread(target=usbrecord_thread).start()

    osc_task = osc.OSCTask(do_record=do_record, setchannels=setchannels)
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        usbrecord_terminate_process = True
        do_record(0)
