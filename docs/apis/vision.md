# Vision and Multimodal Support

AgentForge supports image and multimodal prompts for APIs that implement vision capabilities.

## VisionMixin

- `VisionMixin` is a mixin class that adds image/multimodal support to API integrations.
- Used by `GeminiVision` and can be used in custom APIs.

## How to Use

- To use image/multimodal support, select an API/model that supports images (e.g., `GeminiVision`).
- Pass images to the `generate` method via the `images` argument.

## Example

```python
response = agent.model.generate(model_prompt, images=[image_data], **params)
```

## Configuration Example

```yaml
model_library:
  gemini_api:
    GeminiVision:
      models:
        gemini-vision:
          identifier: "gemini-vision"
          params:
            temperature: 0.7
```

## Notes
- Not all APIs support images. Check the API documentation for support.
- For custom APIs, inherit from `VisionMixin` and implement required methods. 