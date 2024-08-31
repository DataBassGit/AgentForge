import cv2
import pytesseract

def imagetotxt(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to extract text from the image
    extracted_text = pytesseract.image_to_string(gray)
    return extracted_text