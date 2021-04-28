#!/usr/bin/python
# This script is used to create the arrays for the LED layouts if using redily available led string with 10cm spacing between LEDs

import json

MAPPING = {}

ROWS = 18  
COLS = 11
LED_SPACING = 1

print ("Create ZigZag path for leds")
led_number = 0
layout = [[0 for i in range(COLS)] for j in range(ROWS)]  

for c in range (COLS - 1, -1, -1):
    for r in range (0, ROWS):
        hold = ""
        if (c % 2) == 0:
            hold = (chr(c+65)+str(r+1))
        else:
            hold = (chr(c+65)+str(ROWS-r))
        print (hold, c,r,led_number)
        MAPPING [hold] = led_number
        led_number = led_number + LED_SPACING

print (MAPPING) 

outfile = "led_mapping.json"
with open(outfile, 'w') as f:
  json.dump(MAPPING, f, ensure_ascii=False)    