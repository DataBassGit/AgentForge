import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from agentforge.utils.Logger import Logger
import base64
import numpy as np
from PIL import Image
from typing import Union, List, Any
from io import BytesIO

# Get API key from Env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


class Gemini_With_Vision:
    """
    A class for interacting with Google's Generative AI models to generate text based on provided prompts and images.
    
    Extends the base Gemini functionality to handle both text and vision inputs, including error handling 
    for rate limits and retries for failed requests.

    Attributes:
        num_retries (int): The number of times to retry generating text upon encountering errors.
    """
    num_retries = 4

    def __init__(self, model):
        """
        Initializes the Gemini_With_Vision class with the vision-capable model.

        Parameters:
            model (str): The identifier of the Google Generative AI model to use. Defaults to gemini-pro-vision.
        """
        self._model = genai.GenerativeModel(model)
        self.logger = None

    def _process_image_input(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> Any:
        """
        Process different types of image inputs into a format acceptable by Gemini.
        
        Parameters:
            image_input: Can be:
                - Path to image file (str)
                - Base64 encoded image string
                - Bytes object
                - PIL Image object
                - NumPy array
        
        Returns:
            Processed image in a format acceptable by Gemini
        """
        try:
            # Verify file type and size before processing
            def verify_image(img: Image.Image) -> bool:
                """Verify image format and size"""
                allowed_formats = {'JPEG', 'JPG', 'PNG', 'GIF', 'WEBP'}
                max_size = 20 * 1024 * 1024  # 20MB limit
                
                # Check format
                if img.format and img.format.upper() not in allowed_formats:
                    self.logger.log(f"Unsupported image format: {img.format}", 'warning')
                    return False
                
                # Check file size
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format=img.format or 'PNG')
                size = img_byte_arr.tell()
                if size > max_size:
                    self.logger.log(f"Image size ({size/1024/1024:.2f}MB) exceeds 20MB limit", 'warning')
                    return False
                
                return True

            self.logger.log(f"Processing image input of type: {type(image_input)}", 'info')

            if isinstance(image_input, str):
                # Check if it's a base64 string
                if image_input.startswith(('data:image', 'base64:')):
                    self.logger.log("Processing base64 encoded image", 'info')
                    # Extract the base64 data
                    base64_data = image_input.split('base64,')[-1]
                    image_bytes = base64.b64decode(base64_data)
                    img = Image.open(BytesIO(image_bytes))
                else:
                    # Assume it's a file path
                    self.logger.log(f"Loading image from path: {image_input}", 'info')
                    img = Image.open(image_input)
            
            elif isinstance(image_input, bytes):
                self.logger.log("Processing bytes input", 'info')
                img = Image.open(BytesIO(image_input))
            
            elif isinstance(image_input, np.ndarray):
                self.logger.log("Processing NumPy array input", 'info')
                img = Image.fromarray(image_input)
            
            elif isinstance(image_input, Image.Image):
                self.logger.log("Processing PIL Image input", 'info')
                img = image_input
            
            else:
                error_msg = f"Unsupported image input type: {type(image_input)}"
                self.logger.log(error_msg, 'error')
                raise ValueError(error_msg)

            # Verify the processed image
            if not verify_image(img):
                error_msg = "Image verification failed"
                self.logger.log(error_msg, 'error')
                raise ValueError(error_msg)

            self.logger.log(f"Successfully processed image: {img.format} {img.size}", 'info')
            return img
                
        except Exception as e:
            error_msg = f"Error processing image input: {str(e)}"
            self.logger.log(error_msg, 'error')
            raise

    def generate_response(self, model_prompt, image_parts=None, **params):
        """
        Generates text based on the provided prompts, images, and additional parameters for the model.

        Parameters:
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            image_parts (Union[List[Union[str, bytes, Image.Image, np.ndarray]], 
                             Union[str, bytes, Image.Image, np.ndarray]]): 
                Single image or list of images in various formats:
                - File paths
                - Base64 encoded strings
                - Bytes objects
                - PIL Image objects
                - NumPy arrays
            **params: Arbitrary keyword arguments providing additional options to the model.

        Returns:
            str or None: The generated text from the model or None if the operation fails after retry attempts.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        prompt = '\n\n'.join([model_prompt.get('System', ''), model_prompt.get('User', '')])
        
        # Combine text prompt with images if provided
        content = [prompt]
        
        if image_parts is not None:
            # Convert single image to list for uniform processing
            if not isinstance(image_parts, list):
                image_parts = [image_parts]
            
            # Process each image input
            processed_images = []
            for img in image_parts:
                try:
                    processed_img = self._process_image_input(img)
                    processed_images.append(processed_img)
                except Exception as e:
                    self.logger.log(f"Error processing image: {str(e)}", 'error')
                    continue
            
            content.extend(processed_images)

        # Will retry to get response if a rate limit or bad gateway error is received
        reply = None
        for attempt in range(self.num_retries):
            backoff = 8 ** (attempt + 2)
            try:
                response = self._model.generate_content(
                    content,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    },
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=params.get("max_new_tokens", 2048),
                        temperature=params.get("temperature", 0.7),
                        top_p=params.get("top_p", 1),
                        top_k=params.get("top_k", 1),
                        candidate_count=max(params.get("candidate_count", 1), 1)
                    )
                )

                reply = response.text
                self.logger.log_response(reply)
                print(response)

                break

            except Exception as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        # reply will be none if we have failed above
        if reply is None:
            self.logger.log("\n\nError: Failed to get Gemini Response", 'critical')

        return reply


if __name__ == "__main__":
    # Initialize the model
    gemini_vision = Gemini_With_Vision("gemini-1.5-flash")

    # Test 1: Text-only input
    print("Testing")
    text_response = gemini_vision.generate_response({
        "System": "You are a helpful assistant.",
        "User": "What is the capital of France?"
    }, agent_name="TestAgent")
    print("\nText-only test response:", text_response)

    # Test 2: Image + Text input
    try:
        from PIL import Image
        import requests
        from io import BytesIO

        # Download a sample image from the internet
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques%2C_Paris_ao%C3%BBt_2014_%282%29.jpg/1200px-La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques%2C_Paris_ao%C3%BBt_2014_%282%29.jpg"
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # Generate response with image
        vision_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=[image], agent_name="TestAgent")
        print("\nImage test response:", vision_response)

    except Exception as e:
        print(f"\nError during image test: {str(e)}")

    # Test 3: Base64 image input
    try:
        # Convert the previous image to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        base64_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=f"data:image/jpeg;base64,{img_str}", agent_name="TestAgent")
        print("\nBase64 image test response:", base64_response)

    except Exception as e:
        print(f"\nError during base64 image test: {str(e)}")

    # Test 4: NumPy array input
    try:
        import numpy as np
        # Convert PIL image to NumPy array
        np_image = np.array(image)
        numpy_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=np_image, agent_name="TestAgent")
        print("\nNumPy array test response:", numpy_response)

    except Exception as e:
        print(f"\nError during NumPy array test: {str(e)}")

    # Test 5: File type verification
    try:
        # Create a temporary BMP image (unsupported format)
        temp_image = Image.new('RGB', (100, 100), color='red')
        buffered = BytesIO()
        temp_image.save(buffered, format="BMP")
        bmp_data = buffered.getvalue()
        
        # This should raise an error due to unsupported format
        bmp_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=bmp_data, agent_name="TestAgent")
        print("\nBMP image test response:", bmp_response)

    except Exception as e:
        print(f"\nExpected error during BMP image test: {str(e)}")