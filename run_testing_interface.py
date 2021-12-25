# -*- coding: utf-8 -*-
import argparse
from led.moonboard import MoonBoard,LED_LAYOUT
from gi.repository import GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from functools import partial
import json 
import json
import RPi.GPIO as GPIO
import os
#import signal
import sys
import logging

# external power LED and power button
LED_GPIO = 26
BUTTON_GPIO = 3

# Main stuff
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--driver_type',
                        help='driver type, depends on leds and device controlling the led.',
                        choices=['PiWS281x', 'WS2801', 'SimPixel'],
                        default='WS2801')

    parser.add_argument('--brightness',  default=100, type=int)

    parser.add_argument('--led_layout',  
                        default=None, 
                        choices=list(LED_LAYOUT.keys())
                        )

    parser.add_argument('--debug',  action = "store_true")


    args = parser.parse_args()
    argsd=vars(args)
    logger = logging.getLogger('run')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    #problems
    led_layout = LED_LAYOUT.get(args.led_layout) if args.led_layout is not None else None
    MOONBOARD = MoonBoard(args.driver_type, led_layout)

    holds = {} 
    holds ["START"] = "K1"
    holds ["MOVES"] = ["B2", "B5"] 
    holds ["TOP"] = "K7"
    #MOONBOARD.show_problem(holds)
    MOONBOARD.show_hold("A4")
