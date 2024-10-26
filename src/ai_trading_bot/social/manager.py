import logging
from typing import Dict, Any, List
from datetime import datetime
from .twitter import TwitterManager
from .telegram import TelegramManager
from .content import ContentGenerator

class SocialMediaManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.social.manager')
        self.twitter = TwitterManager()
        self.telegram = TelegramManager()
        self.content_generator = ContentGenerator()

    async def post_update(
        self,
        data: Dict[str, Any],
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        try:
            if platforms is None:
                platforms = ['twitter', 'telegram']

            content = await self.content_generator.generate_content(data)
            results = {}

            for platform in platforms:
                if platform == 'twitter':
                    results['twitter'] = await self.twitter.post_update(content)
                elif platform == 'telegram':
                    results['telegram'] = await self.telegram.post_update(content)

            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }

        except Exception as e:
            self.logger.error(f"Failed to post update: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def analyze_sentiment(
        self,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        try:
            if platforms is None:
                platforms = ['twitter', 'telegram']

            results = {}
            
            if 'twitter' in platforms:
                results['twitter'] = await self.twitter.get_sentiment()
            if 'telegram' in platforms:
                results['telegram'] = await self.telegram.get_sentiment()

            return {
                'timestamp': datetime.now().isoformat(),
                'sentiment': results
            }

        except Exception as e:
            self.logger.error(f"Failed to analyze sentiment: {e}")
            return {'error': str(e)}

    async def get_engagement_metrics(
        self,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        try:
            if platforms is None:
                platforms = ['twitter', 'telegram']

            metrics = {}
            
            if 'twitter' in platforms:
                metrics['twitter'] = await self.twitter.get_engagement()
            if 'telegram' in platforms:
                metrics['telegram'] = await self.telegram.get_engagement()

            return {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }

        except Exception as e:
            self.logger.error(f"Failed to get engagement metrics: {e}")
            return {'error': str(e)}