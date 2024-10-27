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
from stockfish import Stockfish
import threading
import keyboard
import mouse



class ChessBoardDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Board")
        
        # Load previous selection coordinates if available
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.load_coordinates()
        
        # Create buttons: 'Select Area', 'Analyze Board'
        self.screenshot_button = tk.Button(root, text="Select Area", command=self.select_area)
        self.screenshot_button.pack(side="left", pady=5)

        self.analyze_button = tk.Button(root, text="Analyze Board", command=self.analyze_board)
        self.analyze_button.pack(side="right", pady=5)

        # Create a checkbox to select the player's color
        self.player_color_var = tk.StringVar(value="White")
        self.player_color_checkbox = tk.Checkbutton(root, text="Player is Black", variable=self.player_color_var, onvalue="Black", offvalue="White", command=self.update_board_coordinates)
        self.player_color_checkbox.pack(side="top", pady=5)

        # Threshold slider for color detection
        self.threshold_value = tk.IntVar(value=148)  # Initial value for threshold
        self.threshold_slider = tk.Scale(root, from_=50, to=400, orient="horizontal", label="Color Threshold", variable=self.threshold_value)
        self.threshold_slider.pack(side="bottom", pady=5)

        # Create a checkbox for recapturing and reanalyzing after best move
        self.reanalyze_var = tk.BooleanVar(value=False)
        self.reanalyze_checkbox = tk.Checkbutton(root, text="Recapture", variable=self.reanalyze_var)
        self.reanalyze_checkbox.pack(side="right", pady=5)

        # Button to destroy overlay boxes
        self.clear_overlays_button = tk.Button(root, text="Clear Overlays", command=self.clear_overlay_boxes)
        self.clear_overlays_button.pack(side="left", pady=5)

        # Stockfish Think Time Slider
        self.think_time_slider = tk.Scale(root, from_=100, to=10000, orient="horizontal", label="Think Time (ms)")
        self.think_time_slider.set(500)
        self.think_time_slider.pack(side="bottom", pady=5)


        # Create a label to display the chessboard image
        self.image_label = tk.Label(root)
        self.image_label.pack(fill="both", expand=True)

        # Load pre-trained SVM model for piece recognition
        self.svm_model = self.load_svm_model()

        # Initialize Stockfish engine
        stockfish_path = r"C:\GitHubRepos\MyPythonScripts\ChessOpener\stockfish\stockfish-windows-x86-64-avx2.exe"
        self.stockfish_path = stockfish_path
        self.initialize_stockfish()

        # Store the latest screenshot with grid for drawing moves
        self.screenshot_with_grid = None

        # Flag to track if hotkeys are temporarily denied  
        self.hotkey_denied = False  

        # Bind key event to reanalyze board
        keyboard.add_hotkey('a', lambda: self.analyze_board_if_ready())
        keyboard.add_hotkey('s', lambda: self.toggle_player_color())

            # Add hotkey for mouse wheel scroll up to analyze the board
        mouse.hook(self.on_mouse_event)

    def on_mouse_event(self, event):
        # Check if the event is a wheel event and if it is a scroll up
        if isinstance(event, mouse.WheelEvent) and event.delta > 0:
            self.analyze_board_if_ready()
            
    def deny_hotkeys_for(self, duration):
        # Method to deny hotkeys for a set amount of time
        def deny():
            self.hotkey_denied = True
            time.sleep(duration)
            self.hotkey_denied = False
        threading.Thread(target=deny).start()

    def analyze_board_if_ready(self):
        # Only proceed if hotkeys are not denied
        if not self.hotkey_denied:
            threading.Thread(target=self.analyze_board).start()

    def clear_overlay_boxes(self):
        # Method to clear overlay boxes from the screen
        for box in self.current_overlays:
            box.destroy()
        self.current_overlays.clear()

    def toggle_player_color(self):
        # Function to toggle the player's color checkbox
        if self.player_color_var.get() == "White":
            self.player_color_var.set("Black")
        else:
            self.player_color_var.set("White")
        self.update_board_coordinates()  # Update the board after toggling


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

    def initialize_stockfish(self):
        try:
            self.stockfish = Stockfish(self.stockfish_path)
            self.stockfish.set_skill_level(10)  # Adjust skill level as needed
        except Exception as e:
            print(f"Failed to initialize Stockfish: {e}")
            self.stockfish = None

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

        # Create a small zoom window
        zoom_window = tk.Toplevel(selection_window)
        zoom_window.title("Zoom View")
        zoom_window.geometry("200x200")  # Fixed size for zoom window
        zoom_label = tk.Label(zoom_window)
        zoom_label.pack()

        self.rect = None

        def on_mouse_down(event):
            self.start_x, self.start_y = event.x, event.y
            self.rect = selection_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

        def on_mouse_move(event):
            if self.rect is not None:
                selection_canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

            # Update zoom window
            x, y = event.x, event.y
            zoom_size = 40  # Size of the area to zoom in on
            zoom_factor = 5  # Zoom factor

            # Calculate bounding box for zoom area
            left = max(0, x - zoom_size // 2)
            top = max(0, y - zoom_size // 2)
            right = min(screenshot.shape[1], x + zoom_size // 2)
            bottom = min(screenshot.shape[0], y + zoom_size // 2)

            # Crop and resize the zoom area
            zoom_area = screenshot[top:bottom, left:right]
            zoom_area = cv2.resize(zoom_area, (zoom_size * zoom_factor, zoom_size * zoom_factor), interpolation=cv2.INTER_LINEAR)
            zoom_area = cv2.cvtColor(zoom_area, cv2.COLOR_BGR2RGB)

            # Draw a box around the center pixel
            zoom_area = np.array(zoom_area)
            center_x = zoom_area.shape[1] // 2
            center_y = zoom_area.shape[0] // 2
            cv2.rectangle(zoom_area, (center_x - 2, center_y - 2), (center_x + 2, center_y + 2), (255, 0, 0), 1)

            zoom_image = Image.fromarray(zoom_area)
            zoom_photo = ImageTk.PhotoImage(zoom_image)
            zoom_label.config(image=zoom_photo)
            zoom_label.image = zoom_photo

        def on_mouse_up(event):
            self.end_x, self.end_y = event.x, event.y
            selection_window.destroy()
            zoom_window.destroy()
            # Show the main window again
            self.root.deiconify()
            # Save the selected coordinates
            self.save_coordinates()
            # Automatically analyze the board after selecting
            self.analyze_board()

        selection_canvas.bind("<ButtonPress-1>", on_mouse_down)
        selection_canvas.bind("<B1-Motion>", on_mouse_move)
        selection_canvas.bind("<ButtonRelease-1>", on_mouse_up)
        selection_window.bind("<Motion>", on_mouse_move)



    def analyze_board(self):


        if self.start_x is None or self.start_y is None or self.end_x is None or self.end_y is None:
            print("Please select an area first.")
            return

        if not self.svm_model:
            print("SVM model not loaded. Cannot analyze the board.")
            return

        think_time_ms = self.think_time_slider.get()  # Get the think time from the slider
        think_time_seconds = think_time_ms / 1000.0  # Convert milliseconds to seconds
        self.deny_hotkeys_for(think_time_seconds)  # Deny hotkeys for the same amount of time as the think time

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
        self.screenshot_with_grid = screenshot.copy()
        cells = []
        board_position = [['' for _ in range(board_size)] for _ in range(board_size)]
        for i in range(board_size):
            for j in range(board_size):
                top_left = (j * cell_width, i * cell_height)
                bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
                cell = screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                cells.append(cell)
                
        # Perform color analysis using mean brightness to determine piece colors
        colors = self.determine_piece_colors(cells)
        
        # Define the chessboard coordinates based on player color
        board_coordinates = self.get_board_coordinates()

        for idx, (i, j) in enumerate([(i, j) for i in range(board_size) for j in range(board_size)]):
            top_left = (j * cell_width, i * cell_height)
            bottom_right = ((j + 1) * cell_width, (i + 1) * cell_height)
            cell = cells[idx]
            
            # Identify the piece in the cell using HOG and SVM
            piece_name, confidence = self.identify_piece_with_svm(cell)
            if piece_name and confidence > 0.8:  # Only consider predictions with high confidence
                # Add piece color label at the bottom of the cell if not identified as empty
                piece_color = colors[idx] if piece_name.lower() != "empty" else ""
                if piece_name.lower() != "empty":
                    color_label_y = bottom_right[1] - 10
                    color = (0, 0, 0) if piece_color == 'Black' else (255, 255, 255)
                    cv2.putText(self.screenshot_with_grid, piece_color, (top_left[0] + 5, color_label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
                    
                    # Update board position
                    piece_fen = 'n' if piece_name.lower() == 'knight' and piece_color == 'Black' else 'N' if piece_name.lower() == 'knight' and piece_color == 'White' else piece_name[0].lower() if piece_color == 'Black' else piece_name[0].upper()
                    board_position[i][j] = piece_fen
                
                # Use the piece color to adjust the final prediction if applicable
                if piece_color == "Black" and "White" in piece_name:
                    continue  # Skip if prediction does not match color
                if piece_color == "White" and "Black" in piece_name:
                    continue  # Skip if prediction does not match color
                
                cv2.putText(self.screenshot_with_grid, piece_name, (top_left[0] + 5, top_left[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            # Add coordinates in the middle of each cell with orange color
            coord = board_coordinates[i][j]
            coord_x = top_left[0] + cell_width // 2 - 10
            coord_y = top_left[1] + cell_height // 2 + 5
            cv2.putText(self.screenshot_with_grid, coord, (coord_x, coord_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1, cv2.LINE_AA)
            
            # Draw the grid
            cv2.rectangle(self.screenshot_with_grid, top_left, bottom_right, (255, 0, 0), 1)
        
        # Generate FEN notation
        castling_rights = self.check_castling_rights(board_position)
        fen_rows = []
        for row in board_position:
            empty_count = 0
            fen_row = ''
            for cell in row:
                if cell == '':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += cell
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        fen = '/'.join(fen_rows) + (' b' if self.player_color_var.get() == 'Black' else ' w') + f' {castling_rights} - 0 1'
        
        # Flip the FEN if the player is black to adjust the board perspective
        if self.player_color_var.get() == 'Black':
            fen_rows = fen.split(' ')[0].split('/')
            fen_rows = [row[::-1] for row in reversed(fen_rows)]
            fen = '/'.join(fen_rows) + (' b' if self.player_color_var.get() == 'Black' else ' w') + f' {castling_rights} - 0 1'

        print("FEN Notation:", fen)
        
        # Display the updated board with grid
        self.display_image(self.screenshot_with_grid)

        # Use a separate thread to get the best move to avoid blocking the GUI
        threading.Thread(target=self.get_best_move_and_draw, args=(fen,)).start()

    def check_castling_rights(self, board_position):
        white_castling_rights = {'K': True, 'Q': True}
        black_castling_rights = {'k': True, 'q': True}
        
        # Automatically determine if kings have been in check based on board state
        # Check if white king or rooks have moved or if there are pieces in the way for castling
        if board_position[7][4] != 'K' or board_position[7][7] != 'R' or board_position[7][5] or board_position[7][6]:
            white_castling_rights['K'] = False

        if board_position[7][4] != 'K' or board_position[7][0] != 'R' or board_position[7][1] or board_position[7][2] or board_position[7][3]:
            white_castling_rights['Q'] = False

        # Check if black king or rooks have moved or if there are pieces in the way for castling
        if board_position[0][4] != 'k' or board_position[0][7] != 'r' or board_position[0][5] or board_position[0][6]:
            black_castling_rights['k'] = False

        if board_position[0][4] != 'k' or board_position[0][0] != 'r' or board_position[0][1] or board_position[0][2] or board_position[0][3]:
            black_castling_rights['q'] = False

        # Build castling rights string
        castling_rights = ""
        castling_rights += 'K' if white_castling_rights['K'] else ''
        castling_rights += 'Q' if white_castling_rights['Q'] else ''
        castling_rights += 'k' if black_castling_rights['k'] else ''
        castling_rights += 'q' if black_castling_rights['q'] else ''
        return castling_rights if castling_rights else '-'

    def determine_piece_colors(self, cells):
        colors = []
        # Get the current threshold value from the slider
        brightness_threshold = self.threshold_value.get()
        for cell in cells:
            # Convert the cell to grayscale
            cell_gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            
            # Calculate the average brightness of the cell
            avg_brightness = np.mean(cell_gray)
            
            # Classify based on brightness threshold
            if avg_brightness > brightness_threshold:
                colors.append("White")
            else:
                colors.append("Black")
    
        return colors

    def get_best_move_and_draw(self, fen):
        start, end = self.get_best_move(fen)
        if start is None or end is None:
            print("No move available.")
            return

        print(f"The best move is from {start} to {end}.")
        
        # Now that we have the move, we need to update the GUI.
        # Tkinter GUI updates must be run on the main thread.
        self.root.after(0, self.highlight_best_move, start, end)
        self.root.after(0, self.highlight_over_screen, start, end)

    def highlight_over_screen(self, start, end):
        # Assume the selected area is a perfect square chessboard
        board_size = 8
        cell_width = (self.end_x - self.start_x) // board_size
        cell_height = (self.end_y - self.start_y) // board_size

        # Define the chessboard coordinates based on player color
        board_coordinates = self.get_board_coordinates()

        start_x, start_y = self.get_cell_coordinates(start, board_coordinates, cell_width, cell_height)
        end_x, end_y = self.get_cell_coordinates(end, board_coordinates, cell_width, cell_height)
        
        if start_x is not None and end_x is not None:
            # Destroy existing overlay boxes before creating new ones
            if hasattr(self, 'current_overlays'):
                for overlay in self.current_overlays:
                    overlay.destroy()
            else:
                self.current_overlays = []

            # Convert local coordinates to screen coordinates
            screen_start_x = self.start_x + start_x
            screen_start_y = self.start_y + start_y
            screen_end_x = self.start_x + end_x
            screen_end_y = self.start_y + end_y

            # Create a transparent tkinter window for drawing the highlight box for the start position
            overlay = tk.Toplevel(self.root)
            overlay.attributes("-transparentcolor", "magenta")
            overlay.attributes("-topmost", True)
            overlay.geometry(f"{cell_width}x{cell_height}+{screen_start_x}+{screen_start_y}")
            overlay.overrideredirect(True)

            canvas = tk.Canvas(overlay, width=cell_width, height=cell_height, bg='magenta', highlightthickness=0)
            canvas.pack()
            canvas.create_rectangle(0, 0, cell_width, cell_height, outline='green', width=5)

            # Add the overlay to the list of current overlays
            self.current_overlays.append(overlay)

            # Create a transparent tkinter window for drawing the highlight box for the end position
            overlay_end = tk.Toplevel(self.root)
            overlay_end.attributes("-transparentcolor", "magenta")
            overlay_end.attributes("-topmost", True)
            overlay_end.geometry(f"{cell_width}x{cell_height}+{screen_end_x}+{screen_end_y}")
            overlay_end.overrideredirect(True)

            canvas_end = tk.Canvas(overlay_end, width=cell_width, height=cell_height, bg='magenta', highlightthickness=0)
            canvas_end.pack()
            canvas_end.create_rectangle(0, 0, cell_width, cell_height, outline='red', width=5)

            # Add the overlay to the list of current overlays
            self.current_overlays.append(overlay_end)





    def highlight_best_move(self, start, end):
        # Assume the selected area is a perfect square chessboard
        board_size = 8
        cell_width = (self.end_x - self.start_x) // board_size
        cell_height = (self.end_y - self.start_y) // board_size

        # Define the chessboard coordinates based on player color
        board_coordinates = self.get_board_coordinates()

        start_x, start_y = self.get_cell_coordinates(start, board_coordinates, cell_width, cell_height)
        end_x, end_y = self.get_cell_coordinates(end, board_coordinates, cell_width, cell_height)
        
        if start_x is not None and end_x is not None:
            # Draw the best move on the original screenshot with grid
            cv2.rectangle(self.screenshot_with_grid, (start_x, start_y), (start_x + cell_width, start_y + cell_height), (0, 255, 0), 3)
            cv2.rectangle(self.screenshot_with_grid, (end_x, end_y), (end_x + cell_width, end_y + cell_height), (0, 0, 255), 3)
            
            # Display the result in the GUI
            self.display_image(self.screenshot_with_grid)

            # If the reanalyze checkbox is checked, reanalyze the board
            if self.reanalyze_var.get():
                threading.Thread(target=self.analyze_board).start()

    def get_best_move(self, fen):
        if self.stockfish is None:
            print("Stockfish is not initialized. Reinitializing...")
            self.initialize_stockfish()
            if self.stockfish is None:
                print("Failed to reinitialize Stockfish.")
                return None, None
        
        try:
            # Set the FEN position
            self.stockfish.set_fen_position(fen)
            
            # Get the best move from Stockfish
            think_time = self.think_time_slider.get()
            best_move = self.stockfish.get_best_move_time(think_time)
        except Exception as e:
            print(f"Stockfish process crashed: {e}. Reinitializing...")
            self.initialize_stockfish()
            if self.stockfish is None:
                return None, None
            self.stockfish.set_fen_position(fen)
            best_move = self.stockfish.get_best_move()
        
        if best_move is None:
            return None, None
        
         # **Promotion Check**:
        if len(best_move) == 5:
            best_move = best_move[:4]  # Strip off the promotion character (e.g., "q")

        
        # Split the move into starting and ending coordinates
        start_pos = best_move[:2]
        end_pos = best_move[2:]
        
        return start_pos, end_pos

    def get_cell_coordinates(self, coord, board_coordinates, cell_width, cell_height):
        for i, row in enumerate(board_coordinates):
            for j, board_coord in enumerate(row):
                if board_coord == coord:
                    return j * cell_width, i * cell_height
        return None, None

    def identify_piece_with_svm(self, cell):
        # Resize cell to a fixed size
        cell_resized = cv2.resize(cell, (64, 64))
        
        # Convert to grayscale
        cell_gray = cv2.cvtColor(cell_resized, cv2.COLOR_BGR2GRAY)
        
        # Extract HOG features
        features, _ = hog(cell_gray, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True, block_norm='L2-Hys')
        
        # Predict the piece using the SVM model
        prediction = self.svm_model.decision_function([features])
        confidence = max(prediction[0]) if len(prediction[0]) > 0 else 0
        predicted_class = self.svm_model.classes_[np.argmax(prediction)] if confidence > 0 else None
        return predicted_class, confidence

    def display_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.image_label.imgtk = imgtk
        self.image_label.configure(image=imgtk)

    def update_board_coordinates(self):
        self.analyze_board()

    def get_board_coordinates(self):
        player_color = self.player_color_var.get()
        board_size = 8
        if player_color == "White":
            return [[f'{chr(97 + j)}{8 - i}' for j in range(board_size)] for i in range(board_size)]
        else:
            return [[f'{chr(97 + (board_size - 1 - j))}{i + 1}' for j in range(board_size)] for i in range(board_size)]

    def on_space_press(self, event):
        self.analyze_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessBoardDetector(root)
    root.mainloop()
    keyboard.wait()  # Keep the program running to listen for hotkeys