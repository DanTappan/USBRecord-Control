#
# OSC Interface for VISCA-Game-Controller
# Task which receives OSC messages and turns them into control
# messages
#
#from typing import Optional
import threading
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

Debug = False
OSC_Port = 9999

class OSCTask:
    def set_custom(self, variable, value):
        """ Set the value for a custom variable in server """
        if Debug:
            print(f'osc-set_custom: {variable} {value}')

        self.client.send_message(f'/custom-variable/{variable}/value', value)

    @staticmethod
    def default_handler(address, *args):
        if Debug:
            print(f'osc-default: {address} {args}')

    def config_handler(self, address, *args):

        if Debug:
            print(f'osc-config: {address} {args}')
        clientchange = False
        if address == "/record/config/oschost":
            self.OSC_ServerHost = args[0]
            clientchange = True
        elif address == "/record/config/oscport":
            try:
                self.OSC_ServerPort = int(args[0])
                clientchange = True
            except ValueError:
                print(f"osc-config: bad value for server port {args[0]}")
        elif address == "/record/config/channels":
            try:
                channels = int(args[0])
                self.setchannels(channels)
            except ValueError:
                print(f"osc-config: bad value for channels {args[0]}")
        if clientchange:
            self.client = SimpleUDPClient(self.OSC_ServerHost, self.OSC_ServerPort)

    def record_handler(self, address, *args):
        """ Handle a record/<onoff> command - argment is a string 1/0 """
        if Debug:
            print(f'osc-record: {address} {args}')
        try:
            self.do_record(int(args[0]))

        except ValueError:
            print(f"OSC record: bad arguments {args}")

    def osc_task(self):
        """
        Thread to run
        """
        self.server.serve_forever()

    def __init__(self, do_record, setchannels):

        self.dispatcher = Dispatcher()
        self.do_record = do_record
        self.setchannels = setchannels

        self.dispatcher.map("/record", self.record_handler)
        self.dispatcher.map("/record/config/*", self.config_handler)

        self.dispatcher.set_default_handler(self.default_handler)

        self.OSC_ServerHost = "127.0.0.1"
        self.OSC_ServerPort = 12321
        self.client = SimpleUDPClient(self.OSC_ServerHost, self.OSC_ServerPort)
        self.server = BlockingOSCUDPServer(('',
                                            OSC_Port),
                                           dispatcher=self.dispatcher)
        self.thread = threading.Thread(target=self.osc_task)
        self.thread.daemon = True
        self.thread.start()
        pass

    def shutdown(self):
        self.server.shutdown()
        pass