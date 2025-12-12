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
# - terminate 'rec' on command
#
# TODO - add an audio player

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
probe_device = False

# timer_thread - periodic timer
#
def timer_thread():
    global probe_device

    sleep(30)   # Give Companion time to start up
    while True:
        probe_device = True
        time.sleep(300)

# find_device - run periodically to discover the connected
# recording device
def find_device():
    output = subprocess.run([ './probe_device'],
                                capture_output=True, text=True).stdout
    match = re.match("hw:([A-Za-z0-9]+)", output)
    if match:
        osc_task.set_custom("record_device", match.group(1))


# rec_parse - parse the output of 'rec'
#
rec_parse_prog = None
def rec_parse(line):
    global rec_parse_prog

    if rec_parse_prog is None:
        rec_parse_prog = re.compile("In:.+ Out:([0-9.]+[kMG]) .+")
    match = rec_parse_prog.match(line)
    if match:
        osc_task.set_custom("record_bytes", match.group(1))
    else:
        match = re.match("Recording .+ from ([a-zA-Z0-9]+), Output File: .+", line)
        if match:
            osc_task.set_custom("record_device", match.group(1))

    return match

def record_status(onoff):
    """ Change in recording status. """
    global usbrecord_active

    onoff = bool(onoff) # Make sure value is a boolean

    usbrecord_active = onoff
    osc_task.set_custom("record_status", onoff)

def setchannels(num):
    global usb_channels
    """"Set the number of channels to record"""
    usb_channels = num

def run_usbrecord():
    """Start the usb_record script to run 'rec'"""
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
    """Kill the running 'rec' process with a SIGINT"""
    args = [
        data_files.killrecord
    ]
    subprocess.run(args)

def usbrecord_thread():
    """ Thread to run/monitor the 'rec' subprocess"""
    global usbrecord_terminate_process, usbrecord_active, probe_device

    popen = None

    while True:
        if popen is None:
            if not usbrecord_active:
                # No active 'rec' process: perodic check for a change in recording device
                #
                if probe_device:
                    find_device()
                    probe_device = False

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
                        # if it's not a line we recognize, then output for
                        # debug
                        osc_task.set_custom("record_log",
                                            line)
                        print(f'usbrecord: {line}')

def do_record(onoff):
    """"Start/Stop recording"""
    record_status(bool(onoff))

if __name__ == '__main__' :
    threading.Thread(target=usbrecord_thread, daemon=True).start()
    threading.Thread(target=timer_thread, daemon=True).start()

    osc_task = osc.OSCTask(do_record=do_record, setchannels=setchannels)

    osc_task.set_custom("recorder_reset", str(int(time.time())))

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        usbrecord_terminate_process = True
        do_record(0)
