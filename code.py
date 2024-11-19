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
from adafruit_display_shapes.rect import Rect
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.stop import Stop
import busio
import adafruit_ssd1327
import digitalio

keys = [
    "C major",
    "C minor",
    "D major",
    "D minor",
    "E major",
    "E minor",
    "F major",
    "F minor",
    "G major",
    "G minor",
    "A major",
    "A minor",
    "B major",
    "B minor",
]

guitar_keys = [
    "C major",
    "D major",
    "E major",
    "F major",
    "G major",
    "A major",
    "B major",
]

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
    "B minor": ["D", "G", "C#dim", "F#", "Bm", "Em", "D", "G", "C#", "F#", "B", "E"],
}

guitar_chord = {
    "C major": ["C", "Dm", "Em", "F", "G", "Am", "G7"],
    "D major": ["D", "Em", "F#m", "G", "A", "Em", "A7"],
    "E major": ["E", "F#m", "G#m", "A", "B", "C#m", "B7"],
    "F major": ["F", "Gm", "Am", "Bb", "C", "Dm", "C7"],
    "G major": ["G", "Am", "Bm", "C", "D", "Em", "D7"],
    "A major": ["A", "Bm", "C#m", "D", "E", "F#m", "E7"],
    "B major": ["B", "C#m", "D#m", "E", "F#", "G#m", "F#7"],
}

note_to_midi = {
    "C": 60,
    "C#": 61,
    "Db": 61,
    "D": 62,
    "D#": 63,
    "Eb": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "Gb": 66,
    "G": 67,
    "G#": 68,
    "Ab": 68,
    "A": 69,
    "A#": 70,
    "Bb": 70,
    "B": 71,
}

chord_intervals = {
    "maj": [0, 4, 7],  # Major triad
    "min": [0, 3, 7],  # Minor triad
    "dim": [0, 3, 6],  # Diminished triad
    "aug": [0, 4, 8],  # Augmented triad
    "7": [0, 4, 7, 10],  # Dominant 7th: Root, Major 3rd, Perfect 5th, Minor 7th
}

default_midi_notes = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
note_pins = [
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP20,
    board.GP21,
    board.GP22,
    board.GP26,
    board.GP27,
]

note_buttons = []

midi_notes_list = []

strum_notes_list = []

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
midi_num = 60
button_num = 0
button_pos = 0
led_check = None
clock = time.monotonic()
displayio.release_displays()

fb = picodvi.Framebuffer(
    320,
    240,
    clk_dp=board.GP14,
    clk_dn=board.GP15,
    red_dp=board.GP12,
    red_dn=board.GP13,
    green_dp=board.GP18,
    green_dn=board.GP19,
    blue_dp=board.GP16,
    blue_dn=board.GP17,
    color_depth=8,
)
display = framebufferio.FramebufferDisplay(fb, rotation=270)

# Colors
white = 0xFFFFFF
gray = 0x4C4C4C
yellow = 0xCCCC00
pink = 0xFF00FF
blue = 0x0000FF
row_colors = [0xF15BB5, 0xFF5400, 0x9B5DE5]

group = displayio.Group()

select = digitalio.DigitalInOut(board.GP4)
select.direction = digitalio.Direction.INPUT
select.pull = digitalio.Pull.UP

up_button = digitalio.DigitalInOut(board.GP0)
up_button.direction = digitalio.Direction.INPUT
up_button.pull = digitalio.Pull.UP
down_button = digitalio.DigitalInOut(board.GP2)
down_button.direction = digitalio.Direction.INPUT
down_button.pull = digitalio.Pull.UP

exit_button = digitalio.DigitalInOut(board.GP1)
exit_button.direction = digitalio.Direction.INPUT
exit_button.pull = digitalio.Pull.UP

global option

option = {1: "Traditional mode", 2: "Chord mode", 3: "Strum mode"}


def switch_option(page):
    return option.get(page, "Invalid Option")


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

    #bg = Rect(0, 0, display.width, display.height, fill=white)
    rnd = Rect(cx - 75, cy - 130, 155, 20, fill=0x5A189A, outline=0xE0AAFF)
    tri1 = Triangle(
        cx - 10,
        cy - 140,
        cx,
        cy - 145,
        cx + 10,
        cy - 140,
        fill=0xFF99C8,
        outline=0x8338EC,
    )
    tri2 = Triangle(
        cx - 10,
        cy - 100,
        cx,
        cy - 95,
        cx + 10,
        cy - 100,
        fill=0xFF99C8,
        outline=0x8338EC,
    )
    text = label.Label(terminalio.FONT, text="Traditional mode", color=0xFFC8DD)
    text1 = label.Label(terminalio.FONT, text="", color=0xF15BB5)
    text2 = label.Label(terminalio.FONT, text="", color=0xFF5400)
    text3 = label.Label(terminalio.FONT, text="", color=0x9B5DE5)

    chord_label_list = []

    text.anchor_point = (0.5, 0.5)
    text.anchored_position = (120, 40)

    text1.anchor_point = (0.5, 0.5)
    text1.anchored_position = (50, 100)

    text2.anchor_point = (0.5, 0.5)
    text2.anchored_position = (120, 100)

    text3.anchor_point = (0.5, 0.5)
    text3.anchored_position = (190, 100)
    #group.append(bg)
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
            rect = Rect(x, y, rect_width, rect_height, fill=0x4F518C)
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


