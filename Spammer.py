import keyboard
import random
import time
import threading

def spam(key):
    while keyboard.is_pressed(key):
        keyboard.write(key)
        rand = random.randint(200, 500) / 1000  # Convert to seconds
        time.sleep(rand)

def start_spam(key):
    if not keyboard.is_pressed(key):
        thread = threading.Thread(target=spam, args=(key,))
        thread.start()

keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

for key in keys:
    keyboard.add_hotkey(key, start_spam, args=(key,))

keyboard.wait('esc')  # Press 'esc' to stop the script3333333333333