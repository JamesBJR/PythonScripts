import cv2
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog

class MinesweeperHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper Helper GUI")
        self.running = False
        self.thread = None
        self.template_path = 'minesweeper_template.png'

        self.start_button = tk.Button(self.root, text="Start Search", command=self.start_search)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Search", command=self.stop_search)
        self.stop_button.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Select Board Area", command=self.select_board_area)
        self.select_button.pack(pady=10)

        self.choose_template_button = tk.Button(self.root, text="Choose Template Path", command=self.choose_template_path)
        self.choose_template_button.pack(pady=10)

    def start_search(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.find_minesweeper_board, args=(self.template_path,))
            self.thread.start()

    def stop_search(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            cv2.destroyAllWindows()

    def select_board_area(self):
        self.root.withdraw()
        tkinter.messagebox.showinfo("Info", "Select the Minesweeper board area by clicking and dragging.")
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        roi = cv2.selectROI("Select Board Area", screen_np, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select Board Area")
        self.root.deiconify()

        if roi != (0, 0, 0, 0):
            x, y, w, h = roi
            board_image = screen_np[y:y+h, x:x+w]
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                cv2.imwrite(save_path, cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY))
                tkinter.messagebox.showinfo("Success", f"Template saved as '{save_path}'")

    def choose_template_path(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if path:
            self.template_path = path
            tkinter.messagebox.showinfo("Template Selected", f"Template path set to '{self.template_path}'")

    def find_minesweeper_board(self, template_path):
        try:
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                raise FileNotFoundError(f"Template image '{template_path}' not found.")
        except FileNotFoundError as e:
            print(e)
            tkinter.messagebox.showerror("Error", str(e))
            self.running = False
            return

        while self.running:
            # Capture the screen
            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

            # Match the template to find the board
            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(result >= threshold)

            for pt in zip(*loc[::-1]):
                bottom_right = (pt[0] + template.shape[1], pt[1] + template.shape[0])
                cv2.rectangle(screen_np, pt, bottom_right, (0, 0, 255), 2)

            # Display the screen with the detected board
            cv2.imshow('Minesweeper Detector', screen_np)

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperHelper(root)
    root.mainloop()