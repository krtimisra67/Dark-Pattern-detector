import cv2
import numpy as np
import pyautogui
import easyocr
import re
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Initialize main Tkinter window
root = tk.Tk()
root.title("Dark Pattern Detector")
root.geometry("700x700")

# Placeholder labels for uploaded image and extracted text
image_label = Label(root)
text_label = Label(root, text="Extracted Text will appear here", wraplength=600, justify="left")
dark_pattern_label = Label(root, text="Detected Dark Patterns will appear here", wraplength=600, justify="left")

# Enhanced preprocessing of the image using adaptive thresholding
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Increase contrast
    alpha = 1.5  # Contrast control
    beta = 0     # Brightness control
    processed_img = cv2.convertScaleAbs(processed_img, alpha=alpha, beta=beta)
    
    # Apply morphological operations to enhance text
    kernel = np.ones((2, 2), np.uint8)
    processed_img = cv2.morphologyEx(processed_img, cv2.MORPH_CLOSE, kernel)
    processed_img = cv2.morphologyEx(processed_img, cv2.MORPH_OPEN, kernel)
    
    return processed_img

# Function to perform OCR on an image with EasyOCR
def ocr_image(image):
    preprocessed_img = preprocess_image(image)
    results = reader.readtext(preprocessed_img, detail=0)  # detail=0 returns only the recognized text
    
    # Combine all detected text segments into a single string
    text = " ".join(results)
    return text

# Function to detect dark patterns in text
def detect_dark_patterns(text):
    # Define dark pattern types with associated example phrases
    patterns = {
        "FOMO": [
            r"(?i)don't delay|Lowest Price in \d days|Save \d+% more with Subscribe & Save|ends soon|high demand|exclusive deal|ending soon|last few left|only a few left|limited time only",
        ],
        "False Scarcity": [
            r"(?i)limited stock|Only \d+ left|while supplies last|act fast|limited edition|exclusive offer|limited quantity|grab yours now|few items left|running out|last opportunity|almost gone|final call",
        ],
        "False Urgency": [
            r"(?i)Order within \d+ hrs|ends in \d+ mins|timer|limited time|get it now|don't wait|final hours|hurry up|only today|ending soon|limited availability|last chance|act now",
        ]
    }

    # Find matches for each pattern type
    detected_patterns = {pattern_type: [] for pattern_type in patterns}
    for pattern_type, regex_list in patterns.items():
        for regex in regex_list:
            matches = re.findall(regex, text)
            if matches:
                detected_patterns[pattern_type].extend(matches)
    
    return detected_patterns

# Function to capture screenshot and display results
def capture_screenshot():
    img = pyautogui.screenshot()
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Process the screenshot with OCR and dark pattern detection
    extracted_text = ocr_image(cv_img)
    detected_patterns = detect_dark_patterns(extracted_text)
    
    # Generate text for each dark pattern type
    fomo_text = ', '.join(detected_patterns["FOMO"]) if detected_patterns["FOMO"] else "No FOMO patterns detected."
    scarcity_text = ', '.join(detected_patterns["False Scarcity"]) if detected_patterns["False Scarcity"] else "No False Scarcity patterns detected."
    urgency_text = ', '.join(detected_patterns["False Urgency"]) if detected_patterns["False Urgency"] else "No False Urgency patterns detected."
    
    # Update UI elements with extracted text and detected patterns
    text_label.config(text=f"Extracted Text:\n{extracted_text}")
    dark_pattern_label.config(text=f"Detected Patterns:\nFOMO: {fomo_text}\nFalse Scarcity: {scarcity_text}\nFalse Urgency: {urgency_text}")
    
    # Convert and display preprocessed image in the GUI
    preprocessed_img = preprocess_image(cv_img)
    img_pil = Image.fromarray(preprocessed_img)
    img_pil.thumbnail((400, 400))  # Resize for display
    img_tk = ImageTk.PhotoImage(img_pil)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    image_label.pack()

# GUI Elements
capture_button = tk.Button(root, text="Capture Screenshot", command=capture_screenshot)
capture_button.pack(pady=20)
image_label.pack(pady=10)
text_label.pack(pady=10)
dark_pattern_label.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
