import cv2
import pytesseract

def imagetotxt(image_path):
    """
    Extract text from an image using OCR (Optical Character Recognition).

    This function uses OpenCV to load and preprocess the image, and Tesseract OCR
    to extract text from the preprocessed image.

    Args:
        image_path (str): The file path to the image.

    Returns:
        str: The extracted text from the image.

    Raises:
        FileNotFoundError: If the specified image file does not exist.
        ValueError: If the image file is invalid or cannot be read.
        ImportError: If required libraries (cv2 or pytesseract) are not installed.
        Exception: For any other unexpected errors during execution.
    """
    try:
        # Load the image
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Unable to read the image file: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Use Tesseract to extract text from the image
        extracted_text = pytesseract.image_to_string(gray)
        
        return extracted_text.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"The image file does not exist: {image_path}")
    except ImportError as e:
        raise ImportError(f"Required library not installed: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred while processing the image: {str(e)}")

# Usage example (commented out)
# if __name__ == "__main__":
#     try:
#         image_path = "path/to/your/image.jpg"  # Replace with the path to your image
#         text = imagetotxt(image_path)
#         print("Extracted text:")
#         print(text)
#     except Exception as e:
#         print(f"Error: {str(e)}")
