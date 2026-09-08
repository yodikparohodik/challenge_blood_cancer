"""
SelfLearn - Referee component for orchestrating the learning process
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from common import (
    calculate_metrics, get_timestamp, ensure_dir, 
    DEGRADATION_TYPES, setup_logging
)
from teacher import Teacher
from student import Task, SimpleCNN, get_model


class Referee:
    """Referee component that orchestrates the learning competition."""
    
    def __init__(
        self,
        data_dir: str = 'data',
        config: Optional[Dict[str, Any]] = None,
        logger=None
    ):
        """
        Initialize Referee.
        
        Args:
            data_dir: Directory for storing data and results
            config: Configuration dictionary
            logger: Logger instance
        """
        self.data_dir = data_dir
        self.config = config or {}
        self.logger = logger
        
        # Paths
        self.state_path = os.path.join(data_dir, 'state.json')
        self.results_path = os.path.join(data_dir, 'results.json')
        self.models_dir = os.path.join(data_dir, 'models')
        self.generated_dir = os.path.join(data_dir, 'generated')
        
        # Ensure directories exist
        ensure_dir(data_dir)
        ensure_dir(self.models_dir)
        ensure_dir(self.generated_dir)
        
        # State
        self.current_competition = 0
        self.current_round = 0
        self.total_competitions = 0
        self.is_running = False
        self.stop_requested = False
        
        # Components
        self.teacher = None
        self.student = None
        
        # Results storage
        self.results = {
            'competitions': []
        }
        
        # Load existing state if available
        self._load_state()
    
    def _log(self, level: str, message: str):
        """Log message if logger is available."""
        if self.logger:
            getattr(self.logger, level.lower())(message)
        else:
            print(f"[{level}] {message}")
    
    def _initialize_components(self):
        """Initialize teacher and student components."""
        teacher_config = self.config.get('teacher', {})
        student_config = self.config.get('student', {})
        training_config = self.config.get('training', {})
        
        # Initialize teacher
        self.teacher = Teacher(
            degradation_probs=teacher_config.get('initial_degradation_probs'),
            adaptation_rate=teacher_config.get('adaptation_rate', 0.1),
            max_probability=teacher_config.get('max_probability', 0.4),
            min_probability=teacher_config.get('min_probability', 0.05),
            num_classes=student_config.get('num_classes', 10)
        )
        
        # Initialize student
        model_type = student_config.get('model_type', 'SimpleCNN')
        num_classes = student_config.get('num_classes', 10)
        self.student = get_model(model_type, num_classes=num_classes)
        
        # Try to load existing model weights
        model_path = os.path.join(self.models_dir, 'best.pth')
        if os.path.exists(model_path):
            try:
                self.student.load(model_path)
                self._log('INFO', f'Loaded existing model from {model_path}')
            except Exception as e:
                self._log('WARNING', f'Failed to load model: {e}')
    
    def _save_state(self):
        """Save current state to disk."""
        state = {
            'current_competition': self.current_competition,
            'current_round': self.current_round,
            'total_competitions': self.total_competitions,
            'degradation_probs': self.teacher.degradation_probs if self.teacher else {},
            'model_weights_path': os.path.join(self.models_dir, 'best.pth'),
            'last_updated': get_timestamp(),
            'is_running': self.is_running
        }
        
        with open(self.state_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self):
        """Load state from disk if available."""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    state = json.load(f)
                
                self.current_competition = state.get('current_competition', 0)
                self.current_round = state.get('current_round', 0)
                self.total_competitions = state.get('total_competitions', 0)
                self.is_running = state.get('is_running', False)
                
                self._log('INFO', f'Loaded state from {self.state_path}')
            except Exception as e:
                self._log('WARNING', f'Failed to load state: {e}')
        
        # Load results
        if os.path.exists(self.results_path):
            try:
                with open(self.results_path, 'r') as f:
                    self.results = json.load(f)
            except Exception as e:
                self._log('WARNING', f'Failed to load results: {e}')
    
    def _save_results(self):
        """Save results to disk."""
        with open(self.results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def _evaluate_round(
        self,
        tasks: List[Task],
        predictions: List[int]
    ) -> Dict[str, Any]:
        """Evaluate round results."""
        labels = [task.label for task in tasks]
        
        # Calculate overall metrics
        metrics = calculate_metrics(predictions, labels)
        
        # Calculate error rate by degradation type
        error_by_degradation = {}
        degradation_tasks = {}
        
        for i, task in enumerate(tasks):
            deg_type = task.metadata.get('degradation_type', 'unknown')
            if deg_type not in degradation_tasks:
                degradation_tasks[deg_type] = {'correct': 0, 'total': 0}
            
            degradation_tasks[deg_type]['total'] += 1
            if predictions[i] == labels[i]:
                degradation_tasks[deg_type]['correct'] += 1
        
        for deg_type, stats in degradation_tasks.items():
            if stats['total'] > 0:
                error_rate = 1.0 - (stats['correct'] / stats['total'])
                error_by_degradation[deg_type] = error_rate
        
        return {
            'metrics': metrics,
            'error_by_degradation': error_by_degradation,
            'tasks_count': len(tasks)
        }
    
    def run_competition(
        self,
        competitions: int = 3,
        rounds_per_competition: int = 5,
        tasks_per_round: int = 20,
        epochs: int = 10,
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        Run full competition cycle.
        
        Args:
            competitions: Number of competitions to run
            rounds_per_competition: Rounds per competition
            tasks_per_round: Tasks per round
            epochs: Training epochs per round
            batch_size: Training batch size
        
        Returns:
            Competition results
        """
        self._log('INFO', f'Starting competition: {competitions} competitions, '
                         f'{rounds_per_competition} rounds, {tasks_per_round} tasks')
        
        self.is_running = True
        self.total_competitions = competitions
        self._initialize_components()
        
        training_config = self.config.get('training', {})
        if epochs is None:
            epochs = training_config.get('epochs', 10)
        if batch_size is None:
            batch_size = training_config.get('batch_size', 32)
        
        all_results = []
        
        try:
            for comp_idx in range(self.current_competition, competitions):
                self.current_competition = comp_idx
                competition_result = {
                    'id': comp_idx + 1,
                    'started_at': get_timestamp(),
                    'rounds': []
                }
                
                self._log('INFO', f'Competition {comp_idx + 1}/{competitions}')
                
                for round_idx in range(rounds_per_competition):
                    if self.stop_requested:
                        self._log('INFO', 'Stop requested, exiting...')
                        break
                    
                    self.current_round = round_idx
                    self._log('INFO', f'  Round {round_idx + 1}/{rounds_per_competition}')
                    
                    # Generate tasks
                    tasks = self.teacher.generate_tasks(tasks_per_round)
                    
                    # Train on tasks
                    history = self.student.train_method(
                        tasks,
                        epochs=epochs,
                        batch_size=batch_size
                    )
                    
                    # Evaluate on same tasks (for simplicity)
                    images = [task.image for task in tasks]
                    predictions = self.student.predict(images)
                    
                    # Evaluate results
                    eval_result = self._evaluate_round(tasks, predictions)
                    
                    round_result = {
                        'round_number': round_idx + 1,
                        'tasks_count': tasks_per_round,
                        'metrics': eval_result['metrics'],
                        'error_by_degradation': eval_result['error_by_degradation'],
                        'training_history': {
                            'final_loss': history['loss'][-1] if history['loss'] else 0,
                            'final_accuracy': history['accuracy'][-1] if history['accuracy'] else 0
                        }
                    }
                    
                    competition_result['rounds'].append(round_result)
                    
                    # Adapt teacher strategy
                    self.teacher.adapt_strategy(eval_result['error_by_degradation'])
                    
                    self._log('INFO', f'    Accuracy: {eval_result["metrics"]["accuracy"]:.3f}')
                    
                    # Save state after each round
                    self._save_state()
                    self._save_results()
                
                competition_result['completed_at'] = get_timestamp()
                self.results['competitions'].append(competition_result)
                all_results.append(competition_result)
                
                # Save model after each competition
                model_path = os.path.join(self.models_dir, 'best.pth')
                self.student.save(model_path)
                
                if self.stop_requested:
                    break
            
            self._log('INFO', 'Competition completed!')
            
        except Exception as e:
            self._log('ERROR', f'Competition failed: {e}')
            raise
        
        finally:
            self.is_running = False
            self._save_state()
            self._save_results()
        
        return {
            'competitions': all_results,
            'final_degradation_probs': self.teacher.degradation_probs,
            'model_path': os.path.join(self.models_dir, 'best.pth')
        }
    
    def stop(self):
        """Request stop of current competition."""
        self.stop_requested = True
        self._log('INFO', 'Stop requested')
    
    def reset(self):
        """Reset all state and results."""
        self.current_competition = 0
        self.current_round = 0
        self.total_competitions = 0
        self.is_running = False
        self.stop_requested = False
        self.results = {'competitions': []}
        self.teacher = None
        self.student = None
        
        # Clear files
        if os.path.exists(self.state_path):
            os.remove(self.state_path)
        if os.path.exists(self.results_path):
            os.remove(self.results_path)
        
        self._log('INFO', 'State reset complete')
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            'current_competition': self.current_competition,
            'current_round': self.current_round,
            'total_competitions': self.total_competitions,
            'is_running': self.is_running,
            'stop_requested': self.stop_requested,
            'degradation_probs': self.teacher.degradation_probs if self.teacher else {}
        }
    
    def get_results(self) -> Dict[str, Any]:
        """Get all results."""
        return self.results
    
    def get_models_info(self) -> List[Dict[str, Any]]:
        """Get information about available models."""
        models = []
        if os.path.exists(self.models_dir):
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.pth'):
                    filepath = os.path.join(self.models_dir, filename)
                    models.append({
                        'name': filename,
                        'path': filepath,
                        'size_bytes': os.path.getsize(filepath)
                    })
        return models
