import tkinter as tk
from tkinter import messagebox
import pyautogui
import keyboard  # Import the keyboard library
import time  # Import the time library
import threading  # Import the threading library
import random  # Import the random library
import json  # Import the json library for saving and loading screen location
from bomb_location_search import search_letters_in_location  # Import the new method

# Global variable to store screen location coordinates
screen_location = None

# Global list to store the last 10 words
last_words = []

# Global set to track used letters
used_letters = set()

# Global variable to store the overlay window
overlay = None

# File to save the screen location
screen_location_file = 'C:\\GitHubRepos\\MyPythonScripts\\BombParty\\screen_location.json'

def save_screen_location(location):
    with open(screen_location_file, 'w') as file:
        json.dump(location, file)

def load_screen_location():
    global screen_location
    try:
        with open(screen_location_file, 'r') as file:
            screen_location = tuple(json.load(file))
            draw_box_around_location(screen_location)
    except (FileNotFoundError, json.JSONDecodeError):
        screen_location = None

def draw_box_around_location(location):
    global overlay
    x1, y1, x2, y2 = location
    width = x2 - x1
    height = y2 - y1

    # Destroy the old overlay if it exists
    if overlay is not None:
        overlay.destroy()

    # Create an overlay window
    overlay = tk.Toplevel()
    overlay.attributes('-fullscreen', True)
    overlay.attributes('-alpha', 0.3)
    overlay.attributes('-topmost', True)
    overlay.attributes('-transparentcolor', 'black')
    overlay.config(bg='black')

    # Make the overlay click-through
    overlay.attributes('-disabled', True)

    # Create a canvas to draw the rectangle
    canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Draw a white rectangle
    canvas.create_rectangle(x1, y1, x2, y2, outline='white', width=2)

def find_word_with_letters_in_order(letters, dictionary_path='C:\\GitHubRepos\\MyPythonScripts\\BombParty\\organized_wordlist.txt', find_shortest=False, prioritize_new_letters=True):
    with open(dictionary_path, 'r') as file:
        words = file.read().splitlines()
    
    random.shuffle(words)  # Shuffle the list of words

    def contains_letters_in_order(word, letters):
        return letters in word

    def count_new_letters(word):
        return len(set(word) - used_letters)

    selected_word = ''
    prioritized_word = ''
    max_new_letters = 0
    for word in words:
        if contains_letters_in_order(word, letters) and word not in last_words and len(word) >= 4:
            new_letters_count = count_new_letters(word)
            if prioritize_new_letters and new_letters_count > max_new_letters:
                max_new_letters = new_letters_count
                prioritized_word = word
            elif new_letters_count == max_new_letters:
                if find_shortest:
                    if not prioritized_word or len(word) < len(prioritized_word):
                        prioritized_word = word
                else:
                    if len(word) > len(prioritized_word):
                        prioritized_word = word
            else:
                if find_shortest:
                    if not selected_word or len(word) < len(selected_word):
                        selected_word = word
                else:
                    if len(word) > len(selected_word):
                        selected_word = word

    # Return the prioritized word if found, otherwise return the default selected word
    return prioritized_word if prioritized_word else selected_word

def type_word(word):
    for char in word:
        pyautogui.write(char)
        # Add a random delay between each character
        time.sleep(random.uniform(0.01, 0.05))  # Adjust the range for more human-like typing speed
        # Occasionally add a longer pause to simulate thinking or hesitation
        if random.random() < 0.1:  # 10% chance to add a longer pause
            time.sleep(random.uniform(0.1, .2))
    pyautogui.press('enter')  # Press Enter key after typing the word
    pyautogui.press('enter')  # Press Enter key after typing the word

def update_used_letters(word):
    global used_letters
    used_letters.update(set(word) - {'-'})  # Exclude hyphens
    used_letters_text.delete(1.0, tk.END)
    used_letters_text.insert(tk.END, f"Used letters: {', '.join(sorted(used_letters))}")
    if len(used_letters) >= 26:  # All letters in the alphabet have been used
        used_letters.clear()
        used_letters_text.delete(1.0, tk.END)
        used_letters_text.insert(tk.END, "Used letters: ")

def search_and_type(event=None):
    letters = entry.get().strip().upper()
    if not letters:
        if screen_location:
            letters = search_letters_in_location(screen_location)
            if not letters:
                result_label.config(text="No letters found in the defined screen location.")
                return
            extracted_label.config(text=f"Extracted letters: {letters}")
        else:
            result_label.config(text="Please enter the letters in specific order or define screen location.")
            return

    find_shortest = shortest_var.get()
    prioritize_new_letters = prioritize_new_letters_var.get()
    selected_word = find_word_with_letters_in_order(letters, find_shortest=find_shortest, prioritize_new_letters=prioritize_new_letters)
    if selected_word:
        result_label.config(text=f"Selected word: {selected_word}")
        if type_var.get():
            threading.Thread(target=type_word, args=(selected_word,)).start()
        
        # Add the word to the last_words list and maintain its size
        last_words.append(selected_word)
        if len(last_words) > 1000:
            last_words.pop(0)
        
        # Update the used letters
        update_used_letters(selected_word)
    else:
        result_label.config(text="No word found.")

