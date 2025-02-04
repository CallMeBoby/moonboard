
import json
import subprocess
import logging
from moonboard_app_protocol import UnstuffSequence, decode_problem_string
import paho.mqtt.client as mqtt

import os
import pty

class OutStream: # FIXME: simplify
    def __init__(self, fileno):
        self._fileno = fileno
        self._buffer = b""

    def read_lines(self):
        try:
            output = os.read(self._fileno, 1000)
        except OSError as e:
            if e.errno != errno.EIO: raise
            output = b""
        lines = output.split(b"\n")
        lines[0] = self._buffer + lines[0] # prepend previous
                                           # non-finished line.
        if output:
            self._buffer = lines[-1]
            finished_lines = lines[:-1]
            readable = True
        else:
            self._buffer = b""
            if len(lines) == 1 and not lines[0]:
                # We did not have buffer left, so no output at all.
                lines = []
            finished_lines = lines
            readable = False

        finished_lines = [line.rstrip(b"\r")
                         for line in finished_lines]
        
        return finished_lines, readable

class MoonboardBLE():
    def __init__(self):
        self._start_mqtt()
        return

    def setup_adv(self,logger):
        """
        Setup Advertisinf"""
        logger.info('setup adv')
        setup_adv = [
        "hcitool -i hci0 cmd 0x08 0x000a 00",
        "hcitool -i hci0 cmd 0x08 0x0008 18 02 01 06 02 0a 00 11 07 9e ca dc 24 0e e5 a9 e0 93 f3 a3 b5 01 00 40 6e 00 00 00 00 00 00 00",
        "hcitool -i hci0 cmd 0x08 0x0009 0d 0c 09 4d 6f 6f 6e 62 6f 61 72 64 20 41",
        "hcitool -i hci0 cmd 0x08 0x0006 80 02 c0 03 00 00 00 00 00 00 00 00 00 07 00"
        ]
        for c in setup_adv:
            os.system("sudo "+ c) 

    def start_adv(self,logger,start=True):
        """
        Start Advertising 
        """
        if start:
            start='01'
            logger.info('start adv')
        else:
            start='00'
            logger.info('stop adv')
        start_adv= "hcitool -i hci0 cmd 0x08 0x000a {}".format(start)
        os.system("sudo " +start_adv) 

    def process_rx(self, unstuffer,logger,ba):
        new_problem_string= unstuffer.process_bytes(ba)
        flags = unstuffer.flags

        if new_problem_string is not None:
            problem= decode_problem_string(new_problem_string, flags)
            print(json.dumps(problem)) # FIXME
            self._sendmessage("/problem", json.dumps(problem)) # FIXME
            unstuffer.flags = []
            self.start_adv(logger)

    def monitor_btmon(self, logger, unstuffer): 
        out_r, out_w = pty.openpty()
        cmd = ["sudo","btmon"]
        process = subprocess.Popen(cmd, stdout=out_w)
        f = OutStream(out_r)
        while True:
            lines, readable = f.read_lines()
            if not readable: break
            for line in lines:                
                if line != '':
                    line = line.decode()
                    if 'Data:' in line:
                        data = line.replace(' ','').replace('\x1b','').replace('[0m','').replace('Data:','')
                        self.process_rx(unstuffer,logger,data)
                        t1 = bytearray.fromhex(data).decode(errors="ignore")
                        logger.info('New data '+ data+ 'and decoded '+t1)


    def main(self,logger,adapter):
        logger.info("Bluetooth adapter: "+ str(adapter))
        
        unstuffer= UnstuffSequence(logger)

        self.setup_adv(logger)
        self.start_adv(logger)
        self.monitor_btmon(logger,unstuffer)

    def _start_mqtt(self):
        # Connect to MQTT
        hostname = "raspi-moonboard" # FIXME
        port = 1883 # FIXME
        self._client = mqtt.Client()
        self._client.connect(hostname, port,60)
        self._sendmessage("/status", "Starting")
 
    def _sendmessage(self, topic="/none", message="None"):
        ttopic = "moonboard/ble"+topic
        mmessage = str(message)
        #logging.debug("MQTT>: " + ttopic + " ###> " + mmessage)
        self._client.publish(ttopic, mmessage)


if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description='Moonboard bluetooth service')
    parser.add_argument('--debug',  action = "store_true")

    args = parser.parse_args()
    argsd=vars(args)

    logger = logging.getLogger('moonboard.ble')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    mbble = MoonboardBLE()
    mbble.main(logger,adapter='/org/bluez/hci0') # FIXME: use configured adapter
