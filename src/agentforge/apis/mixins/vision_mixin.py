import base64
from pathlib import Path
import io

try:
    from PIL import Image  # Pillow: lightweight fork of PIL
except ImportError as e:
    Image = None

class VisionMixin:
    """Shared helpers + capability flag for image modalities."""
    supported_modalities = {"text", "image"}

    def _prepare_image_payload(self, images):
        if Image is None:
            raise ImportError("Vision support requires Pillow.  pip install pillow")

        def to_png_b64(obj):
            if isinstance(obj, (str, Path)):
                data = Path(obj).read_bytes()
            elif isinstance(obj, bytes):
                data = obj
            elif isinstance(obj, Image.Image):
                buf = io.BytesIO()
                obj.save(buf, format="PNG")
                data = buf.getvalue()
            else:
                raise TypeError(f"Unsupported image input: {type(obj)}")
            return base64.b64encode(data).decode()

        parts = []
        for img in images:
            b64 = to_png_b64(img)
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}"}
            })
        return parts 