import asyncio
import logging
from ai_trading_bot.core import SessionManager, TaskExecutor, Scheduler
from ai_trading_bot.data import DataAggregator, DataValidator
from ai_trading_bot.analysis import (
    SentimentAnalyzer,
    MarketAnalyzer,
    DecisionEngine,
    ManipulationDetector
)
from ai_trading_bot.portfolio import PortfolioManager
from ai_trading_bot.social import SocialMediaManager
from ai_trading_bot.learning import AdaptiveLearner
from ai_trading_bot.monitoring import MetricsCollector, AlertManager
from ai_trading_bot.config import ConfigManager

class TradingBot:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot')
        self.config = ConfigManager()
        
        # Initialize core components
        self.session_manager = SessionManager()
        self.task_executor = TaskExecutor()
        self.scheduler = Scheduler()
        
        # Initialize data components
        self.data_aggregator = DataAggregator()
        self.data_validator = DataValidator()
        
        # Initialize analysis components
        self.market_analyzer = MarketAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.decision_engine = DecisionEngine(AdaptiveLearner())
        self.manipulation_detector = ManipulationDetector()
        
        # Initialize portfolio management
        self.portfolio_manager = PortfolioManager()
        
        # Initialize social media
        self.social_media_manager = SocialMediaManager()
        
        # Initialize monitoring
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()

    async def start(self):
        try:
            self.logger.info("Starting AI Trading Bot")
            
            # Start data collection
            await self.data_aggregator.start()
            
            # Start scheduler
            await self.scheduler.start()
            
            # Start monitoring
            await self.metrics_collector.start()
            
            # Main trading loop
            while True:
                try:
                    await self._trading_cycle()
                except Exception as e:
                    self.logger.error(f"Trading cycle error: {e}")
                await asyncio.sleep(60)  # 1-minute cycle
                
        except Exception as e:
            self.logger.error(f"Bot startup failed: {e}")
            raise

    async def stop(self):
        try:
            self.logger.info("Stopping AI Trading Bot")
            await self.data_aggregator.stop()
            await self.scheduler.stop()
            await self.metrics_collector.stop()
        except Exception as e:
            self.logger.error(f"Bot shutdown error: {e}")
            raise

    async def _trading_cycle(self):
        # Collect and validate data
        data = await self.data_aggregator.collect_data()
        validation = self.data_validator.validate_data(data)
        
        if not validation['is_valid']:
            self.logger.warning(f"Data validation failed: {validation['issues']}")
            return

        # Analyze market and detect manipulation
        market_analysis = await self.market_analyzer.analyze_market(data)
        manipulation_data = await self.manipulation_detector.detect_manipulation(data)
        sentiment_data = await self.sentiment_analyzer.analyze_sentiment(data)

        # Make trading decisions
        decisions = await self.decision_engine.make_decisions(
            market_analysis,
            sentiment_data,
            manipulation_data
        )

        # Execute decisions
        if decisions:
            await self.portfolio_manager.execute_recommendations(decisions)

        # Update social media
        await self.social_media_manager.post_update({
            'market_data': market_analysis,
            'sentiment': sentiment_data,
            'decisions': decisions
        })

        # Collect metrics and check alerts
        metrics = await self.metrics_collector.collect_metrics()
        await self.alert_manager.check_alerts(metrics)

async def main():
    bot = TradingBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())