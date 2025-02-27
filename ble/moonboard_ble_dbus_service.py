import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from gatt_base.gatt_lib_advertisement import Advertisement
from gatt_base.gatt_lib_characteristic import Characteristic
from gatt_base.gatt_lib_service import Service
import string,json
import subprocess
import logging
from moonboard_app_protocol import UnstuffSequence, decode_problem_string
import paho.mqtt.client as mqtt

import os
import threading
import pty
 
BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
LOCAL_NAME =                   'Moonboard A'
SERVICE_NAME=                  'com.moonboard'
mainloop = None

class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service, process_rx):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)
        self.process_rx=process_rx

    def WriteValue(self, value, options):
        pass
        #self.process_rx(value)

class UartService(Service):
    def __init__(self, bus,path, index, process_rx):
        Service.__init__(self, bus,path, index, UART_SERVICE_UUID, True)
        self.add_characteristic(RxCharacteristic(bus, 1, self, process_rx))       

class OutStream:
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


class MoonApplication(dbus.service.Object):
    IFACE = "com.moonboard.method"
    def __init__(self, bus, socket,logger):
        self._start_mqtt()
        self.path = '/com/moonboard'
        self.services = []
        self.logger=logger
        self.unstuffer= UnstuffSequence(self.logger)
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(UartService(bus,self.get_path(), 0, self.process_rx)) 

        monitor_thread = threading.Thread(target=self.monitor_btmon)  
        monitor_thread.start()

    def monitor_btmon(self): 
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
                        self.process_rx(data)
                        self.logger.debug('New data '+ data)

    def process_rx(self,ba):
        new_problem_string= self.unstuffer.process_bytes(ba)
        flags = self.unstuffer.flags

        if new_problem_string is not None:
            self.logger.debug('Before decode->'+ new_problem_string)
            problem=decode_problem_string(new_problem_string, flags)
            self.new_problem(json.dumps(problem))
            self._sendmessage("/problem", json.dumps(problem)) # FIXME
            self.unstuffer.flags = []
            start_adv(self.logger)

    @dbus.service.signal(dbus_interface="com.moonboard",
                            signature="s")
    def new_problem(self, problem):
        self.logger.debug('Signal new problem: '+ str(problem))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response
    
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

def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def run(*popenargs, **kwargs):
    input = kwargs.pop("input", None)
    check = kwargs.pop("handle", False)

    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    try:
        stdout, stderr = process.communicate(input)
    except:
        process.kill()
        process.wait()
        raise
    retcode = process.poll()
    if check and retcode:
        raise subprocess.CalledProcessError(
            retcode, process.args, output=stdout, stderr=stderr)
    return retcode, stdout, stderr


def setup_adv(logger):
    logger.debug('setup adv')
    setup_adv = [
    "hcitool -i hci0 cmd 0x08 0x000a 00",
    "hcitool -i hci0 cmd 0x08 0x0008 18 02 01 06 02 0a 00 11 07 9e ca dc 24 0e e5 a9 e0 93 f3 a3 b5 01 00 40 6e 00 00 00 00 00 00 00",
    "hcitool -i hci0 cmd 0x08 0x0009 0d 0c 09 4d 6f 6f 6e 62 6f 61 72 64 20 41",
    "hcitool -i hci0 cmd 0x08 0x0006 80 02 c0 03 00 00 00 00 00 00 00 00 00 07 00"
    ]
    for c in setup_adv:
        run("sudo "+ c, shell=True)


def start_adv(logger,start=True):
    if start:
        start='01'
        logger.debug('start adv')
    else:
        start='00'
        logger.debug('stop adv')
    start_adv= "hcitool -i hci0 cmd 0x08 0x000a {}".format(start)
    run("sudo " +start_adv, shell=True)

def main(logger,adapter):
    global mainloop

    logger.debug("Bluetooth adapter: "+ str(adapter))

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    try:
        bus_name = dbus.service.BusName(SERVICE_NAME,
                                        bus=bus,
                                        do_not_queue=True)
    except dbus.exceptions.NameExistsException:
        sys.exit(1)

    app = MoonApplication(bus_name,None,logger)    

    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)

 
    loop = GLib.MainLoop()

    logger.debug('app path: '+ app.get_path())

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    
    setup_adv(logger)
    start_adv(logger)

    # Run the loop
    try:
        loop.run()
    except KeyboardInterrupt:
        print("keyboard interrupt received")
    except Exception as e:
        print("Unexpected exception occurred: '{}'".format(str(e)))
    finally:
        loop.quit()
 
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

    main(logger,adapter='/org/bluez/hci0')
