import pyautogui
import pytesseract
from PIL import Image, ImageOps

def search_letters_in_location(screen_location):
    if screen_location is None:
        raise ValueError("Screen location is not defined.")

    # Capture the screenshot of the defined area
    x1, y1, x2, y2 = screen_location
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

    # Invert the colors if the text is white on a black background
    screenshot = ImageOps.invert(screenshot.convert('RGB'))

    # Convert the screenshot to a format suitable for OCR
    screenshot = screenshot.convert('L')  # Convert to grayscale

    # Use pytesseract to extract text from the screenshot with a custom configuration
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    extracted_text = pytesseract.image_to_string(screenshot, config=custom_config).upper()  # Convert to uppercase

    # Filter out non-alphabetic characters and return the letters
    letters = ''.join(filter(str.isalpha, extracted_text))
    return letters

# Example usage
if __name__ == "__main__":
    screen_location = (100, 100, 300, 200)  # Example coordinates
    letters = search_letters_in_location(screen_location)
    print(f"Extracted letters: {letters}")