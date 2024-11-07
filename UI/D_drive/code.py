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

keys = [
    "C major", "C minor", "D major", "D minor", "E major", "E minor",
    "F major", "F minor", "G major", "G minor", "A major", "A minor",
    "B major", "B minor"
]

guitar_keys = ["C major", "D major", "E major", "F major", "G major","A major", "B major"]

chords = {
    "C major": ["Em", "Am", "Dm", "G", "C", "F", "E", "A", "D", "G", "C", "F"],
    "D major": ["F#m", "Bm", "Em", "A", "D", "G", "F#", "B", "E", "A", "D", "G"],
    "E major": ["G#m", "C#m", "F#m", "B", "E", "A", "G#", "C#", "F#", "B", "E", "A"],
    "F major": ["Am", "Dm", "Gm", "C", "F", "Bb", "A", "D", "G", "C", "F", "Bb"],
    "G major": ["Bm", "Em", "Am", "D", "G", "C", "B", "E", "A", "D", "G", "C"],
    "A major": ["C#m", "F#m", "Bm", "E", "A", "D", "C#", "F#", "B", "E", "A", "D"],
    "B major": ["D#m", "G#m", "C#m", "F#", "B", "E", "D#", "G#", "C#", "F#", "B", "E"],

    "C minor": ["Eb", "Ab", "Ddim", "G", "Cm", "Fm", "Eb", "Ab", "D", "G", "C", "F"],
    "D minor": ["F", "Bb", "Edim", "A", "Dm", "Gm", "F", "Bb", "E", "A", "D", "G"],
    "E minor": ["G", "C", "F#dim", "B", "Em", "Am", "G", "C", "F#", "B", "E", "A"],
    "F minor": ["Ab", "Db", "Gdim", "Cm", "Fm", "Bbm", "Ab", "Db", "G", "C", "F", "Bb"],
    "G minor": ["Bb", "Eb", "Adim", "D", "Gm", "Cm", "Bb", "Eb", "A", "D", "G", "C"],
    "A minor": ["C", "F", "Bdim", "E", "Am", "Dm", "C", "F", "B", "E", "A", "D"],
    "B minor": ["D", "G", "C#dim", "F#", "Bm", "Em", "D", "G", "C#", "F#", "B", "E"]
}

guitar_chord = {
    "C major": ["C", "Dm", "Em", "F", "FG", "Am", "G7"],
    "D major": ["D", "Em", "F#m", "G", "A", "Em", "A7"],
    "E major": ["E", "F#m", "G#m", "A", "B", "C#m", "B7"],
    "F major": ["F", "Gm", "Am", "Bb", "C", "Dm", "C7"],
    "G major": ["G", "Am", "Bm", "C", "D", "Em", "D7"],
    "A major": ["A", "Bm", "C#m", "D", "E", "F#m", "E7"],
    "B major": ["B", "C#m", "D#m", "E", "F#", "G#m", "F#7"]
}

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
row_colors = [0xf15bb5, 0xff5400, 0x9b5de5]

group = displayio.Group()

# Setup for 5-way select button
select = digitalio.DigitalInOut(board.GP6)
select.direction = digitalio.Direction.INPUT
select.pull = digitalio.Pull.UP

# Setup for 5-way Up and down button
up_button = digitalio.DigitalInOut(board.GP7)
up_button.direction = digitalio.Direction.INPUT
up_button.pull = digitalio.Pull.UP
down_button = digitalio.DigitalInOut(board.GP8)
down_button.direction = digitalio.Direction.INPUT
down_button.pull = digitalio.Pull.UP

# Setup for 5-way exit button
exit_button = digitalio.DigitalInOut(board.GP5)
exit_button.direction = digitalio.Direction.INPUT
exit_button.pull = digitalio.Pull.UP

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

def update_mode(next_page, current_page):
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

def update_key_selection(next_key_index, current_key_index):
    global tri1, tri2, text
    if next_key_index == 0 and current_key_index == 1:
        group.remove(tri1)
    elif next_key_index == 1 and current_key_index == 0:
        group.append(tri1)
    elif next_key_index == 12 and current_key_index == 13:
        group.append(tri2)
    elif next_key_index == 13 and current_key_index == 12:
        group.remove(tri2)
    text.text = keys[next_key_index]
    gc.collect()
    return next_key_index

def update_guitar_key_selection(next_key_index, current_key_index):
    global tri1, tri2, text
    if next_key_index == 0 and current_key_index == 1:
        group.remove(tri1)
    elif next_key_index == 1 and current_key_index == 0:
        group.append(tri1)
    elif next_key_index == 5 and current_key_index == 6:
        group.append(tri2)
    elif next_key_index == 6 and current_key_index == 5:
        group.remove(tri2)
    text.text = guitar_keys[next_key_index]
    gc.collect()
    return next_key_index

