import pytest
import os
import sys
from unittest.mock import MagicMock, patch
import base64

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional, continue without it
    pass

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from agentforge.apis.base_api import BaseModel, UnsupportedModalityError
from agentforge.apis.gemini_api import Gemini, GeminiVision
from agentforge.apis.mixins.vision_mixin import VisionMixin


class TestBaseModelVisionSupport:
    def test_base_model_text_only(self):
        """Test that BaseModel only supports text."""
        model = BaseModel("test-model")
        assert model.supported_modalities == {"text"}
        
        # Test that _prepare_image_payload raises UnsupportedModalityError
        with pytest.raises(UnsupportedModalityError):
            model._prepare_image_payload(["image.png"])
    
    def test_base_model_rejects_images(self):
        """Test that BaseModel rejects images when passed."""
        model = BaseModel("test-model")
        
        # Patch _prepare_prompt to avoid needing actual model_prompt
        with patch.object(model, '_prepare_prompt', return_value=[]):
            # Test that generate raises UnsupportedModalityError when images are passed
            with pytest.raises(UnsupportedModalityError):
                model.generate(None, images=["image.png"])


class TestVisionMixin:
    def test_vision_mixin_supported_modalities(self):
        """Test that VisionMixin supports both text and image."""
        class TestModel(VisionMixin, BaseModel):
            pass
        
        model = TestModel("test-model")
        assert model.supported_modalities == {"text", "image"}


class TestGeminiVision:
    def test_gemini_vision_inheritance(self):
        """Test that GeminiVision inherits from VisionMixin and Gemini."""
        assert issubclass(GeminiVision, VisionMixin)
        assert issubclass(GeminiVision, Gemini)
        
        model = GeminiVision("test-model")
        assert model.supported_modalities == {"text", "image"}
    
    def test_gemini_vision_merge_parts(self):
        """Test that _merge_parts correctly formats the request for Gemini."""
        model = GeminiVision("test-model")
        
        # Test with only text
        text_parts = {"text": "test prompt"}
        text_request = model._merge_parts(text_parts)
        assert text_request == {"contents": ["test prompt"]}
        
        # Test with text and image - skip actual image processing for unit test
        parts = {
            "text": "test prompt", 
            "image": []  # Empty for unit test - real processing happens in integration test
        }
        request = model._merge_parts(parts)
        assert request == {"contents": ["test prompt"]}

    @pytest.mark.integration
    def test_real_image_processing(self):
        """Test GeminiVision with a real image (test.jpg) and a simple prompt."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow is not installed, skipping real image processing test.")

        if not os.getenv('GOOGLE_API_KEY'):
            pytest.skip("GOOGLE_API_KEY not set, skipping real image processing test.")

        img_path = os.path.join(os.path.dirname(__file__), "test.jpg")
        assert os.path.exists(img_path), "test.jpg not found in multimedia tests directory."

        prompt = {"system": "You are a helpful assistant.", "user": "What is in this image?"}
        model = GeminiVision("gemini-2.5-flash-preview-04-17")
        response = model.generate(prompt, images=[img_path])
        assert response and isinstance(response, str) and len(response.strip()) > 0, "Model did not return a valid response."


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 