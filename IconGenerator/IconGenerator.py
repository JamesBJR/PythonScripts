from PIL import Image
import tkinter as tk
from tkinter import filedialog

def generate_icon(input_image_path, output_icon_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]):
    """
    Generate a full icon file from an input image.

    :param input_image_path: Path to the input image file.
    :param output_icon_path: Path to save the generated icon file.
    :param sizes: List of sizes for the icon.
    """
    # Open the input image
    img = Image.open(input_image_path).convert("RGBA")
    
    # Save the images as an icon file with multiple sizes
    img.save(output_icon_path, format='ICO', sizes=sizes)

def convert_to_png(input_image_path, output_png_path):
    """
    Convert an image to PNG format.

    :param input_image_path: Path to the input image file.
    :param output_png_path: Path to save the converted PNG file.
    """
    img = Image.open(input_image_path).convert("RGBA")
    img.save(output_png_path, format='PNG')

def select_file():
    file_path = filedialog.askopenfilename()
    return file_path

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".ico", filetypes=[("ICO files", "*.ico"), ("PNG files", "*.png")])
    return file_path

def on_generate_icon():
    input_path = input_path_entry.get()
    if input_path:
        output_path = save_file()
        if output_path:
            generate_icon(input_path, output_path)

def on_convert_to_png():
    input_path = input_path_entry.get()
    if input_path:
        output_path = save_file()
        if output_path:
            convert_to_png(input_path, output_path)

# Create the GUI
root = tk.Tk()
root.title("Icon Generator")

input_path_label = tk.Label(root, text="Image Path:")
input_path_label.pack(pady=5)

input_path_entry = tk.Entry(root, width=50)
input_path_entry.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=lambda: input_path_entry.insert(0, select_file()))
browse_button.pack(pady=5)

generate_icon_button = tk.Button(root, text="Generate Icon", command=on_generate_icon)
generate_icon_button.pack(pady=10)

convert_to_png_button = tk.Button(root, text="Convert to PNG", command=on_convert_to_png)
convert_to_png_button.pack(pady=10)

root.mainloop()
