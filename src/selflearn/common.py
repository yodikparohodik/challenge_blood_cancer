"""
SelfLearn - Common utilities and metrics
"""
import os
import random
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


# Constants
DEGRADATION_TYPES = [
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

DEFAULT_CONFIG = {
    'system': {
        'seed': 42,
        'log_level': 'INFO',
        'data_dir': 'data',
        'save_every_round': True
    },
    'training': {
        'batch_size': 32,
        'learning_rate': 0.001,
        'epochs': 10,
        'optimizer': 'adam',
        'patience': 5
    },
    'teacher': {
        'adaptation_rate': 0.1,
        'max_probability': 0.4,
        'min_probability': 0.05
    },
    'student': {
        'model_type': 'SimpleCNN',
        'num_classes': 10,
        'input_size': [64, 64, 3]
    }
}


def set_seed(seed: int) -> None:
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def setup_logging(level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger('selflearn')
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def ensure_dir(path: str) -> None:
    """Ensure directory exists."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def calculate_metrics(predictions: List[int], labels: List[int]) -> Dict[str, Any]:
    """
    Calculate classification metrics.
    
    Args:
        predictions: List of predicted labels
        labels: List of true labels
    
    Returns:
        Dictionary with metrics: accuracy, precision, recall, f1_score, confusion_matrix
    """
    if len(predictions) == 0 or len(labels) == 0:
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'confusion_matrix': []
        }
    
    # Handle multi-class
    average = 'macro' if len(set(labels)) > 2 else 'binary'
    
    acc = accuracy_score(labels, predictions)
    prec = precision_score(labels, predictions, average=average, zero_division=0)
    rec = recall_score(labels, predictions, average=average, zero_division=0)
    f1 = f1_score(labels, predictions, average=average, zero_division=0)
    cm = confusion_matrix(labels, predictions).tolist()
    
    return {
        'accuracy': float(acc),
        'precision': float(prec),
        'recall': float(rec),
        'f1_score': float(f1),
        'confusion_matrix': cm
    }


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def normalize_probabilities(probs: Dict[str, float]) -> Dict[str, float]:
    """Normalize probabilities to sum to 1.0."""
    total = sum(probs.values())
    if total == 0:
        # Equal distribution if all zeros
        n = len(probs)
        return {k: 1.0 / n for k in probs}
    return {k: v / total for k, v in probs.items()}


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))
