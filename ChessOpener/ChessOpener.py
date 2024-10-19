import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, Image, ImageTk
import cv2
import numpy as np
import threading
import time
import os
import chess
import chess.svg
import json

class ChessboardCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chessboard Capture")
        
        # Instructions
        self.label = ttk.Label(root, text="Click 'Select Area' to define the capture area, then click 'Capture'.")
        self.label.pack(pady=10)
        
        # Button to select area
        self.select_area_btn = ttk.Button(root, text="Select Area", command=self.select_area)
        self.select_area_btn.pack(pady=10)
        
        # Button to start capture
        self.capture_btn = ttk.Button(root, text="Capture Chessboard", command=self.capture_screen)
        self.capture_btn.pack(pady=10)
        
        # Button to analyze chessboard
        self.analyze_btn = ttk.Button(root, text="Analyze Chessboard State", command=self.analyze_chessboard)
        self.analyze_btn.pack(pady=10)
        
        # Canvas for preview
        self.preview_canvas = tk.Canvas(root, width=400, height=400)
        self.preview_canvas.pack(pady=10)
        
        # Status indicator
        self.status_indicator = tk.Canvas(root, width=50, height=50)
        self.status_indicator.pack(pady=10)
        self.status_box = self.status_indicator.create_rectangle(5, 5, 45, 45, fill='red')
        
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.rect_id = None
        self.captured_image = None
        
        # Load previously saved capture area
        self.load_capture_area()
        
        # List of piece labels (e.g., 0 = empty, 1 = white pawn, etc.)
        self.piece_labels = {
            'empty': '.',
            'white_pawn': 'P', 'black_pawn': 'p',
            'white_rook': 'R', 'black_rook': 'r',
            'white_knight': 'N', 'black_knight': 'n',
            'white_bishop': 'B', 'black_bishop': 'b',
            'white_queen': 'Q', 'black_queen': 'q',
            'white_king': 'K', 'black_king': 'k'
        }
        
        # Load templates for matching
        self.templates = self.load_templates(r'C:\GitHubRepos\MyPythonScripts\ChessOpener\templates')
        
        # Start the background checker loop
        self.running = True
        self.check_thread = threading.Thread(target=self.check_for_chessboard)
        self.check_thread.daemon = True
        self.check_thread.start()

    def load_templates(self, template_dir):
        templates = {}
        for filename in os.listdir(template_dir):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                piece_name = filename.split('.')[0]
                template_path = os.path.join(template_dir, filename)
                template_image = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template_image is not None:
                    templates[piece_name] = cv2.normalize(template_image, None, 0, 255, cv2.NORM_MINMAX)
        return templates

    def select_area(self):
        # Create a transparent overlay window to select the capture area
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.configure(bg='gray')
        self.overlay.bind("<ButtonPress-1>", self.on_button_press)
        self.overlay.bind("<B1-Motion>", self.on_mouse_drag)
        self.overlay.bind("<ButtonRelease-1>", self.on_button_release)
        
        # Change mouse cursor to crosshair
        self.overlay.config(cursor="cross")

        # Create a canvas on the overlay to draw the selection rectangle
        self.overlay_canvas = tk.Canvas(self.overlay, bg='gray', highlightthickness=0)
        self.overlay_canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = self.start_y = self.end_x = self.end_y = 0

    def on_button_press(self, event):
        # Record the starting position of the selection
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = None

    def on_mouse_drag(self, event):
        # Update the rectangle as the mouse is dragged
        self.end_x = event.x
        self.end_y = event.y

        if self.rect_id:
            self.overlay_canvas.delete(self.rect_id)
        self.rect_id = self.overlay_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline='red', width=2)

    def on_button_release(self, event):
        # Record the ending position and close the overlay
        self.end_x = event.x
        self.end_y = event.y
        self.overlay.destroy()
        
        # Save the capture area
        self.save_capture_area()

    def capture_screen(self):
        if self.start_x and self.start_y and self.end_x and self.end_y:
            # Ensure coordinates are ordered correctly
            x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
            x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
            self.captured_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            if self.captured_image is not None:
                self.preview_image(self.captured_image)
            else:
                print("Failed to capture the screen. Please try again.")
        else:
            print("Please select an area first.")
        
    def preview_image(self, image):
        image.thumbnail((400, 400))
        self.image_tk = ImageTk.PhotoImage(image)
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        
    def analyze_chessboard(self):
        if self.captured_image is None:
            print("Please capture an image first.")
            return False
        
        try:
            # Convert captured image to an OpenCV format
            image = cv2.cvtColor(np.array(self.captured_image), cv2.COLOR_RGB2BGR)
        except cv2.error as e:
            print("Error converting image to OpenCV format:", e)
            return False
        
        if image is None or image.size == 0:
            print("Captured image is empty. Please try again.")
            return False
        
        # Resize the image to a standard size for easier processing
        image = cv2.resize(image, (800, 800))

        # Split the board into 64 squares
        squares = self.split_board(image)
        board_state = []

        # Classify each square using template matching
        for square in squares:
            piece_label = self.classify_square(square)
            board_state.append(piece_label)

        # Output the board state in a chessboard format
        self.print_board_state_chess(board_state)
        
    def split_board(self, image):
        squares = []
        square_size = image.shape[0] // 8
        for row in range(8):
            for col in range(8):
                x_start = col * square_size
                y_start = row * square_size
                square = image[y_start:y_start + square_size, x_start:x_start + square_size]
                squares.append(square)
        return squares

    def classify_square(self, square):
        gray_square = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)
        best_match = ('empty', 0.5)  # Default to empty with a threshold score
        
        # Preprocessing: Apply GaussianBlur to reduce noise
        gray_square = cv2.GaussianBlur(gray_square, (5, 5), 0)
        
        # For white pieces, apply adaptive thresholding and contrast enhancement to better distinguish them on light squares
        enhanced_square = cv2.convertScaleAbs(gray_square, alpha=1.5, beta=20)  # Increase contrast
        _, white_square = cv2.threshold(enhanced_square, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Perform template matching for each piece at multiple scales
        for piece_name, template in self.templates.items():
            for scale in [1.0, 0.95, 1.05]:  # Try different scales for flexibility
                resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
                if resized_template.shape[0] > gray_square.shape[0] or resized_template.shape[1] > gray_square.shape[1]:
                    continue
                if 'white' in piece_name:
                    res = cv2.matchTemplate(white_square, resized_template, cv2.TM_CCOEFF_NORMED)
                else:
                    res = cv2.matchTemplate(gray_square, resized_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                if max_val > best_match[1] and max_val > 0.55:  # Adjusted threshold for better sensitivity
                    best_match = (piece_name, max_val)
        
        return best_match[0]
    
    def print_board_state_chess(self, board_state):
        board_representation = ""
        for row in range(8):
            for col in range(8):
                piece_label = board_state[row * 8 + col]
                board_representation += self.piece_labels[piece_label] + " "
            board_representation += "\n"
        print(board_representation)
    
    def save_capture_area(self):
        capture_area = {
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y
        }
        with open(r"C:\GitHubRepos\MyPythonScripts\ChessOpener\capture_area.json", "w") as f:
            json.dump(capture_area, f)

    def load_capture_area(self):
        if os.path.exists(r"C:\GitHubRepos\MyPythonScripts\ChessOpener\capture_area.json"):
            with open(r"C:\GitHubRepos\MyPythonScripts\ChessOpener\capture_area.json", "r") as f:
                capture_area = json.load(f)
                self.start_x = capture_area.get("start_x", 0)
                self.start_y = capture_area.get("start_y", 0)
                self.end_x = capture_area.get("end_x", 0)
                self.end_y = capture_area.get("end_y", 0)
        
    def check_for_chessboard(self):
        while self.running:
            if self.start_x and self.start_y and self.end_x and self.end_y:
                # Ensure coordinates are ordered correctly
                x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
                x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
                self.captured_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                if self.captured_image is not None:
                    self.analyze_chessboard()
                    self.status_indicator.itemconfig(self.status_box, fill='green')
                else:
                    self.status_indicator.itemconfig(self.status_box, fill='red')
            else:
                self.status_indicator.itemconfig(self.status_box, fill='red')
            time.sleep(3)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessboardCaptureApp(root)
    root.mainloop()