def update_guitar_chord_selection(next_chord_index, current_chord_index, strum_key):
    global tri1, tri2, text
    if next_chord_index == 0 and current_chord_index == 1:
        group.remove(tri1)
    elif next_chord_index == 1 and current_chord_index == 0:
        group.append(tri1)
    elif next_chord_index == 5 and current_chord_index == 6:
        group.append(tri2)
    elif next_chord_index == 6 and current_chord_index == 5:
        group.remove(tri2)
    text.text = guitar_chord[strum_key][next_chord_index]
    gc.collect()
    return next_chord_index

def display_chords_for_key(selected_key):
    if tri1 in group:
        group.remove(tri1)
    if tri2 in group:
        group.remove(tri2)
    chord_text_list = chords[selected_key]
    for i in range(len(chord_label_list)):
        chord_label_list[i].text = chord_text_list[i]
        chord_label_list[i].color = white
    gc.collect()


def initialize_page():
    cx = int((display.width) / 2)
    cy = int((display.height) / 2)
    minor = min(cx, cy)
    pad = 100
    size = minor - pad

    global text, text1, text2, text3, tri1, tri2, rnd, grid_rects, chord_label_list

    grid_rects = [[], [], []]

    # Create RoundRect and Triangles
    bg = Rect(0, 0, display.width, display.height, fill=white)
    rnd = RoundRect(cx - 100, cy - 130, 200, 20, int(size / 5), stroke=1, fill=0x5a189a, outline=0xe0aaff)
    tri1 = Triangle(cx - 40, cy - 140, cx, cy - 150, cx + 40, cy - 140, fill=0xff99c8, outline=0x8338ec)
    tri2 = Triangle(cx - 40, cy - 100, cx, cy - 90, cx + 40, cy - 100, fill=0xff99c8, outline=0x8338ec)
    text = label.Label(terminalio.FONT, text="Traditional mode", color=0xffc8dd)
    text1 = label.Label(terminalio.FONT, text="", color=0xf15bb5)
    text2 = label.Label(terminalio.FONT, text="", color=0xff5400)
    text3 = label.Label(terminalio.FONT, text="", color=0x9b5de5)

    chord_label_list = []

    text.anchor_point = (0.5, 0.5)
    text.anchored_position = (120, 40)

    text1.anchor_point = (0.5, 0.5)
    text1.anchored_position = (50, 100)

    text2.anchor_point = (0.5, 0.5)
    text2.anchored_position = (120, 100)

    text3.anchor_point = (0.5, 0.5)
    text3.anchored_position = (190, 100)
    # Add the shapes to the group
    group.append(bg)
    group.append(rnd)
    group.append(tri2)
    group.append(text)
    group.append(text1)
    group.append(text2)
    group.append(text3)

    rect_width = 56
    rect_height = 44
    margin_x = 7
    margin_y = 24

    start_x = (display.width - (rect_width * 4 + margin_x * 3)) // 2
    start_y = display.height - rect_height * 3 - margin_y * 2

    for row in range(3):
        for col in range(4):
            x = start_x + col * (rect_width + margin_x)
            y = start_y + row * (rect_height + margin_y)
            rect = Rect(x, y, rect_width, rect_height, fill=0x4f518c)
            group.append(rect)
            grid_rects[row].append(rect)

            chord_index = row * 4 + col
            chord_text = ""
            text_label = label.Label(terminalio.FONT, text=chord_text)
            text_label.anchor_point = (0.5, 0.5)
            text_label.anchored_position = (x + rect_width / 2, y + rect_height / 2)
            group.append(text_label)
            chord_label_list.append(text_label)
    gc.collect()
    return text

def add_outline(fill_color, outline_colors, rect_width=56, rect_height=44, margin_x=7, margin_y=24):

    start_x = (display.width - (rect_width * 4 + margin_x * 3)) // 2
    start_y = display.height - rect_height * 3 - margin_y * 2
    for row_index, rects in enumerate(grid_rects):
        if row_index == count-1:
            for col, rect in enumerate(rects):
                x = start_x + col * (rect_width + margin_x)
                y = start_y + row_index * (rect_height + margin_y)
                group.remove(rect)
                new_rect = Rect(x, y, rect_width, rect_height, fill=fill_color, outline=outline_colors[row_index], stroke=3)
                group.append(new_rect)
                grid_rects[row_index][col] = new_rect
        gc.collect()


def modify_mode(text_obj, group, tri1, tri2, mode_text):
    text_obj.text = mode_text
    if tri1 in group:
        group.remove(tri1)
    if tri2 in group:
        group.remove(tri2)
    if mode_text == "Strum mode selected":
        add_outline(fill_color=0x4f518c, outline_colors=row_colors)
    return True

