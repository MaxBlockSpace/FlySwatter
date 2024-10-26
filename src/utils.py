import logging
import os
from datetime import datetime

def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/error.log', mode='a', level=logging.ERROR),
            logging.FileHandler(f'logs/combined.log', mode='a'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)