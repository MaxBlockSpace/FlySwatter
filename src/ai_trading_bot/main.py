import asyncio
import logging
from datetime import datetime
from typing import Optional

from .core import SessionManager, TaskExecutor
from .data import DataAggregator, DataValidator
from .analysis import (
    MarketAnalyzer,
    PatternRecognizer,
    SentimentAnalyzer,
    DecisionEngine
)
from .portfolio import PortfolioManager
from .social import SocialMediaManager
from .support import ErrorHandler, LogCache, SecurityManager
from .context import ContextManager

class TradingBot:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot')
        self.context = ContextManager()
        self.error_handler = ErrorHandler()
        self.log_cache = LogCache()
        self.security = SecurityManager()
        
        # Initialize core components
        self.session_manager = SessionManager(self.context)
        self.task_executor = TaskExecutor(self.context)
        
        # Initialize data components
        self.data_aggregator = DataAggregator(self.context)
        self.data_validator = DataValidator()
        
        # Initialize analysis components
        self.market_analyzer = MarketAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.decision_engine = DecisionEngine()
        
        # Initialize execution components
        self.portfolio_manager = PortfolioManager(self.context)
        self.social_media_manager = SocialMediaManager(self.context)

    async def start(self) -> None:
        try:
            self.logger.info("Starting AI Trading Bot")
            await self.data_aggregator.start()
            await self._run_trading_loop()
        except Exception as e:
            self.error_handler.handle_error(e, {'component': 'main', 'action': 'start'})
            raise

    async def stop(self) -> None:
        try:
            self.logger.info("Stopping AI Trading Bot")
            await self.data_aggregator.stop()
        except Exception as e:
            self.error_handler.handle_error(e, {'component': 'main', 'action': 'stop'})
            raise

    async def _run_trading_loop(self) -> None:
        while True:
            try:
                session_id = await self.session_manager.start_session('trading')
                if not session_id:
                    continue

                # Collect and validate data
                data = await self.data_aggregator.collect_data()
                validation = self.data_validator.validate_data(data)
                
                if not validation['is_valid']:
                    self.logger.warning(f"Data validation failed: {validation['issues']}")
                    continue

                # Analyze market
                market_analysis = await self.market_analyzer.analyze_market(data['market'])
                patterns = await self.pattern_recognizer.identify_patterns(data['market'])
                sentiment = await self.sentiment_analyzer.analyze_sentiment(data)

                # Make decisions
                decisions = await self.decision_engine.make_decisions(
                    market_data=data['market'],
                    sentiment_data=sentiment
                )

                # Execute decisions
                if decisions:
                    await self.portfolio_manager.execute_recommendations(decisions)

                # Update social media
                await self.social_media_manager.create_and_post_update(
                    {
                        'market_data': market_analysis,
                        'patterns': patterns,
                        'sentiment': sentiment,
                        'decisions': decisions
                    },
                    ['twitter', 'telegram']
                )

                await self.session_manager.end_session(session_id)
                await asyncio.sleep(300)  # 5 minutes between sessions

            except Exception as e:
                self.error_handler.handle_error(e, {'component': 'main', 'action': 'trading_loop'})
                await asyncio.sleep(60)  # Wait before retrying

async def main() -> None:
    bot = TradingBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())