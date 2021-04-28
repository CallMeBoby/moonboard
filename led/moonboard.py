# -*- coding: utf-8 -*-
from bibliopixel.colors import COLORS
from bibliopixel.layout import Strip
from bibliopixel.drivers.PiWS281X import PiWS281X
from bibliopixel.drivers.dummy_driver import DriverDummy
import string
import json
import time

# FIXME: Describe Layouts
# FIXME: Delete this
LED_LAYOUT = {
    'evo': [[17,  18,  53,  54,  89,  90, 125, 126, 161, 162, 197],
            [16,  19,  52,  55,  88,  91, 124, 127, 160, 163, 196],
            [15,  20,  51,  56,  87,  92, 123, 128, 159, 164, 195],
            [14,  21,  50,  57,  86,  93, 122, 129, 158, 165, 194],
            [13,  22,  49,  58,  85,  94, 121, 130, 157, 166, 193],
            [12,  23,  48,  59,  84,  95, 120, 131, 156, 167, 192],
            [11,  24,  47,  60,  83,  96, 119, 132, 155, 168, 191],
            [10,  25,  46,  61,  82,  97, 118, 133, 154, 169, 190],
            [9,  26,  45,  62,  81,  98, 117, 134, 153, 170, 189],
            [8,  27,  44,  63,  80,  99, 116, 135, 152, 171, 188],
            [7,  28,  43,  64,  79, 100, 115, 136, 151, 172, 187],
            [6,  29,  42,  65,  78, 101, 114, 137, 150, 173, 186],
            [5,  30,  41,  66,  77, 102, 113, 138, 149, 174, 185],
            [4,  31,  40,  67,  76, 103, 112, 139, 148, 175, 184],
            [3,  32,  39,  68,  75, 104, 111, 140, 147, 176, 183],
            [2,  33,  38,  69,  74, 105, 110, 141, 146, 177, 182],
            [1,  34,  37,  70,  73, 106, 109, 142, 145, 178, 181],
            [0,  35,  36,  71,  72, 107, 108, 143, 144, 179, 180]]
}


class MoonBoard:
    DEFAULT_PROBLEM_COLORS = {'START': COLORS.green,
                              'TOP': COLORS.red, 'MOVES': COLORS.blue}
    DEFAULT_COLOR = COLORS.blue
    LED_SPACING = 1
    ROWS = 18
    COLS = 11
    NUM_PIXELS = ROWS*COLS
    DEFAULT_BRIGHTNESS = 50
    SETUP = 'Moonboard2016'

    MAPPING = {}

    with open('/home/pi/moonboard/led/led_mapping.json') as json_file:
        data = json.load(json_file)
        MAPPING = data

    def __init__(self, led_layout=None, brightness=DEFAULT_BRIGHTNESS):
        try:
            driver = PiWS281X(self.NUM_PIXELS)  # default GPIO18
        except (ImportError, ValueError) as e:
            print("Not able to initialize the driver. Error{}".format(e))
            print("Use bibliopixel.drivers.dummy_driver")
            driver = DriverDummy(self.NUM_PIXELS)

        self.layout = Strip(driver, threadedUpdate=True, brightness=brightness)

        self.layout.cleanup_drivers()
        self.layout.start()

    def clear(self):
        self.layout.all_off()
        self.layout.push_to_driver()

    def set_hold(self, hold, color=DEFAULT_COLOR):
        self.layout.set(self.MAPPING[hold], color)

    def show_hold(self, hold, color=DEFAULT_COLOR):
        self.set_hold(hold, color)
        self.layout.push_to_driver()

    def show_problem(self, holds, hold_colors={}):
        self.clear()
        for k in ['START', 'MOVES', 'TOP']:
            for hold in holds[k]:
                self.set_hold(
                    hold,
                    hold_colors.get(k, self.DEFAULT_PROBLEM_COLORS[k]),
                )
        self.layout.push_to_driver()

    # run all colors in led´s to see if something is missing
    def led_test(self):
        print('led test')
        duration = 0.4
        COLORS = ['red', 'green', 'blue']

        for color in range(len(COLORS)):
            for i in range(1, self.ROWS+1):
                for j in range(0, self.COLS):
                    columnChar = chr(j+65)
                    hold = columnChar + str(i)
                    print(hold)
                    self.layout.set(self.MAPPING[hold], COLORS[color])
                self.layout.push_to_driver()
                time.sleep(duration)
        time.sleep(1.2)
        self.clear()

    def display_holdset(self, holdset="Hold Set A", duration=10, **kwds):
        print("Display holdset: " + str(holdset))

        with open('../problems/HoldSetup.json') as json_file:  # FIXME: path
            data = json.load(json_file)
            for hold in data[self.SETUP]:
                hs = (data[self.SETUP][hold]['HoldSet'])
                color = COLORS.black

                if (hs == holdset):  # FIXME
                    color = COLORS.green

                self.layout.set(self.MAPPING[hold], color)

                #self.set_hold (hold, color)
                # print "Orientation"

        self.layout.push_to_driver()

        time.sleep(60*10)

        self.clear()

    def led_raho(self):
        print('print word RHAO')
        # R
        for i in [129, 130, 131, 133, 155, 156, 158, 165, 166, 167, 168, 169]:
            self.layout.set(i, 'yellow')
        self.layout.push_to_driver()
        time.sleep(0.4)

        # A
        or i in [21, 22, 23, 24, 25, 48, 50, 57, 58, 59, 60, 61]:
            self.layout.set(i, 'blue')
        self.layout.push_to_driver()
        time.sleep(0.4)

        # H
        or i in [136, 137, 138, 139, 140, 149, 172, 173, 174, 175, 176]:
            self.layout.set(i, 'red')
        self.layout.push_to_driver()
        time.sleep(0.4)

        # O
        or i in [28, 29, 30, 31, 32, 39, 43, 64, 65, 66, 67, 68]:
            self.layout.set(i, 'white')
        self.layout.push_to_driver()
        time.sleep(0.4)

        time.sleep(1.2)
        self.clear()
