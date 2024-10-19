import ctypes
import tkinter as tk
from tkinter import messagebox
import pyautogui
import time

class BoxDrawer:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.geometry("300x200+100+100")
        self.root.configure(bg='red')
        self.root.attributes('-alpha', 0.3)  # Set transparency level

        self.drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_data["x"]
        y = self.root.winfo_y() + event.y - self.drag_data["y"]
        self.root.geometry(f"300x200+{x}+{y}")

def create_overlay_box():
    root = tk.Tk()
    app = BoxDrawer(root)
    root.mainloop()

if __name__ == "__main__":
    create_overlay_box()