def add_outline(
        fill_color, outline_colors, rect_width=56, rect_height=44, margin_x=7, margin_y=24
):
    start_x = (display.width - (rect_width * 4 + margin_x * 3)) // 2
    start_y = display.height - rect_height * 3 - margin_y * 2
    for row_index, rects in enumerate(grid_rects):
        if row_index == count - 1:
            for col, rect in enumerate(rects):
                x = start_x + col * (rect_width + margin_x)
                y = start_y + row_index * (rect_height + margin_y)
                group.remove(rect)
                new_rect = Rect(
                    x,
                    y,
                    rect_width,
                    rect_height,
                    fill=fill_color,
                    outline=outline_colors[row_index],
                    stroke=3,
                )
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
        add_outline(fill_color=0x4F518C, outline_colors=row_colors)
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


def chord_to_midi(chord: str):
    if chord.endswith("dim"):
        root = chord[:-3]
        chord_type = "dim"
    elif chord.endswith("aug"):
        root = chord[:-3]
        chord_type = "aug"
    elif chord.endswith("m"):
        root = chord[:-1]
        chord_type = "min"
    elif chord.endswith("7"):
        root = chord[:-1]
        chord_type = "7"
    else:
        root = chord
        chord_type = "maj"

    root_midi = note_to_midi.get(root, None)
    if root_midi is None:
        raise ValueError(f"Unknown root note: {root}")

    intervals = chord_intervals.get(chord_type, None)
    if intervals is None:
        raise ValueError(f"Unknown chord type: {chord_type}")

    return [root_midi + interval for interval in intervals]


def precompute_midi_notes(chords):
    midi_notes_list = []
    for chord in chords:
        midi_notes = chord_to_midi(chord)
        midi_notes_list.append(midi_notes)
    return midi_notes_list


def strum_mode():
    midi_chord_one = [note - 12 for note in chord_to_midi(chord_one)]
    midi_chord_two = [note - 12 for note in chord_to_midi(chord_two)]
    midi_chord_three = [note - 12 for note in chord_to_midi(chord_three)]
    midi_chord_one = (
        midi_chord_one[:3] + [midi_chord_one[0] + 12]
        if len(midi_chord_one) >= 3
        else midi_chord_one
    )
    midi_chord_two = (
        midi_chord_two[:3] + [midi_chord_two[0] + 12]
        if len(midi_chord_two) >= 3
        else midi_chord_two
    )
    midi_chord_three = (
        midi_chord_three[:3] + [midi_chord_three[0] + 12]
        if len(midi_chord_three) >= 3
        else midi_chord_three
    )
    midi_notes_list[0:4] = midi_chord_one
    midi_notes_list[4:8] = midi_chord_two
    midi_notes_list[8:12] = midi_chord_three


ChordModeChanged = False
NormalModeChanged = False
StrumModeChanged = False

chord_one = ""
chord_two = ""
chord_three = ""