def global_hotkey():
    search_and_type()

def toggle_shortest_var():
    shortest_var.set(not shortest_var.get())

def define_location():
    global screen_location
    screen_location = 0, 0, 0, 0  # Initialize screen_location to a default value
    start_x, start_y = 0, 0  # Initialize start_x and start_y

    def on_mouse_down(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x_root, event.y_root
        canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', tag='rect')

    def on_mouse_move(event):
        canvas.coords('rect', start_x, start_y, event.x_root, event.y_root)

    def on_mouse_up(event):
        global screen_location
        end_x, end_y = event.x_root, event.y_root
        screen_location = (start_x, start_y, end_x, end_y)
        save_screen_location(screen_location)
        draw_box_around_location(screen_location)
        capture_window.destroy()
        messagebox.showinfo("Screen Location", f"Screen location defined: {screen_location}")

    capture_window = tk.Toplevel(root)
    capture_window.attributes('-fullscreen', True)
    capture_window.attributes('-alpha', 0.3)
    canvas = tk.Canvas(capture_window, cursor='cross')
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.bind('<ButtonPress-1>', on_mouse_down)
    canvas.bind('<B1-Motion>', on_mouse_move)
    canvas.bind('<ButtonRelease-1>', on_mouse_up)
    capture_window.mainloop()

def toggle_always_on_top():
    root.attributes('-topmost', always_on_top_var.get())

def clear_last_words():
    global last_words, used_letters
    last_words = []
    used_letters.clear()
    used_letters_text.delete(1.0, tk.END)
    used_letters_text.insert(tk.END, "Used letters: ")
    messagebox.showinfo("Clear Last Words", "The last words list and used letters have been cleared.")

def remove_last_word():
    if last_words:
        removed_word = last_words[-1]  # Get the last word without removing it from the list
        remove_last_word_label.config(text=f"Removed last word: {removed_word}")
        
        # Update the text file to remove the last word
        with open('C:\\GitHubRepos\\MyPythonScripts\\BombParty\\organized_wordlist.txt', 'r') as file:
            words = file.read().splitlines()
        
        if removed_word in words:
            words.remove(removed_word)
        
        with open('C:\\GitHubRepos\\MyPythonScripts\\BombParty\\organized_wordlist.txt', 'w') as file:
            file.write('\n'.join(words))
    else:
        remove_last_word_label.config(text="No words to remove.")

# GUI setup
root = tk.Tk()
root.title("Word Finder")

tk.Label(root, text="Enter the letters in specific order:").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5)
entry.bind('<Return>', search_and_type)  # Bind Enter key to search_and_type function

type_var = tk.BooleanVar()
tk.Checkbutton(root, text="Type the word automatically", variable=type_var).pack(pady=5)

shortest_var = tk.BooleanVar()
tk.Checkbutton(root, text="Find the shortest word", variable=shortest_var).pack(pady=5)

prioritize_new_letters_var = tk.BooleanVar()
tk.Checkbutton(root, text="Prioritize new letters", variable=prioritize_new_letters_var).pack(pady=5)

always_on_top_var = tk.BooleanVar()
tk.Checkbutton(root, text="Always on Top", variable=always_on_top_var, command=toggle_always_on_top).pack(pady=5)

tk.Button(root, text="Search", command=search_and_type).pack(pady=5)
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

extracted_label = tk.Label(root, text="")  # Label to show extracted letters
extracted_label.pack(pady=5)

used_letters_text = tk.Text(root, height=4, wrap=tk.WORD)  # Text widget to show used letters with word wrap
used_letters_text.pack(pady=5, fill=tk.BOTH, expand=True)

remove_last_word_label = tk.Label(root, text="")  # Label to show the status of the last word removal
remove_last_word_label.pack(pady=5)

tk.Button(root, text="Define Screen Location", command=define_location).pack(pady=5)

tk.Button(root, text="Clear Last Words", command=clear_last_words).pack(pady=5)  # Add button to clear last words

# Set up global hotkey
keyboard.add_hotkey('home', global_hotkey)
keyboard.add_hotkey('end', toggle_shortest_var)
keyboard.add_hotkey('down', remove_last_word)

# Load the screen location when the application starts
load_screen_location()

root.mainloop()