def initialize_chord(tri1, tri2, text):
    if text.text == "Chord mode" or text.text == "Strum mode":
        text.text = "Select the Key"
        time.sleep(1)
        text.text = "C major"
        if tri1 in group:
            group.remove(tri1)
        if tri2 not in group:
            group.append(tri2)
    gc.collect()


def initialize_strum_chord(tri1, tri2, text):
    global strum_key
    if text.text in guitar_chord.keys():
        strum_key = text.text
        text.text = "Select the Chord"
        time.sleep(1)
        text.text = guitar_chord[strum_key][0]
        if tri1 in group:
            group.remove(tri1)
        if tri2 not in group:
            group.append(tri2)
    gc.collect()

def main_loop():
    global key_selected
    global count
    global strum_key
    strum_key = ""
    count = 0
    current_page = 1
    next_page = 1
    initialize_page()
    selected = False
    modified = False
    key_selected = False
    current_key_index = 0
    next_key_index = 0
    strum_chord_selected = False
    current_chord_index = 0
    next_chord_index = 0

    while True:
        if not selected:
            if not up_button.value:
                if next_page > 1:
                    next_page -= 1
                current_page = update_mode(next_page, current_page)
                time.sleep(0.3)

            if not down_button.value:
                if next_page < 3:
                    next_page += 1
                current_page = update_mode(next_page, current_page)
                time.sleep(0.3)

            if not select.value:
                selected = True
                time.sleep(0.3)
        else:
            if current_page == 1:
                if not modified:
                    modified = modify_mode(text, group, tri1, tri2, "Regular mode selected")
            elif current_page == 2:
                if not key_selected:
                    initialize_chord(tri1,tri2, text)
                    if not up_button.value:
                        if next_key_index > 0:
                            next_key_index -= 1
                            current_key_index = update_key_selection(next_key_index, current_key_index)
                            time.sleep(0.3)
                    if not down_button.value:
                        if next_key_index < 13:
                            next_key_index += 1
                            current_key_index = update_key_selection(next_key_index, current_key_index)
                            time.sleep(0.3)
                    if not select.value:

                        key_selected = True
                        selected_key = keys[current_key_index]
                        display_chords_for_key(selected_key)
                        time.sleep(0.3)
            elif current_page == 3:
                if not key_selected:
                    initialize_chord(tri1,tri2, text)
                    if not up_button.value:
                        if next_key_index > 0:
                            next_key_index -= 1
                            current_key_index = update_guitar_key_selection(next_key_index, current_key_index)
                            time.sleep(0.3)
                    if not down_button.value:
                        if next_key_index < 6:
                            next_key_index += 1
                            current_key_index = update_guitar_key_selection(next_key_index, current_key_index)
                            time.sleep(0.3)
                    if not select.value:
                        key_selected = True
                        selected_key = keys[current_key_index]
                        time.sleep(0.3)

                else:
                    initialize_strum_chord(tri1,tri2, text)
                    if count < 3:
                        if not up_button.value:
                            if next_chord_index > 0:
                                next_chord_index -= 1
                                next_chord_index -= 1
                                print("test 1")
                                current_chord_index = update_guitar_chord_selection(next_chord_index, current_chord_index,strum_key)
                                time.sleep(0.3)
                        if not down_button.value:
                            if next_chord_index < 6:
                                next_chord_index += 1
                                print("test2")
                                print("Test1 strum key value: ", strum_key)
                                current_chord_index = update_guitar_chord_selection(next_chord_index, current_chord_index, strum_key)
                                time.sleep(0.3)
                        if not select.value:
                            count+=1
                            print(count)
                            time.sleep(0.3)
                            if (count == 1):
                                text1.text = guitar_chord[strum_key][current_chord_index]
                                add_outline(fill_color=0x4f518c, outline_colors=row_colors)
                            elif (count == 2):
                                text2.text = guitar_chord[strum_key][current_chord_index]
                                add_outline(fill_color=0x4f518c, outline_colors=row_colors)
                            elif (count == 3):
                                text3.text = guitar_chord[strum_key][current_chord_index]
                                add_outline(fill_color=0x4f518c, outline_colors=row_colors)
                            gc.collect()



                #if not modified:
                    #modified = modify_mode(text, group, tri1, tri2, "Strum mode selected")
            if not exit_button.value:
                current_page = 1
                next_page = 1
                clean_up(group)
                gc.collect()
                initialize_page()
                selected = False
                modified = False
                key_selected = False
                current_key_index = 0
                next_key_index = 0
                time.sleep(0.3)
                count = 0
                next_chord_index = 0
                current_chord_index = 0
                strum_key = ""


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

