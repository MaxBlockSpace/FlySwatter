import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .content_generator import ContentGenerator
from .platform_manager import PlatformManager

class SocialMediaManager:
    def __init__(self, context_manager):
        self.logger = logging.getLogger('ai_trading_bot.social_media')
        self.content_generator = ContentGenerator()
        self.platform_manager = PlatformManager(context_manager)
        self.context = context_manager

    async def create_and_post_update(self, data: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        try:
            content_type = self._determine_content_type(data)
            context = self._prepare_context(data)
            
            content = await self.content_generator.generate_content(context, content_type)
            if not content:
                return {'success': False, 'error': 'Content generation failed'}

            results = {}
            for platform in platforms:
                result = await self.platform_manager.post_content(content, platform)
                results[platform] = result

            self._log_activity(content, results)
            return {'success': True, 'results': results}

        except Exception as e:
            self.logger.error(f"Update creation/posting failed: {e}")
            return {'success': False, 'error': str(e)}

    def _determine_content_type(self, data: Dict[str, Any]) -> str:
        if data.get('requires_visualization'):
            return 'image'
        elif data.get('sentiment', 0) > 0.8:
            return 'meme'
        return 'text'

    def _prepare_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'timestamp': datetime.now().isoformat(),
            'sentiment': data.get('sentiment'),
            'data': data.get('market_data'),
            'topic': data.get('topic', 'crypto trading')
        }

    def _log_activity(self, content: Dict[str, Any], results: Dict[str, Any]) -> None:
        activity = {
            'timestamp': datetime.now().isoformat(),
            'content_type': content['type'],
            'platforms': results
        }
        
        try:
            self.context.save_session_data(
                {'session_id': 'social_media', 'tasks': [activity]},
                True
            )
        except Exception as e:
            self.logger.error(f"Failed to log activity: {e}")

    async def analyze_engagement(self) -> Dict[str, Any]:
        engagement_metrics = {}
        
        for platform in ['twitter', 'telegram']:
            posts = self.platform_manager.get_recent_posts(platform)
            if posts:
                engagement_metrics[platform] = self._calculate_engagement_metrics(posts)

        return engagement_metrics

    def _calculate_engagement_metrics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_engagement = sum(
            post['engagement']['likes'] + post['engagement']['retweets']
            for post in posts
        )
        
        return {
            'total_engagement': total_engagement,
            'average_engagement': total_engagement / len(posts) if posts else 0,
            'post_count': len(posts)
        }