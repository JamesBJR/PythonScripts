import cv2
import numpy as np
import pyautogui
import tkinter as tk
from PIL import ImageGrab, Image, ImageTk
import time
import os
import json
import joblib
from skimage.feature import hog

class ChessBoardDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Board Detector")
        
        # Load previous selection coordinates if available
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.load_coordinates()
        
        # Create buttons: 'Select Area', 'Analyze Board'
        self.screenshot_button = tk.Button(root, text="Select Area", command=self.select_area)
        self.screenshot_button.pack(side="top", pady=5)

        self.analyze_button = tk.Button(root, text="Analyze Board", command=self.analyze_board)
        self.analyze_button.pack(side="top", pady=5)

        # Create a label to display the chessboard image
        self.image_label = tk.Label(root)
        self.image_label.pack(fill="both", expand=True)

        # Load pre-trained SVM model for piece recognition
        self.svm_model = self.load_svm_model()

    def load_coordinates(self):
        try:
            with open("chessboard_coordinates.json", "r") as file:
                data = json.load(file)
                self.start_x = data.get("start_x")
                self.start_y = data.get("start_y")
                self.end_x = data.get("end_x")
                self.end_y = data.get("end_y")
        except FileNotFoundError:
            pass

    def save_coordinates(self):
        data = {
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y
        }
        with open("chessboard_coordinates.json", "w") as file:
            json.dump(data, file)

    def load_svm_model(self):
        # Load the pre-trained SVM model for chess piece detection
        model_path = r"C:\GitHubRepos\MyPythonScripts\ChessOpener\chess_piece_svm_model.pkl"
        if os.path.exists(model_path):
            return joblib.load(model_path)
        else:
            print("Model file not found. Please train the SVM model first.")
            return None

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
            # Save the selected coordinates
            self.save_coordinates()
            # Automatically analyze the board after selecting
            self.analyze_board()

        selection_canvas.bind("<ButtonPress-1>", on_mouse_down)
        selection_canvas.bind("<B1-Motion>", on_mouse_move)
        selection_canvas.bind("<ButtonRelease-1>", on_mouse_up)

    def analyze_board(self):
        if self.start_x is None or self.start_y is None or self.end_x is None or self.end_y is None:
            print("Please select an area first.")
            return

        if not self.svm_model:
            print("SVM model not loaded. Cannot analyze the board.")
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
        
        # Draw the chessboard grid and identify pieces
        screenshot_with_grid = screenshot.copy()
        for i in range(board_size):
            for j in range(board_size):
                top_left = (j * cell_width, i * cell_height)
                bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
                cell = screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                
                # Identify the piece in the cell using HOG and SVM
                piece_name = self.identify_piece_with_svm(cell)
                if piece_name:
                    cv2.putText(screenshot_with_grid, piece_name, (top_left[0] + 5, top_left[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                
                # Draw the grid
                cv2.rectangle(screenshot_with_grid, top_left, bottom_right, (255, 0, 0), 1)
        
        # Display the result in the GUI
        self.display_image(screenshot_with_grid)

    def identify_piece_with_svm(self, cell):
        # Resize cell to a fixed size
        cell_resized = cv2.resize(cell, (64, 64))
        
        # Convert to grayscale
        cell_gray = cv2.cvtColor(cell_resized, cv2.COLOR_BGR2GRAY)
        
        # Extract HOG features
        features, _ = hog(cell_gray, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True, block_norm='L2-Hys')
        
        # Predict the piece using the SVM model
        prediction = self.svm_model.predict([features])
        return prediction[0] if prediction else None

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
