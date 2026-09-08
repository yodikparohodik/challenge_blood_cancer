"""
SelfLearn - Teacher component for generating tasks
"""
import random
from typing import Dict, List, Any, Optional, Tuple

from PIL import Image

from common import DEGRADATION_TYPES, normalize_probabilities, clamp
from synthesize import Synthesizer
from degrade import DegradeAPI
from student import Task


class Teacher:
    """Teacher component that generates learning tasks with degradations."""
    
    def __init__(
        self,
        degradation_probs: Optional[Dict[str, float]] = None,
        adaptation_rate: float = 0.1,
        max_probability: float = 0.4,
        min_probability: float = 0.05,
        image_size: Tuple[int, int] = (64, 64),
        num_classes: int = 10
    ):
        """
        Initialize Teacher.
        
        Args:
            degradation_probs: Initial probabilities for each degradation type
            adaptation_rate: Rate of probability adjustment
            max_probability: Maximum probability for any degradation
            min_probability: Minimum probability for any degradation
            image_size: Size of generated images
            num_classes: Number of classes (digits 0-9)
        """
        self.adaptation_rate = adaptation_rate
        self.max_probability = max_probability
        self.min_probability = min_probability
        self.num_classes = num_classes
        
        # Initialize degradation probabilities
        if degradation_probs is None:
            # Equal distribution
            prob = 1.0 / len(DEGRADATION_TYPES)
            self.degradation_probs = {d: prob for d in DEGRADATION_TYPES}
        else:
            self.degradation_probs = degradation_probs.copy()
        
        # Normalize to ensure sum = 1
        self.degradation_probs = normalize_probabilities(self.degradation_probs)
        
        # Initialize synthesizer
        self.synthesizer = Synthesizer(size=image_size)
    
    def _select_degradation(self) -> str:
        """Select degradation type based on current probabilities."""
        degradations = list(self.degradation_probs.keys())
        probs = [self.degradation_probs[d] for d in degradations]
        return random.choices(degradations, weights=probs, k=1)[0]
    
    def _select_severity(self, degradation_type: str) -> float:
        """Select severity level for degradation."""
        # Base severity with some randomness
        base_severity = random.uniform(0.2, 0.8)
        return base_severity
    
    def generate_task(self) -> Task:
        """
        Generate a single learning task.
        
        Returns:
            Task object with image, label, and metadata
        """
        # Generate base image with random digit
        digit = random.randint(0, self.num_classes - 1)
        base_image = self.synthesizer.generate_digit(digit)
        
        # Select degradation
        degradation_type = self._select_degradation()
        severity = self._select_severity(degradation_type)
        
        # Apply degradation
        degraded_image = DegradeAPI.apply(base_image, degradation_type, severity)
        
        # Create metadata
        metadata = {
            'degradation_type': degradation_type,
            'severity': severity,
            'original_digit': digit,
            'base_image_mode': base_image.mode
        }
        
        return Task(
            image=degraded_image,
            label=digit,
            metadata=metadata
        )
    
    def generate_tasks(self, num_tasks: int) -> List[Task]:
        """
        Generate multiple learning tasks.
        
        Args:
            num_tasks: Number of tasks to generate
        
        Returns:
            List of Task objects
        """
        return [self.generate_task() for _ in range(num_tasks)]
    
    def adapt_strategy(self, error_analysis: Dict[str, float]) -> None:
        """
        Adapt degradation probabilities based on error analysis.
        
        Args:
            error_analysis: Dictionary mapping degradation_type to error_rate
        """
        for degradation_type, error_rate in error_analysis.items():
            if degradation_type not in self.degradation_probs:
                continue
            
            current_prob = self.degradation_probs[degradation_type]
            
            # Increase probability for high error rates, decrease for low
            if error_rate > 0.3:  # High error rate - focus more
                adjustment = 1 + self.adaptation_rate
            elif error_rate < 0.1:  # Low error rate - focus less
                adjustment = 1 - self.adaptation_rate
            else:
                adjustment = 1.0
            
            new_prob = current_prob * adjustment
            new_prob = clamp(new_prob, self.min_probability, self.max_probability)
            
            self.degradation_probs[degradation_type] = new_prob
        
        # Re-normalize probabilities
        self.degradation_probs = normalize_probabilities(self.degradation_probs)
    
    def get_current_strategy(self) -> Dict[str, Any]:
        """Get current degradation strategy."""
        return {
            'degradation_probs': self.degradation_probs.copy(),
            'adaptation_rate': self.adaptation_rate,
            'num_classes': self.num_classes
        }
    
    def set_strategy(self, strategy: Dict[str, Any]) -> None:
        """Set degradation strategy from external source."""
        if 'degradation_probs' in strategy:
            self.degradation_probs = normalize_probabilities(strategy['degradation_probs'])
        if 'adaptation_rate' in strategy:
            self.adaptation_rate = strategy['adaptation_rate']
        if 'num_classes' in strategy:
            self.num_classes = strategy['num_classes']
