"""
SelfLearn - Image synthesizer for generating base images
"""
import random
from typing import Tuple, Optional, Union
from PIL import Image, ImageDraw, ImageFont


class Synthesizer:
    """Synthesizer for generating base images with digits, shapes, and text."""
    
    def __init__(
        self,
        size: Tuple[int, int] = (64, 64),
        background_color: Union[str, Tuple[int, int, int]] = 'white',
        foreground_color: Optional[Union[str, Tuple[int, int, int]]] = None
    ):
        """
        Initialize synthesizer.
        
        Args:
            size: Image size (width, height)
            background_color: Background color ('white', 'black', or RGB tuple)
            foreground_color: Foreground color or 'random' for random colors
        """
        self.size = size
        self.bg_color = self._parse_color(background_color, default=(255, 255, 255))
        self.fg_color = foreground_color
    
    def _parse_color(
        self,
        color: Union[str, Tuple[int, int, int]],
        default: Tuple[int, int, int] = (0, 0, 0)
    ) -> Tuple[int, int, int]:
        """Parse color string or return RGB tuple."""
        if isinstance(color, tuple):
            return color
        
        colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128)
        }
        
        if isinstance(color, str):
            if color == 'random':
                return (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
            return colors.get(color.lower(), default)
        
        return default
    
    def generate_digit(
        self,
        digit: int,
        font_size: int = 40,
        position: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """
        Generate image with a digit.
        
        Args:
            digit: Digit 0-9
            font_size: Font size in pixels
            position: (x, y) position or None for center
        
        Returns:
            PIL Image with digit
        """
        if not 0 <= digit <= 9:
            raise ValueError("Digit must be between 0 and 9")
        
        img = Image.new('RGB', self.size, self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
            except (IOError, OSError):
                font = ImageFont.load_default()
        
        text = str(digit)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if position is None:
            # Center the text
            x = (self.size[0] - text_width) // 2
            y = (self.size[1] - text_height) // 2
        else:
            x, y = position
        
        fg = self._parse_color(self.fg_color, default=(0, 0, 0)) if self.fg_color else (0, 0, 0)
        draw.text((x, y), text, fill=fg, font=font)
        
        return img
    
    def generate_shape(
        self,
        shape_type: str,
        size_factor: float = 0.6,
        position: Optional[Tuple[int, int]] = None,
        rotation: float = 0.0
    ) -> Image.Image:
        """
        Generate image with a geometric shape.
        
        Args:
            shape_type: One of 'circle', 'rectangle', 'triangle', 'line'
            size_factor: Size relative to image (0.0 to 1.0)
            position: Center position or None for center
            rotation: Rotation angle in degrees
        
        Returns:
            PIL Image with shape
        """
        img = Image.new('RGB', self.size, self.bg_color)
        draw = ImageDraw.Draw(img)
        
        fg = self._parse_color(self.fg_color, default=(0, 0, 0)) if self.fg_color else (0, 0, 0)
        
        width, height = self.size
        shape_size = int(min(width, height) * size_factor)
        
        if position is None:
            cx, cy = width // 2, height // 2
        else:
            cx, cy = position
        
        half = shape_size // 2
        
        if shape_type == 'circle':
            draw.ellipse(
                [cx - half, cy - half, cx + half, cy + half],
                fill=fg
            )
        elif shape_type == 'rectangle':
            draw.rectangle(
                [cx - half, cy - half, cx + half, cy + half],
                fill=fg
            )
        elif shape_type == 'triangle':
            points = [
                (cx, cy - half),
                (cx - half, cy + half),
                (cx + half, cy + half)
            ]
            draw.polygon(points, fill=fg)
        elif shape_type == 'line':
            draw.line(
                [(cx - half, cy), (cx + half, cy)],
                fill=fg,
                width=max(2, shape_size // 10)
            )
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
        
        # Apply rotation if needed
        if rotation != 0:
            img = img.rotate(rotation, expand=False, resample=Image.BICUBIC)
        
        return img
    
    def generate_text(
        self,
        text: str,
        font_size: int = 20,
        position: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """
        Generate image with custom text.
        
        Args:
            text: Text string to render
            font_size: Font size in pixels
            position: (x, y) position or None for center
        
        Returns:
            PIL Image with text
        """
        img = Image.new('RGB', self.size, self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", font_size)
            except (IOError, OSError):
                font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if position is None:
            x = (self.size[0] - text_width) // 2
            y = (self.size[1] - text_height) // 2
        else:
            x, y = position
        
        fg = self._parse_color(self.fg_color, default=(0, 0, 0)) if self.fg_color else (0, 0, 0)
        draw.text((x, y), text, fill=fg, font=font)
        
        return img
    
    def generate_random_digit(self) -> Tuple[Image.Image, int]:
        """Generate image with random digit. Returns (image, digit)."""
        digit = random.randint(0, 9)
        return self.generate_digit(digit), digit
    
    def generate_random_shape(self) -> Tuple[Image.Image, str]:
        """Generate image with random shape. Returns (image, shape_type)."""
        shapes = ['circle', 'rectangle', 'triangle', 'line']
        shape_type = random.choice(shapes)
        return self.generate_shape(shape_type), shape_type
