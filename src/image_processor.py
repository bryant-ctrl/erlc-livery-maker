"""
Image Processor - Handles mask generation, image loading, and compositing
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple


class ImageProcessor:
    """Processes template images and generates masks for inpainting"""

    def __init__(self):
        pass

    def load_template(self, template_path: Path) -> Image.Image:
        """Load a template image"""
        return Image.open(template_path).convert("RGB")

    def create_mask(self, image: Image.Image, tolerance: int = 30) -> Image.Image:
        """
        Create an inpainting mask from template image.
        White pixels = area to inpaint (vehicle body)
        Black pixels = area to preserve (background, windows, wheels, etc.)

        Args:
            image: PIL Image of the template
            tolerance: Color tolerance for white detection (0-255)

        Returns:
            PIL Image mask (L mode - grayscale)
        """
        # Convert PIL to numpy array
        img_array = np.array(image)

        # Convert to HSV for better white detection
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

        # Define range for white color
        # White in HSV: High Value (V), Low Saturation (S)
        lower_white = np.array([0, 0, 255 - tolerance])
        upper_white = np.array([180, tolerance, 255])

        # Create mask where white pixels are 255, others are 0
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fill small holes
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove noise

        # Convert back to PIL Image
        return Image.fromarray(mask, mode='L')

    def save_image(self, image: Image.Image, output_path: Path) -> None:
        """Save image to disk"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, "PNG")

    def composite_result(self, original: Image.Image, generated: Image.Image,
                        mask: Image.Image) -> Image.Image:
        """
        Composite generated image over original template using mask.
        This ensures crisp preservation of non-painted areas.

        Args:
            original: Original template image
            generated: AI-generated inpainted image
            mask: Mask used for inpainting (white = painted area)

        Returns:
            Composited final image
        """
        # Ensure all images are the same size
        if generated.size != original.size:
            generated = generated.resize(original.size, Image.Resampling.LANCZOS)

        if mask.size != original.size:
            mask = mask.resize(original.size, Image.Resampling.LANCZOS)

        # Convert mask to binary (0 or 255)
        mask_array = np.array(mask)
        mask_array = (mask_array > 127).astype(np.uint8) * 255
        mask_binary = Image.fromarray(mask_array, mode='L')

        # Composite: where mask is white, use generated; where black, use original
        result = Image.composite(generated, original, mask_binary)

        return result

    def prepare_for_api(self, image: Image.Image, mask: Image.Image,
                       max_size: int = 1024, min_size: int = 256) -> Tuple[Image.Image, Image.Image]:
        """
        Prepare image and mask for API submission by resizing if needed.
        Some APIs have size limits and minimum requirements.

        Args:
            image: Template image
            mask: Inpainting mask
            max_size: Maximum dimension size
            min_size: Minimum dimension size (for FLUX and other models)

        Returns:
            Tuple of (resized_image, resized_mask)
        """
        width, height = image.size

        # Check if resizing is needed
        if max(width, height) > max_size:
            # Calculate new dimensions maintaining aspect ratio
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))

            # Ensure minimum size is met
            if new_width < min_size:
                scale = min_size / new_width
                new_width = min_size
                new_height = int(new_height * scale)
            if new_height < min_size:
                scale = min_size / new_height
                new_height = min_size
                new_width = int(new_width * scale)

            # Resize both image and mask
            image_resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            mask_resized = mask.resize((new_width, new_height), Image.Resampling.LANCZOS)

            return image_resized, mask_resized

        return image, mask


if __name__ == "__main__":
    # Test the image processor
    processor = ImageProcessor()

    # Test with a template
    test_template = Path("templates/Bullhorn Determinator SFP Fury 2022 /Challenger_Template_Left.png")

    if test_template.exists():
        print(f"Loading template: {test_template}")
        img = processor.load_template(test_template)
        print(f"Template size: {img.size}")

        print("Generating mask...")
        mask = processor.create_mask(img)

        # Save mask for inspection
        processor.save_image(mask, Path("output/test_mask.png"))
        print("Mask saved to: output/test_mask.png")
    else:
        print(f"Template not found: {test_template}")
