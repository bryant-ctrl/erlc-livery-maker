"""
API Client - Handles communication with Replicate API for image generation
"""
import os
import io
import base64
import replicate
from PIL import Image
from typing import Optional
import time


class ReplicateAPIClient:
    """Client for Replicate API image inpainting"""

    def __init__(self, api_key: str, model: str = "stability-ai/stable-diffusion-inpainting:95b7223104132402a9ae91cc677285bc5eb997834bd2349fa486f53910fd68b3"):
        """
        Initialize Replicate API client

        Args:
            api_key: Replicate API key
            model: Model identifier to use for inpainting (with version hash)
        """
        self.api_key = api_key
        self.model = model

        # Set API key in environment
        if api_key:
            os.environ["REPLICATE_API_TOKEN"] = api_key

    def image_to_data_uri(self, image: Image.Image) -> str:
        """Convert PIL Image to data URI for API submission"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def generate_inpainting(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        view: str = "",
        negative_prompt: str = "blurry, low quality, distorted, deformed, text, words, letters",
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5
    ) -> Optional[Image.Image]:
        """
        Generate inpainted image using Replicate API

        Args:
            image: Original template image
            mask: Inpainting mask (white = paint, black = preserve)
            prompt: User prompt for livery design
            view: View angle (Front, Rear, Left, Right, Top)
            negative_prompt: Things to avoid in generation
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt

        Returns:
            PIL Image of generated result, or None if failed
        """
        if not self.api_key:
            raise ValueError("Replicate API key not set")

        try:
            # Build clean prompt - just the user's design request
            full_prompt = f"{prompt}"
            if view:
                full_prompt += f", {view.lower()} side view"
            # Add quality/style descriptors that help without confusing the AI
            full_prompt += ", high quality vehicle livery, professional design, clean graphics"

            print(f"Generating with prompt: {full_prompt}")

            # Convert images to data URIs
            image_uri = self.image_to_data_uri(image)
            mask_uri = self.image_to_data_uri(mask)

            # Determine model type and use appropriate parameters
            if "ideogram" in self.model.lower():
                # Ideogram models (best for text)
                input_params = {
                    "image": image_uri,
                    "mask": mask_uri,
                    "prompt": full_prompt,
                    "magic_prompt_option": "Auto",  # Optimize prompts automatically
                    "style_type": "Auto"
                }
            elif "flux-fill-pro" in self.model or "flux" in self.model.lower():
                # FLUX models use different parameter names
                input_params = {
                    "image": image_uri,
                    "mask": mask_uri,
                    "prompt": full_prompt,
                    "steps": num_inference_steps,
                    "guidance": guidance_scale * 8,  # FLUX uses higher scale (1.5-100 vs 1-20)
                    "output_format": "png"
                }
            else:
                # Stable Diffusion models use original parameter names
                input_params = {
                    "image": image_uri,
                    "mask": mask_uri,
                    "prompt": full_prompt,
                    "negative_prompt": negative_prompt,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                }

            # Run the model
            output = replicate.run(self.model, input=input_params)

            # Handle different output formats
            if isinstance(output, list) and len(output) > 0:
                output_url = output[0]
            elif isinstance(output, str):
                output_url = output
            else:
                print(f"Unexpected output format: {type(output)}")
                return None

            # Download the result
            import requests
            response = requests.get(output_url)
            result_image = Image.open(io.BytesIO(response.content))

            print(f"Successfully generated image: {result_image.size}")
            return result_image

        except Exception as e:
            print(f"Error generating image: {e}")
            import traceback
            traceback.print_exc()
            return None

    def test_connection(self) -> bool:
        """Test if API connection is working"""
        if not self.api_key:
            return False

        try:
            # Simple test - just check if we can initialize
            os.environ["REPLICATE_API_TOKEN"] = self.api_key
            return True
        except Exception as e:
            print(f"API test failed: {e}")
            return False


class FluxAPIClient(ReplicateAPIClient):
    """Client specifically for FLUX.1 inpainting model"""

    def __init__(self, api_key: str):
        super().__init__(api_key, model="black-forest-labs/flux-1.1-pro")

    def generate_inpainting(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        view: str = "",
        **kwargs
    ) -> Optional[Image.Image]:
        """
        Generate using FLUX model (different parameters)
        Note: FLUX might not support inpainting directly,
        so this is a placeholder for future FLUX inpainting models
        """
        # For now, fall back to stable diffusion
        client = ReplicateAPIClient(self.api_key)
        return client.generate_inpainting(image, mask, prompt, view, **kwargs)


if __name__ == "__main__":
    # Test the API client
    import json

    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            api_key = config.get("replicate_api_key", "")

            if api_key:
                client = ReplicateAPIClient(api_key)
                print(f"API client initialized")
                print(f"Connection test: {'Success' if client.test_connection() else 'Failed'}")
            else:
                print("No API key found in config.json")
    else:
        print("config.json not found")
