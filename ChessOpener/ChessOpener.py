import cv2
import numpy as np
import pyautogui
import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab, Image, ImageTk
import time

class ChessBoardDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Board Detector")
        
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        self.canvas = tk.Canvas(root, width=800, height=500)
        self.canvas.pack()

        self.screenshot_button = tk.Button(root, text="Select Area", command=self.select_area)
        self.screenshot_button.pack()

        self.analyze_button = tk.Button(root, text="Analyze Board", command=self.analyze_board)
        self.analyze_button.pack()

        self.image_label = tk.Label(root)
        self.image_label.pack()

    def select_area(self):
        # Hide the window to take a screenshot of full screen
        self.root.withdraw()
        time.sleep(0.5)  # Small delay to make sure the window is hidden

        # Take screenshot of the full screen
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # Create a new tkinter window to select the area
        selection_window = tk.Toplevel(self.root)
        selection_window.attributes("-fullscreen", True)
        selection_window.attributes("-alpha", 0.3)
        selection_window.configure(bg='black')

        selection_canvas = tk.Canvas(selection_window, cursor="cross", bg='black')
        selection_canvas.pack(fill="both", expand=True)

        self.rect = None

        def on_mouse_down(event):
            self.start_x, self.start_y = event.x, event.y
            self.rect = selection_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

        def on_mouse_move(event):
            if self.rect is not None:
                selection_canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        def on_mouse_up(event):
            self.end_x, self.end_y = event.x, event.y
            selection_window.destroy()
            # Show the main window again
            self.root.deiconify()

        selection_canvas.bind("<ButtonPress-1>", on_mouse_down)
        selection_canvas.bind("<B1-Motion>", on_mouse_move)
        selection_canvas.bind("<ButtonRelease-1>", on_mouse_up)

    def analyze_board(self):
        if self.start_x is None or self.start_y is None or self.end_x is None or self.end_y is None:
            print("Please select an area first.")
            return

        # Take a screenshot of the selected area
        screenshot = ImageGrab.grab(bbox=(self.start_x, self.start_y, self.end_x, self.end_y))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        # Assume the selected area is a perfect square chessboard
        board_size = 8
        height, width, _ = screenshot.shape
        cell_width = width // board_size
        cell_height = height // board_size
        
        # Draw the chessboard grid
        screenshot_with_grid = screenshot.copy()
        for i in range(board_size):
            for j in range(board_size):
                top_left = (j * cell_width, i * cell_height)
                bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
                cv2.rectangle(screenshot_with_grid, top_left, bottom_right, (255, 0, 0), 1)
        
        # Display the result in the GUI
        self.display_image(screenshot_with_grid)

    def display_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.image_label.imgtk = imgtk
        self.image_label.configure(image=imgtk)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessBoardDetector(root)
    root.mainloop()
