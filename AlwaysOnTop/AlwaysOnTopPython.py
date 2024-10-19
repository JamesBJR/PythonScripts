import tkinter as tk
import threading
from pynput import keyboard
import ctypes
import time

class AlwaysOnTopApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry('150x170')
        self.root.title("Always On Top Setter")
        self.root.resizable(False, False)
        self.window_title = tk.StringVar()
        self.window_title.set("No active window")

        # GUI Elements
        title_frame = tk.Frame(root, bg='#f0f0f0')
        title_frame.pack(fill='both', pady=(10, 5), padx=10)
        tk.Label(title_frame, text="Active Window:", font=('Helvetica', 10, 'bold')).pack(anchor='w')
        self.title_label = tk.Entry(title_frame, textvariable=self.window_title, width=20, font=('Helvetica', 9))
        self.title_label.pack(pady=5)

        self.toggle_button = tk.Button(root, text="Reset Windows", command=self.reset_modified_windows, font=('Helvetica', 10), bg='#007acc', fg='white')
        self.toggle_button.pack(pady=(5, 10))

        self.status_label = tk.Label(root, text="Press Shift + Space to toggle", font=('Helvetica', 8), wraplength=130)
        self.status_label.pack(pady=5)

        # Bind the left mouse button click on the root window to start dragging
        root.bind('<Button-1>', self.start_move)
        root.bind('<B1-Motion>', self.do_move)

        # Start the hotkey listener
        hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        hotkey_thread.start()

        # Store modified windows
        self.modified_windows = set()

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() - self._x + event.x
        y = self.root.winfo_y() - self._y + event.y
        self.root.geometry(f"+{x}+{y}")

    def hotkey_listener(self):
        with keyboard.GlobalHotKeys({'<shift>+<space>': self.toggle_always_on_top}) as h:
            h.join()

    def toggle_always_on_top(self):
        try:
            # Allow some time to properly get the active window
            time.sleep(0.1)
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if hwnd:
                # Toggle always on top using HWND_TOPMOST (-1) or HWND_NOTOPMOST (-2)
                is_always_on_top = bool(ctypes.windll.user32.GetWindowLongW(hwnd, -20) & 0x00000008)
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    ctypes.c_void_p(-1) if not is_always_on_top else ctypes.c_void_p(-2),
                    0, 0, 0, 0,
                    0x0001 | 0x0002 | 0x0040
                )
                window_title = ctypes.create_unicode_buffer(512)
                ctypes.windll.user32.GetWindowTextW(hwnd, window_title, 512)
                self.window_title.set(window_title.value)
                self.status_label.config(
                    text=f"'{window_title.value}' is now {'always on top' if not is_always_on_top else 'no longer always on top'}.",
                    fg='#007acc' if not is_always_on_top else '#d9534f'
                )
                # Store hwnd if modified
                if not is_always_on_top:
                    self.modified_windows.add(hwnd)
                elif hwnd in self.modified_windows:
                    self.modified_windows.remove(hwnd)
            else:
                self.status_label.config(text="No active window found.", fg='#d9534f')
        except (AttributeError, ctypes.WinError) as e:
            self.status_label.config(text=f"Error: {str(e)}", fg='#d9534f')

    def reset_modified_windows(self):
        try:
            for hwnd in list(self.modified_windows):
                ctypes.windll.user32.SetWindowPos(
                    hwnd,
                    ctypes.c_void_p(-2),
                    0, 0, 0, 0,
                    0x0001 | 0x0002 | 0x0040
                )
                self.modified_windows.remove(hwnd)
            self.status_label.config(text="Modified windows are now reset to normal state.", fg='#007acc')
        except (AttributeError, ctypes.WinError) as e:
            self.status_label.config(text=f"Error: {str(e)}", fg='#d9534f')

if __name__ == "__main__":
    root = tk.Tk()
    app = AlwaysOnTopApp(root)
    root.mainloop()
