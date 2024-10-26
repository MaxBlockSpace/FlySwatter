import logging
import tweepy
from telethon import TelegramClient
from typing import Dict, Any, List, Optional

class PlatformManager:
    def __init__(self, context_manager):
        self.logger = logging.getLogger('ai_trading_bot.social_media.platform')
        self.context = context_manager
        self.platforms = {}
        self._initialize_platforms()

    def _initialize_platforms(self):
        self._setup_twitter()
        self._setup_telegram()

    def _setup_twitter(self):
        try:
            creds = self.context.retrieve_credentials('twitter')
            if creds:
                auth = tweepy.OAuthHandler(
                    creds['consumer_key'],
                    creds['consumer_secret']
                )
                auth.set_access_token(
                    creds['access_token'],
                    creds['access_token_secret']
                )
                self.platforms['twitter'] = tweepy.API(auth)
                self.logger.info("Twitter API initialized")
        except Exception as e:
            self.logger.error(f"Twitter setup failed: {e}")

    def _setup_telegram(self):
        try:
            creds = self.context.retrieve_credentials('telegram')
            if creds:
                client = TelegramClient(
                    'bot_session',
                    creds['api_id'],
                    creds['api_hash']
                )
                self.platforms['telegram'] = client
                self.logger.info("Telegram client initialized")
        except Exception as e:
            self.logger.error(f"Telegram setup failed: {e}")

    async def post_content(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        if platform not in self.platforms:
            return {'success': False, 'error': 'Platform not configured'}

        try:
            if platform == 'twitter':
                return await self._post_to_twitter(content)
            elif platform == 'telegram':
                return await self._post_to_telegram(content)
            else:
                return {'success': False, 'error': 'Unsupported platform'}
        except Exception as e:
            self.logger.error(f"Failed to post to {platform}: {e}")
            return {'success': False, 'error': str(e)}

    async def _post_to_twitter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        api = self.platforms['twitter']
        
        if content['type'] in ['image', 'meme']:
            media = api.media_upload(content['content'])
            status = api.update_status(
                status=content.get('text', ''),
                media_ids=[media.media_id]
            )
        else:
            status = api.update_status(content['content'])

        return {
            'success': True,
            'platform': 'twitter',
            'post_id': status.id,
            'url': f"https://twitter.com/i/web/status/{status.id}"
        }

    async def _post_to_telegram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        client = self.platforms['telegram']
        
        if content['type'] in ['image', 'meme']:
            message = await client.send_file(
                'channel_username',
                content['content'],
                caption=content.get('text', '')
            )
        else:
            message = await client.send_message(
                'channel_username',
                content['content']
            )

        return {
            'success': True,
            'platform': 'telegram',
            'post_id': message.id
        }

    def get_recent_posts(self, platform: str, count: int = 10) -> List[Dict[str, Any]]:
        if platform not in self.platforms:
            return []

        try:
            if platform == 'twitter':
                return self._get_twitter_posts(count)
            elif platform == 'telegram':
                return self._get_telegram_posts(count)
            return []
        except Exception as e:
            self.logger.error(f"Failed to get posts from {platform}: {e}")
            return []

    def _get_twitter_posts(self, count: int) -> List[Dict[str, Any]]:
        api = self.platforms['twitter']
        tweets = api.user_timeline(count=count)
        return [
            {
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'engagement': {
                    'likes': tweet.favorite_count,
                    'retweets': tweet.retweet_count
                }
            }
            for tweet in tweets
        ]

    def _get_telegram_posts(self, count: int) -> List[Dict[str, Any]]:
        # Implement Telegram post retrieval
        return []