import logging
from typing import Dict, Any
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

class TelegramManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.social.telegram')
        self.client = None

    async def initialize(self, credentials: Dict[str, str]) -> None:
        try:
            self.client = TelegramClient(
                'bot_session',
                credentials['api_id'],
                credentials['api_hash']
            )
            await self.client.start(bot_token=credentials['bot_token'])
            self.logger.info("Telegram client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram client: {e}")
            raise

    async def post_update(self, content: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.client:
                raise RuntimeError("Telegram client not initialized")

            if content.get('type') == 'image':
                message = await self.client.send_file(
                    content['channel'],
                    content['image_path'],
                    caption=content['text']
                )
            else:
                message = await self.client.send_message(
                    content['channel'],
                    content['text']
                )

            return {
                'success': True,
                'message_id': message.id
            }

        except Exception as e:
            self.logger.error(f"Failed to post Telegram message: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_sentiment(self) -> Dict[str, Any]:
        try:
            if not self.client:
                raise RuntimeError("Telegram client not initialized")

            messages = await self.client(GetHistoryRequest(
                peer=self.channel,
                limit=100,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            return {
                'timestamp': datetime.now().isoformat(),
                'messages': [
                    {
                        'id': message.id,
                        'text': message.message,
                        'date': message.date.isoformat(),
                        'views': message.views,
                        'forwards': message.forwards
                    }
                    for message in messages.messages
                    if message.message
                ]
            }

        except Exception as e:
            self.logger.error(f"Failed to get Telegram sentiment: {e}")
            return {'error': str(e)}

    async def get_engagement(self) -> Dict[str, Any]:
        try:
            if not self.client:
                raise RuntimeError("Telegram client not initialized")

            messages = await self.client(GetHistoryRequest(
                peer=self.channel,
                limit=100,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            total_views = sum(message.views or 0 for message in messages.messages)
            total_forwards = sum(message.forwards or 0 for message in messages.messages)

            return {
                'timestamp': datetime.now().isoformat(),
                'total_views': total_views,
                'total_forwards': total_forwards,
                'average_views': total_views / len(messages.messages) if messages.messages else 0
            }

        except Exception as e:
            self.logger.error(f"Failed to get Telegram engagement: {e}")
            return {'error': str(e)}