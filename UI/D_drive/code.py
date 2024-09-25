import gc
import time
import displayio
import picodvi
import board
import framebufferio
import terminalio
import digitalio  # For handling button input
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle

# Pin defs for DVI Sock
displayio.release_displays()

fb = picodvi.Framebuffer(320, 240,
    clk_dp=board.GP14, clk_dn=board.GP15,
    red_dp=board.GP12, red_dn=board.GP13,
    green_dp=board.GP18, green_dn=board.GP19,
    blue_dp=board.GP16, blue_dn=board.GP17,
    color_depth=8)
display = framebufferio.FramebufferDisplay(fb, rotation=270)

# Colors
white = 0xffffff
gray = 0x4C4C4C
yellow = 0xcccc00
pink = 0xff00ff
blue = 0x0000ff

group = displayio.Group()

# Setup for 5-way select button
select = digitalio.DigitalInOut(board.GP6)
select.direction = digitalio.Direction.INPUT
select.pull = digitalio.Pull.UP  

#  Up and Down button pins
note_pins = [board.GP7, board.GP8]
note_buttons = []
for pin in note_pins:
    note_pin = digitalio.DigitalInOut(pin)
    note_pin.direction = digitalio.Direction.INPUT
    note_pin.pull = digitalio.Pull.UP
    note_buttons.append(note_pin)

#  note states
note0_pressed = False
note1_pressed = False

#  array of note states
note_states = [note0_pressed, note1_pressed]

def clean_up(group_name):
    for _ in range(len(group_name)):
        group_name.pop()
    gc.collect()

def update_content(next_page, current_page):
    if next_page == 2 and current_page == 1:
        group.append(tri1)
    elif next_page == 3 and current_page == 2:
        group.remove(tri2)
    elif next_page == 2 and current_page == 3:
        group.append(tri2)
    elif next_page == 1 and current_page == 2:
        group.remove(tri1)
    
    text.text = "Option " + str(next_page)
    
    gc.collect()
    return next_page  

def initialize_page():
    cx = int((display.width) / 2)
    cy = int((display.height) / 2)
    minor = min(cx, cy)
    pad = 100
    size = minor - pad
    global text, tri1, tri2, rnd
    # Create RoundRect and Triangles
    rnd = RoundRect(cx - 100, cy - 130, 200, 20, int(size / 5), stroke=1, fill=gray, outline=yellow)
    tri1 = Triangle(cx - 40, cy - 140, cx, cy - 150, cx + 40, cy - 140, fill=pink, outline=blue)
    tri2 = Triangle(cx - 40, cy - 100, cx, cy - 90, cx + 40, cy - 100, fill=pink, outline=blue)
    
    text = label.Label(terminalio.FONT, text="Page 1", color=white)
    text.anchor_point = (0.5, 0.5)
    text.anchored_position = (120, 40)
    
    # Add the shapes to the group
    group.append(rnd)
    group.append(tri2)
    group.append(text)

    return text

def main_loop():
    current_page = 1
    next_page = 1
    
    initialize_page()
    
    while True:
        time.sleep(2)
        next_page = 2
        current_page = update_content(next_page, current_page)
        time.sleep(2)
        next_page = 3
        current_page = update_content(next_page, current_page)
        time.sleep(2)
        next_page = 2
        current_page = update_content(next_page, current_page)
        time.sleep(2)
        next_page = 1
        current_page = update_content(next_page, current_page)
        time.sleep(2)

# Set root group once, before entering the main loop
display.root_group = group

# Start the main loop
main_loop()

