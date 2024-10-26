import logging
import openai
import tweepy
from telethon import TelegramClient

class SocialMediaManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.social_media')
        self.context = None
        self.twitter_api = None
        self.telegram_client = None
        
    def initialize(self, context):
        self.context = context
        self._setup_apis()
        
    def _setup_apis(self):
        credentials = self.context.get_credentials()
        
        # Setup Twitter
        try:
            auth = tweepy.OAuthHandler(
                credentials['twitter']['consumer_key'],
                credentials['twitter']['consumer_secret']
            )
            auth.set_access_token(
                credentials['twitter']['access_token'],
                credentials['twitter']['access_secret']
            )
            self.twitter_api = tweepy.API(auth)
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API: {e}")
            
        # Setup Telegram
        try:
            self.telegram_client = TelegramClient(
                'bot_session',
                credentials['telegram']['api_id'],
                credentials['telegram']['api_hash']
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram client: {e}")
            
    async def generate_content(self, data, sentiment):
        try:
            prompt = self._create_content_prompt(data, sentiment)
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Failed to generate content: {e}")
            return None
            
    def post_update(self, content, platforms=None):
        if platforms is None:
            platforms = ['twitter', 'telegram']
            
        results = {}
        
        if 'twitter' in platforms and self.twitter_api:
            try:
                tweet = self.twitter_api.update_status(content[:280])
                results['twitter'] = {'success': True, 'id': tweet.id}
            except Exception as e:
                self.logger.error(f"Failed to post to Twitter: {e}")
                results['twitter'] = {'success': False, 'error': str(e)}
                
        if 'telegram' in platforms and self.telegram_client:
            try:
                message = await self.telegram_client.send_message(
                    'channel_username',
                    content
                )
                results['telegram'] = {'success': True, 'id': message.id}
            except Exception as e:
                self.logger.error(f"Failed to post to Telegram: {e}")
                results['telegram'] = {'success': False, 'error': str(e)}
                
        return results
        
    def _create_content_prompt(self, data, sentiment):
        return f"""
        Create a professional crypto trading update based on the following data:
        Market Data: {data}
        Sentiment: {sentiment}
        
        Guidelines:
        - Be concise and informative
        - Include key metrics
        - Maintain professional tone
        - No financial advice
        - Include relevant cashtags
        """