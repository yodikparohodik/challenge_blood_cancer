#!/usr/bin/env python3
"""
SelfLearn - Main entry point for CLI
"""
import os
import sys
import argparse
import yaml

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import setup_logging, DEFAULT_CONFIG, set_seed
from referee import Referee


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return DEFAULT_CONFIG


def main():
    parser = argparse.ArgumentParser(
        description='SelfLearn - Autonomous Self-Learning System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run test (minimal)
  python run.py --action test
  
  # Run full training
  python run.py --action run --competitions 5 --rounds 10 --tasks 50
  
  # Start API server
  python run.py --action api --port 8000
  
  # With custom config
  python run.py --action run --config config/custom.yaml
        """
    )
    
    parser.add_argument(
        '--action',
        type=str,
        choices=['test', 'run', 'api'],
        default='test',
        help='Action to perform (default: test)'
    )
    
    parser.add_argument(
        '--competitions',
        type=int,
        default=3,
        help='Number of competitions (default: 3)'
    )
    
    parser.add_argument(
        '--rounds',
        type=int,
        default=5,
        help='Rounds per competition (default: 5)'
    )
    
    parser.add_argument(
        '--tasks',
        type=int,
        default=20,
        help='Tasks per round (default: 20)'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Training epochs (default: from config)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Batch size (default: from config)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to YAML config file'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        help='Log file path (optional)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Data directory (default: data)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level, args.log_file)
    logger.info(f'SelfLearn starting with action: {args.action}')
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.epochs:
        config.setdefault('training', {})['epochs'] = args.epochs
    if args.batch_size:
        config.setdefault('training', {})['batch_size'] = args.batch_size
    
    # Set random seed
    seed = config.get('system', {}).get('seed', 42)
    set_seed(seed)
    logger.info(f'Random seed set to {seed}')
    
    # Initialize referee
    referee = Referee(
        data_dir=args.data_dir,
        config=config,
        logger=logger
    )
    
    try:
        if args.action == 'test':
            logger.info('Running test mode (1 competition, 1 round, 5 tasks)')
            result = referee.run_competition(
                competitions=1,
                rounds_per_competition=1,
                tasks_per_round=5,
                epochs=2,
                batch_size=16
            )
            logger.info('Test completed successfully!')
            logger.info(f'Final accuracy: {result["competitions"][0]["rounds"][0]["metrics"]["accuracy"]:.3f}')
        
        elif args.action == 'run':
            logger.info(
                f'Starting training: {args.competitions} competitions, '
                f'{args.rounds} rounds, {args.tasks} tasks'
            )
            result = referee.run_competition(
                competitions=args.competitions,
                rounds_per_competition=args.rounds,
                tasks_per_round=args.tasks,
                epochs=config.get('training', {}).get('epochs', 10),
                batch_size=config.get('training', {}).get('batch_size', 32)
            )
            logger.info('Training completed!')
            
            # Print summary
            total_rounds = sum(len(c['rounds']) for c in result['competitions'])
            avg_accuracy = sum(
                r['metrics']['accuracy']
                for c in result['competitions']
                for r in c['rounds']
            ) / max(total_rounds, 1)
            
            logger.info(f'Total rounds completed: {total_rounds}')
            logger.info(f'Average accuracy: {avg_accuracy:.3f}')
            logger.info(f'Model saved to: {result["model_path"]}')
        
        elif args.action == 'api':
            logger.info(f'Starting API server on port {args.port}')
            
            # Import and run API
            from api import app
            import uvicorn
            
            uvicorn.run(
                app,
                host='0.0.0.0',
                port=args.port,
                log_level=args.log_level.lower()
            )
    
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
        referee.stop()
    
    except Exception as e:
        logger.error(f'Error: {e}', exc_info=True)
        sys.exit(1)
    
    logger.info('SelfLearn finished')


if __name__ == '__main__':
    main()
