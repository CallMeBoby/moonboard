{"START": ["E4", "H3"], "MOVES": ["E8", "B13", "A16", "A11"], "TOP": ["D18"], "FLAGS": [""]}
start adv
< HCI Command: ogf 0x08, ocf 0x000a, plen 1
  01 
> HCI Event: 0x0e plen 4
  01 0A 20 0C 
New data 31352c5031302c45353423
New data dec? 15,P10,E54#


Traceback (most recent call last):
  File "moon_ble_mqtt_proto.py", line 165, in <module>
    mbble.main(logger,adapter='/org/bluez/hci0') # FIXME: use configured adapter
  File "moon_ble_mqtt_proto.py", line 129, in main
    self.monitor_btmon(logger,unstuffer)
  File "moon_ble_mqtt_proto.py", line 116, in monitor_btmon
    self.process_rx(unstuffer,logger,data)
  File "moon_ble_mqtt_proto.py", line 93, in process_rx
    new_problem_string= unstuffer.process_bytes(ba)
  File "/home/bob/moonboard/ble/moonboard_app_protocol.py", line 54, in process_bytes
    s = bytearray.fromhex(ba).decode()
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 2: invalid start byte
