"""
SelfLearn - Autonomous Self-Learning System

A fully autonomous self-learning system that generates its own training data,
trains models, and adapts task difficulty based on results.
"""

from .common import (
    DEGRADATION_TYPES,
    DEFAULT_CONFIG,
    calculate_metrics,
    set_seed,
    setup_logging,
    ensure_dir,
    get_timestamp,
    normalize_probabilities,
    clamp
)

from .degrade import DegradeAPI
from .synthesize import Synthesizer
from .teacher import Teacher
from .student import Task, SimpleCNN, MiniCNN, get_model
from .referee import Referee

__version__ = '1.0.0'
__all__ = [
    'DEGRADATION_TYPES',
    'DEFAULT_CONFIG',
    'calculate_metrics',
    'set_seed',
    'setup_logging',
    'ensure_dir',
    'get_timestamp',
    'normalize_probabilities',
    'clamp',
    'DegradeAPI',
    'Synthesizer',
    'Teacher',
    'Task',
    'SimpleCNN',
    'MiniCNN',
    'get_model',
    'Referee'
]
