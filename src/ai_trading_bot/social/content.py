import logging
from typing import Dict, Any
from datetime import datetime
import openai

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.social.content')

    async def generate_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            content_type = self._determine_content_type(data)
            context = self._prepare_context(data)

            if content_type == 'text':
                content = await self._generate_text(context)
            elif content_type == 'image':
                content = await self._generate_image(context)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            return {
                'type': content_type,
                'timestamp': datetime.now().isoformat(),
                **content
            }

        except Exception as e:
            self.logger.error(f"Failed to generate content: {e}")
            raise

    def _determine_content_type(self, data: Dict[str, Any]) -> str:
        if data.get('requires_visualization'):
            return 'image'
        return 'text'

    def _prepare_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'market_data': data.get('market_data', {}),
            'sentiment': data.get('sentiment', {}),
            'analysis': data.get('analysis', {}),
            'timestamp': datetime.now().isoformat()
        }

    async def _generate_text(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self._create_text_prompt(context)
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a crypto trading expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=280,
                temperature=0.7
            )

            return {
                'text': response.choices[0].message.content,
                'prompt': prompt
            }

        except Exception as e:
            self.logger.error(f"Failed to generate text: {e}")
            raise

    async def _generate_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self._create_image_prompt(context)
            response = await openai.Image.acreate(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )

            return {
                'image_url': response.data[0].url,
                'prompt': prompt
            }

        except Exception as e:
            self.logger.error(f"Failed to generate image: {e}")
            raise

    def _create_text_prompt(self, context: Dict[str, Any]) -> str:
        market_data = context.get('market_data', {})
        sentiment = context.get('sentiment', {})

        return f"""Create a concise crypto trading update based on:
        - Market Data: {market_data}
        - Sentiment: {sentiment}
        
        Format: Professional, informative tweet with relevant cashtags."""

    def _create_image_prompt(self, context: Dict[str, Any]) -> str:
        return "Create a professional crypto market analysis visualization"