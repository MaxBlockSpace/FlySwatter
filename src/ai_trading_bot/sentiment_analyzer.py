import logging
import openai
from typing import Dict, Any
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self, context_manager):
        self.logger = logging.getLogger('ai_trading_bot.sentiment')
        self.context = context_manager
        self.sia = SentimentIntensityAnalyzer()
        
        # Initialize NLTK components
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')

    async def analyze_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        results = {
            'overall': 0,
            'sources': {}
        }

        try:
            if 'news' in data:
                results['sources']['news'] = await self._analyze_news(data['news'])
            
            if 'social' in data:
                results['sources']['social'] = await self._analyze_social(data['social'])
            
            results['overall'] = self._calculate_overall_sentiment(results['sources'])
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
        
        return results

    async def _analyze_news(self, news_data: Dict[str, Any]) -> float:
        total_sentiment = 0
        count = 0

        for article in news_data.get('articles', []):
            sentiment = await self._analyze_text_gpt(article['content'])
            total_sentiment += sentiment
            count += 1

        return total_sentiment / count if count > 0 else 0

    async def _analyze_social(self, social_data: Dict[str, Any]) -> float:
        total_sentiment = 0
        count = 0

        for post in social_data.get('posts', []):
            sentiment = self.sia.polarity_scores(post['content'])['compound']
            total_sentiment += sentiment
            count += 1

        return total_sentiment / count if count > 0 else 0

    async def _analyze_text_gpt(self, text: str) -> float:
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the following text and return a score between -1 (very negative) and 1 (very positive)."},
                    {"role": "user", "content": text}
                ]
            )
            return float(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"GPT sentiment analysis failed: {e}")
            return 0

    def _calculate_overall_sentiment(self, sources: Dict[str, float]) -> float:
        weights = {
            'news': 0.6,
            'social': 0.4
        }

        weighted_sum = 0
        total_weight = 0

        for source, sentiment in sources.items():
            weight = weights.get(source, 0)
            weighted_sum += sentiment * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0