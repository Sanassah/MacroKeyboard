import board
import digitalio
import time
import usb_hid
import rotaryio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.consumer_control import ConsumerControl

# Encoders 1

button1 = digitalio.DigitalInOut(board.GP26)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP
encoder1 = rotaryio.IncrementalEncoder(board.GP27, board.GP28)
cc1 = ConsumerControl(usb_hid.devices)
button1_state = None
last_position1 = encoder1.position

# Encoders 2

button2 = digitalio.DigitalInOut(board.GP2)
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP
encoder2 = rotaryio.IncrementalEncoder(board.GP0, board.GP1)
cc2 = ConsumerControl(usb_hid.devices)
button2_state = None
last_position2 = encoder2.position

# Define the GPIO pins for each key
key_pins = [
    board.GP21,
    board.GP20,
    board.GP13,
    board.GP18,
    board.GP19,
    board.GP14,
    board.GP16,
    board.GP17,
    board.GP15,
]

# Define the corresponding key names or functions for each pin
key_mapping = {
    board.GP21: Keycode.ONE,
    board.GP20: Keycode.TWO,
    board.GP13: Keycode.THREE,
    board.GP18: Keycode.FOUR,
    board.GP19: Keycode.FIVE,
    board.GP14: Keycode.SIX,
    board.GP16: Keycode.SEVEN,
    board.GP17: Keycode.EIGHT,
    board.GP15: Keycode.NINE,
}

# Initialize the GPIO pins as inputs with pull-up resistors
keys = []
key_hold_time = {}
repeat_delay = 0.5  # Delay before repeated key presses
repeat_interval = 0.01  # Delay between repeated key presses

for pin in key_pins:
    key = digitalio.DigitalInOut(pin)
    key.direction = digitalio.Direction.INPUT
    key.pull = digitalio.Pull.UP
    keys.append(key)
    key_hold_time[pin] = None

# Create a keyboard object
keyboard = Keyboard(usb_hid.devices)

# Main loop
while True:
    # Encoder 1
    current_position1 = encoder1.position
    position_change1 = current_position1 - last_position1

    if position_change1 > 0:
        for _ in range(position_change1):
            cc1.send(ConsumerControlCode.VOLUME_INCREMENT)
        print(current_position1)

    elif position_change1 < 0:
        for _ in range(-position_change1):
            cc1.send(ConsumerControlCode.VOLUME_DECREMENT)
        print(current_position1)

    last_position1 = current_position1

    if not button1.value and button1_state is None:
        button1_state = "pressed"

    if button1.value and button1_state == "pressed":
        print("Button 1 pressed.")
        cc1.send(ConsumerControlCode.MUTE)
        button1_state = None

    # Encoder 2
    current_position2 = encoder2.position
    position_change2 = current_position2 - last_position2

    if position_change2 > 0:
        for _ in range(position_change2):
            keyboard.press(Keycode.LEFT_ARROW)
            keyboard.release_all()
        print(current_position2)

    elif position_change2 < 0:
        for _ in range(-position_change2):
            keyboard.press(Keycode.RIGHT_ARROW)
            keyboard.release_all()
        print(current_position2)

    last_position2 = current_position2

    if not button2.value and button2_state is None:
        button2_state = "pressed"

    if button2.value and button2_state == "pressed":
        print("Button 2 pressed.")
        cc2.send(ConsumerControlCode.PLAY_PAUSE)
        button2_state = None

    # Read the state of each key
    for key_pin, key in zip(key_pins, keys):
        if not key.value:
            # Key is pressed
            if key_pin in key_mapping:
                if key_hold_time[key_pin] is None:
                    # Initial key press
                    key_code = key_mapping[key_pin]
                    keyboard.press(key_code)
                    keyboard.release_all()
                    key_hold_time[key_pin] = time.monotonic()
                else:
                    # Key is being held
                    current_time = time.monotonic()
                    if current_time - key_hold_time[key_pin] >= repeat_delay:
                        key_code = key_mapping[key_pin]
                        keyboard.press(key_code)
                        keyboard.release_all()
                        key_hold_time[key_pin] += repeat_interval

        else:
            # Key is released
            key_hold_time[key_pin] = None
