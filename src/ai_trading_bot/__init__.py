from .core import Session, Task, Scheduler
from .data import DataAggregator, ContextManager
from .analysis import SentimentAnalyzer, DecisionEngine
from .portfolio import PortfolioManager, RiskAnalyzer, PositionManager, PerformanceAnalyzer
from .social import SocialMediaManager, ContentGenerator, PlatformManager
from .support import ErrorHandler, LogCache, SecurityManager

__version__ = "1.0.0"

__all__ = [
    # Core
    'Session',
    'Task',
    'Scheduler',
    
    # Data
    'DataAggregator',
    'ContextManager',
    
    # Analysis
    'SentimentAnalyzer',
    'DecisionEngine',
    
    # Portfolio
    'PortfolioManager',
    'RiskAnalyzer',
    'PositionManager',
    'PerformanceAnalyzer',
    
    # Social
    'SocialMediaManager',
    'ContentGenerator',
    'PlatformManager',
    
    # Support
    'ErrorHandler',
    'LogCache',
    'SecurityManager'
]