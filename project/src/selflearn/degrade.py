"""
SelfLearn - Image degradation API with 9 types of distortions
"""
import random
from typing import Tuple, Optional
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw


class DegradeAPI:
    """API for applying various degradations to images."""
    
    @staticmethod
    def apply(
        image: Image.Image,
        degradation_type: str,
        severity: float = 0.5
    ) -> Image.Image:
        """
        Apply degradation to an image.
        
        Args:
            image: Input PIL Image
            degradation_type: One of the 9 degradation types
            severity: Float in [0.0, 1.0] controlling intensity
        
        Returns:
            Degraded PIL Image
        """
        if severity < 0.0 or severity > 1.0:
            raise ValueError("Severity must be between 0.0 and 1.0")
        
        methods = {
            'gaussian_noise': DegradeAPI._gaussian_noise,
            'salt_pepper': DegradeAPI._salt_pepper,
            'blur': DegradeAPI._blur,
            'brightness': DegradeAPI._brightness,
            'contrast': DegradeAPI._contrast,
            'rotation': DegradeAPI._rotation,
            'occlusion': DegradeAPI._occlusion,
            'compression': DegradeAPI._compression,
            'distortion': DegradeAPI._distortion
        }
        
        if degradation_type not in methods:
            raise ValueError(f"Unknown degradation type: {degradation_type}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return methods[degradation_type](image, severity)
    
    @staticmethod
    def _gaussian_noise(image: Image.Image, severity: float) -> Image.Image:
        """Add Gaussian noise to image."""
        import numpy as np
        
        img_array = np.array(image)
        std = severity * 50  # Max std of 50 at severity=1.0
        
        noise = np.random.normal(0, std, img_array.shape).astype(np.int16)
        noisy_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(noisy_array)
    
    @staticmethod
    def _salt_pepper(image: Image.Image, severity: float) -> Image.Image:
        """Add salt and pepper noise."""
        import numpy as np
        
        img_array = np.array(image)
        prob = severity * 0.3  # Max 30% pixels affected
        
        mask = np.random.random(img_array.shape[:2])
        salt_mask = mask < (prob / 2)
        pepper_mask = mask > (1 - prob / 2)
        
        img_array[salt_mask] = 255
        img_array[pepper_mask] = 0
        
        return Image.fromarray(img_array)
    
    @staticmethod
    def _blur(image: Image.Image, severity: float) -> Image.Image:
        """Apply Gaussian blur."""
        # Map severity to kernel size (3 to 15)
        kernel_size = int(3 + severity * 12)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        return image.filter(ImageFilter.GaussianBlur(radius=kernel_size // 2))
    
    @staticmethod
    def _brightness(image: Image.Image, severity: float) -> Image.Image:
        """Adjust brightness."""
        # Map severity to factor (0.1 to 2.0)
        factor = 0.1 + severity * 1.9
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def _contrast(image: Image.Image, severity: float) -> Image.Image:
        """Adjust contrast."""
        # Map severity to factor (0.1 to 2.0)
        factor = 0.1 + severity * 1.9
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def _rotation(image: Image.Image, severity: float) -> Image.Image:
        """Rotate image."""
        # Map severity to angle (-45 to 45 degrees)
        angle = (severity - 0.5) * 90
        return image.rotate(angle, expand=False, resample=Image.BICUBIC)
    
    @staticmethod
    def _occlusion(image: Image.Image, severity: float) -> Image.Image:
        """Add occlusion (black rectangle)."""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Block size ratio (5% to 30% of image)
        block_ratio = 0.05 + severity * 0.25
        block_w = int(width * block_ratio)
        block_h = int(height * block_ratio)
        
        # Random position
        x = random.randint(0, width - block_w)
        y = random.randint(0, height - block_h)
        
        draw.rectangle([x, y, x + block_w, y + block_h], fill=(0, 0, 0))
        
        return image
    
    @staticmethod
    def _compression(image: Image.Image, severity: float) -> Image.Image:
        """Simulate JPEG compression artifacts."""
        import io
        
        # Map severity to quality (95 to 10)
        quality = int(95 - severity * 85)
        quality = max(10, min(95, quality))
        
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        
        return Image.open(buffer)
    
    @staticmethod
    def _distortion(image: Image.Image, severity: float) -> Image.Image:
        """Apply geometric distortion (wave effect)."""
        import numpy as np
        
        width, height = image.size
        img_array = np.array(image)
        
        # Create distortion map
        amplitude = severity * 10
        frequency = 0.1 + severity * 1.9
        
        distorted = np.zeros_like(img_array)
        
        for y in range(height):
            for x in range(width):
                # Wave distortion
                dx = int(amplitude * np.sin(2 * np.pi * frequency * y / height))
                dy = int(amplitude * np.cos(2 * np.pi * frequency * x / width))
                
                src_x = min(max(x + dx, 0), width - 1)
                src_y = min(max(y + dy, 0), height - 1)
                
                distorted[y, x] = img_array[src_y, src_x]
        
        return Image.fromarray(distorted)
    
    @staticmethod
    def get_all_types() -> list:
        """Return list of all degradation types."""
        return [
            'gaussian_noise',
            'salt_pepper',
            'blur',
            'brightness',
            'contrast',
            'rotation',
            'occlusion',
            'compression',
            'distortion'
        ]
