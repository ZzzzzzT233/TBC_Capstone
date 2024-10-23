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
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.triangle import Triangle
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
import busio
import adafruit_ssd1327
import digitalio

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
#  button pins, all pins in order skipping GP15
note_pins = [
    #board.GP7,
    #board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    #board.GP12,
    #board.GP13,
    #board.GP14,
    #board.GP16,
    #board.GP17,
    #board.GP18,
    #board.GP19,
    board.GP20,
    board.GP21,
    board.GP22,
    board.GP26,
]

note_buttons = []

for pin in note_pins:
    note_pin = digitalio.DigitalInOut(pin)
    note_pin.direction = digitalio.Direction.INPUT
    note_pin.pull = digitalio.Pull.UP
    note_buttons.append(note_pin)

#  note states
note0_pressed = False
note1_pressed = False
note2_pressed = False
note3_pressed = False
note4_pressed = False
note5_pressed = False
note6_pressed = False
note7_pressed = False
note8_pressed = False
note9_pressed = False
note10_pressed = False
note11_pressed = False
note12_pressed = False
note13_pressed = False
note14_pressed = False
note15_pressed = False
#  array of note states
note_states = [
    note0_pressed,
    note1_pressed,
    note2_pressed,
    note3_pressed,
    note4_pressed,
    note5_pressed,
    note6_pressed,
    note7_pressed,
    note8_pressed,
    note9_pressed,
    note10_pressed,
    note11_pressed,
    note12_pressed,
    note13_pressed,
    note14_pressed,
    note15_pressed,
]
#  default midi number
midi_num = 60
#  default MIDI button
button_num = 0
#  default MIDI button position
button_pos = 0
#  check for blinking LED
led_check = None
#  time.monotonic() device
clock = time.monotonic()

#  array of default MIDI notes
midi_notes = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]

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

up_button = digitalio.DigitalInOut(board.GP7)
up_button.direction = digitalio.Direction.INPUT
up_button.pull = digitalio.Pull.UP
down_button = digitalio.DigitalInOut(board.GP8)
down_button.direction = digitalio.Direction.INPUT
down_button.pull = digitalio.Pull.UP

global option

option = {
    1: 'Traditional mode',
    2: 'Chord mode',
    3: 'Strum mode'}

def switch_option(page):
    return option.get(page, 'Invalid Option')


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
    
    text.text = switch_option(next_page)
    
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
    bg = Rect(0, 0, display.width, display.height, fill=0x5069a5)
    rnd = RoundRect(cx - 100, cy - 130, 200, 20, int(size / 5), stroke=1, fill=gray, outline=yellow)
    tri1 = Triangle(cx - 40, cy - 140, cx, cy - 150, cx + 40, cy - 140, fill=pink, outline=blue)
    tri2 = Triangle(cx - 40, cy - 100, cx, cy - 90, cx + 40, cy - 100, fill=pink, outline=blue)
    text = label.Label(terminalio.FONT, text="Traditional mode", color=white)

    text.anchor_point = (0.5, 0.5)
    text.anchored_position = (120, 40)
    
    # Add the shapes to the group
    group.append(bg)
    group.append(rnd)
    group.append(tri2)
    group.append(text)
    
    rect_width = 40  
    rect_height = 30  
    margin_x = 10  
    margin_y = 30
    
    start_x = (display.width - (rect_width * 4 + margin_x * 3)) // 2
    start_y = display.height - rect_height * 3 - margin_y * 2 - 40 
    
    for row in range(3):
        for col in range(4):
            x = start_x + col * (rect_width + margin_x)
            y = start_y + row * (rect_height + margin_y)
            rect = Rect(x, y, rect_width, rect_height, fill=white)
            group.append(rect)

    return text

def modify_mode(text_obj, group, tri1, tri2, mode_text):
    text_obj.text = mode_text
    if tri1 in group:
        group.remove(tri1)
    if tri2 in group:
        group.remove(tri2)
    gc.collect()
    return True

def main_loop():
    current_page = 1
    next_page = 1

    initialize_page()
    selected = False
    modified = False

    while True:
        if not selected:
            if not up_button.value:
                if next_page > 1:
                    next_page -= 1
                current_page = update_content(next_page, current_page)
                time.sleep(0.5)
            
            if not down_button.value:
                if next_page < 3:
                    next_page += 1
                current_page = update_content(next_page, current_page)
                time.sleep(0.5)
            
            if not select.value:
                selected = True
                time.sleep(0.5)
        else:
            if current_page == 1:
                if not modified:
                    modified = modify_mode(text, group, tri1, tri2, "Regular mode selected")
                # implement regular mode functions
            elif current_page == 2:
                pass
            elif current_page == 3:
                if not modified:
                    modified = modify_mode(text, group, tri1, tri2, "Strum mode selected")
        for i in range(7):
            buttons = note_buttons[i]
            #  if button is pressed...
            if not buttons.value and note_states[i] is False:
                #  send the MIDI note and light up the LED
                #midi.send(NoteOn(midi_notes[i], 120))
                midi.send(NoteOn(60, 120))
                midi.send(NoteOn(64, 120))
                midi.send(NoteOn(67, 120))
                note_states[i] = True
            #  if the button is released...
            if buttons.value and note_states[i] is True:
                #  stop sending the MIDI note and turn off the LED
                #midi.send(NoteOff(midi_notes[i], 120))
                midi.send(NoteOff(60, 120))
                midi.send(NoteOff(64, 120))
                midi.send(NoteOff(67, 120))
                note_states[i] = False

# Set root group once, before entering the main loop
display.root_group = group

# Start the main loop
main_loop()


