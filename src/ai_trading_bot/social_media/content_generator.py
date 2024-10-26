import logging
import openai
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional, Dict, Any

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.social_media.content')
        self._ensure_directories()

    def _ensure_directories(self):
        Path('data/templates').mkdir(parents=True, exist_ok=True)
        Path('data/generated').mkdir(parents=True, exist_ok=True)

    async def generate_content(self, context: Dict[str, Any], content_type: str) -> Optional[Dict[str, Any]]:
        try:
            if content_type == 'text':
                return await self._generate_text(context)
            elif content_type == 'image':
                return await self._generate_image(context)
            elif content_type == 'meme':
                return await self._generate_meme(context)
            else:
                self.logger.warning(f"Unsupported content type: {content_type}")
                return None
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return None

    async def _generate_text(self, context: Dict[str, Any]) -> Dict[str, Any]:
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
            'type': 'text',
            'content': response.choices[0].message.content,
            'metadata': {'prompt': prompt}
        }

    async def _generate_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._create_image_prompt(context)
        response = await openai.Image.acreate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_path = f"data/generated/img_{context['timestamp']}.png"
        
        return {
            'type': 'image',
            'content': image_path,
            'url': response.data[0].url,
            'metadata': {'prompt': prompt}
        }

    async def _generate_meme(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._select_meme_template(context)
        text = await self._generate_meme_text(context)
        
        image = Image.open(template)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("data/templates/Impact.ttf", 48)
        
        # Position text on image
        self._draw_text_with_outline(draw, text, image.size, font)
        
        output_path = f"data/generated/meme_{context['timestamp']}.png"
        image.save(output_path)
        
        return {
            'type': 'meme',
            'content': output_path,
            'metadata': {'template': template, 'text': text}
        }

    def _create_text_prompt(self, context: Dict[str, Any]) -> str:
        base_prompt = "Create a professional crypto trading update"
        if context.get('sentiment'):
            base_prompt += f" considering the {context['sentiment']} market sentiment"
        if context.get('data'):
            base_prompt += f" based on: {context['data']}"
        return base_prompt

    def _create_image_prompt(self, context: Dict[str, Any]) -> str:
        return f"Create a professional visualization for {context.get('topic', 'crypto trading')}"

    def _select_meme_template(self, context: Dict[str, Any]) -> str:
        # Simple template selection logic
        return "data/templates/default_meme.png"

    async def _generate_meme_text(self, context: Dict[str, Any]) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Create a short, witty crypto meme caption."},
                {"role": "user", "content": str(context)}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content

    def _draw_text_with_outline(self, draw, text: str, size: tuple, font) -> None:
        x = size[0] // 2
        y = size[1] - 60
        outline_color = "black"
        text_color = "white"
        outline_width = 2

        for adj in range(-outline_width, outline_width+1):
            for opp in range(-outline_width, outline_width+1):
                draw.text((x+adj, y+opp), text, font=font, fill=outline_color, anchor="ms")
        draw.text((x, y), text, font=font, fill=text_color, anchor="ms")