display.root_group = group

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
                ChordModeChanged = False
                StrumModeChanged = False
                NormalModeChanged = True
        elif current_page == 2:
            if not key_selected:
                initialize_chord(tri1, tri2, text)
                if not up_button.value:
                    if next_key_index > 0:
                        next_key_index -= 1
                        current_key_index = update_key_selection(
                            next_key_index, current_key_index
                        )
                        time.sleep(0.3)
                if not down_button.value:
                    if next_key_index < 13:
                        next_key_index += 1
                        current_key_index = update_key_selection(
                            next_key_index, current_key_index
                        )
                        time.sleep(0.3)
                if not select.value:
                    key_selected = True
                    selected_key = keys[current_key_index]
                    display_chords_for_key(selected_key)
                    ChordModeChanged = True
                    StrumModeChanged = False
                    NormalModeChanged = False
                    time.sleep(0.3)
        elif current_page == 3:
            if not key_selected:
                initialize_chord(tri1, tri2, text)
                if not up_button.value:
                    if next_key_index > 0:
                        next_key_index -= 1
                        current_key_index = update_guitar_key_selection(
                            next_key_index, current_key_index
                        )
                        time.sleep(0.3)
                if not down_button.value:
                    if next_key_index < 6:
                        next_key_index += 1
                        current_key_index = update_guitar_key_selection(
                            next_key_index, current_key_index
                        )
                        time.sleep(0.3)
                if not select.value:
                    key_selected = True
                    selected_key = keys[current_key_index]
                    time.sleep(0.3)

            else:
                initialize_strum_chord(tri1, tri2, text)
                if count < 3:
                    if not up_button.value:
                        if next_chord_index > 0:
                            next_chord_index -= 1
                            next_chord_index -= 1
                            current_chord_index = update_guitar_chord_selection(
                                next_chord_index, current_chord_index, strum_key
                            )
                            time.sleep(0.3)
                    if not down_button.value:
                        if next_chord_index < 6:
                            next_chord_index += 1
                            current_chord_index = update_guitar_chord_selection(
                                next_chord_index, current_chord_index, strum_key
                            )
                            time.sleep(0.3)
                    if not select.value:
                        count += 1
                        time.sleep(0.3)
                        if count == 1:
                            text1.text = guitar_chord[strum_key][current_chord_index]
                            chord_one = guitar_chord[strum_key][current_chord_index]
                            add_outline(fill_color=0x4F518C, outline_colors=row_colors)
                        elif count == 2:
                            text2.text = guitar_chord[strum_key][current_chord_index]
                            chord_two = guitar_chord[strum_key][current_chord_index]
                            add_outline(fill_color=0x4F518C, outline_colors=row_colors)
                        elif count == 3:
                            text3.text = guitar_chord[strum_key][current_chord_index]
                            chord_three = guitar_chord[strum_key][current_chord_index]
                            add_outline(fill_color=0x4F518C, outline_colors=row_colors)
                            ChordModeChanged = False
                            StrumModeChanged = True
                            NormalModeChanged = False
                        gc.collect()

        if not exit_button.value:
            if ChordModeChanged:
                for i in range(12):
                    button = note_buttons[i]
                    midi_notes = midi_notes_list[i]
                    for midi_note in midi_notes:
                        midi.send(NoteOff(midi_note, 120))  # Velocity 120
                    note_states[i] = False
            else:
                for i in range(12):
                    button = note_buttons[i]
                    if (len(midi_notes_list)) != 0:
                        midi_notes = midi_notes_list[i]
                        midi.send(NoteOff(midi_notes, 120))  # Note off, velocity 120
                    note_states[i] = False
            current_page = 1
            next_page = 1
            clean_up(group)
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
            ChordModeChanged = False
            StrumModeChanged = False
            NormalModeChanged = False
            midi_notes_list = []
            gc.collect()
            gc.mem_free()

    if ChordModeChanged:
        midi_notes_list = precompute_midi_notes(chords[selected_key])
        for i in range(12):
            buttons = note_buttons[i]
            #  if button is pressed...
            midi_notes = midi_notes_list[i]
            if not buttons.value and note_states[i] is False:
                #  send the MIDI note and light up the LED
                for midi_note in midi_notes:
                    midi.send(NoteOn(midi_note, 120))  # Velocity 120
                note_states[i] = True
            #  if the button is released...
            if buttons.value and note_states[i] is True:
                #  stop sending the MIDI note and turn off the LED
                for midi_note in midi_notes:
                    midi.send(NoteOff(midi_note, 120))  # Velocity 120
                note_states[i] = False
    elif NormalModeChanged:
        midi_notes_list = default_midi_notes  # Assign default MIDI notes for Normal Mode
        for i in range(12):
            button = note_buttons[i]
            midi_note = midi_notes_list[i]  # Get single MIDI note for each button
            if not button.value and not note_states[i]:
                midi.send(NoteOn(midi_note, 120))  # Note on, velocity 120
                note_states[i] = True
            elif button.value and note_states[i]:
                midi.send(NoteOff(midi_note, 120))  # Note off, velocity 120
                note_states[i] = False
    elif StrumModeChanged:
        strum_mode()
        for i in range(12):
            button = note_buttons[i]
            midi_note = midi_notes_list[i]
            if not button.value and not note_states[i]:
                midi.send(NoteOn(midi_note, 120))  # Note on, velocity 120
                note_states[i] = True
            elif button.value and note_states[i]:
                midi.send(NoteOff(midi_note, 120))  # Note off, velocity 120
                note_states[i] = False
    gc.collect()
    gc.mem_free()
