# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
# SPDX-FileCopyrightText: Adapted from Phil B.'s 16bit_hello Arduino Code
#
# SPDX-License-Identifier: MIT

import gc
import math
from random import randint
import time
import displayio
import picodvi
import board
import framebufferio
import vectorio
import terminalio
import simpleio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_lines
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_touchscreen import Touchscreen

# pin defs for DVI Sock
displayio.release_displays()

fb = picodvi.Framebuffer(320, 240,
	clk_dp=board.GP14, clk_dn=board.GP15,
	red_dp=board.GP12, red_dn=board.GP13,
	green_dp=board.GP18, green_dn=board.GP19,
	blue_dp=board.GP16, blue_dn=board.GP17,
	color_depth=8)
display = framebufferio.FramebufferDisplay(fb, rotation=270)

bitmap = displayio.Bitmap(display.width, display.height, 3)

red = 0xff0000
yellow = 0xcccc00
orange = 0xff5500
blue = 0x0000ff
pink = 0xff00ff
purple = 0x5500ff
white = 0xffffff
green =  0x00ff00
aqua = 0x125690
gray = 0x4C4C4C

palette = displayio.Palette(3)
palette[0] = 0x000000 # black
palette[1] = white
palette[2] = yellow

palette.make_transparent(0)

tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

group = displayio.Group()

def clean_up(group_name):
    for _ in range(len(group_name)):
        group_name.pop()
    gc.collect()

def initialize_shapes():
    cx = int((display.width) / 2)
    cy = int((display.height) / 2)
    minor = min(cx, cy)
    pad = 100
    size = minor - pad
    half = int(size / 2)
    print(display.width)
    print(display.height)

    # Create RoundRect and Triangle
    rnd = RoundRect(cx-100 , cy -130, 200, 20, int(size / 5), stroke=1, fill=gray, outline=yellow)
    tri1 = Triangle(cx-40, cy-140, cx, cy - 150, cx + 40, cy-140, fill=pink, outline=blue)
    tri2 = Triangle(cx-40, cy-100, cx, cy - 90, cx + 40, cy-100, fill=pink, outline=blue)
    TEXT = "Testing ----"
    text = label.Label(terminalio.FONT, text=TEXT,color=white)
    text.anchor_point = (0.5, 0.5)
    text.anchored_position = (120, 40)
    
    # Add the shapes to the group
    group.append(rnd)
    group.append(tri1)
    group.append(tri2)
    group.append(text)

    return rnd, tri1, tri2 

def main_loop():
    rnd, tri1, tri2 = initialize_shapes() # Initialization

    while True:
        gc.collect()  # Free up memory

# Set root group once, before entering the main loop
display.root_group = group


# Start the main loop
main_loop()



