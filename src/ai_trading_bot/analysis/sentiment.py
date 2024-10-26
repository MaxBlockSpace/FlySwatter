import logging
from typing import Dict, Any, List
from datetime import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.sentiment')
        self.sia = SentimentIntensityAnalyzer()
        
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')

    async def analyze_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'overall': 0,
                'sources': {}
            }

            if 'news' in data:
                results['sources']['news'] = await self._analyze_news(data['news'])
            
            if 'social' in data:
                results['sources']['social'] = await self._analyze_social(data['social'])

            results['overall'] = self._calculate_overall_sentiment(results['sources'])
            return results

        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return {'error': str(e)}

    async def _analyze_news(self, news_data: List[Dict[str, Any]]) -> Dict[str, float]:
        try:
            sentiments = []
            for article in news_data:
                vader_score = self.sia.polarity_scores(article['content'])
                textblob_score = TextBlob(article['content']).sentiment.polarity
                
                combined_score = (vader_score['compound'] + textblob_score) / 2
                sentiments.append(combined_score)

            return {
                'average': float(np.mean(sentiments)) if sentiments else 0,
                'latest': float(sentiments[-1]) if sentiments else 0,
                'count': len(sentiments)
            }

        except Exception as e:
            self.logger.error(f"News sentiment analysis failed: {e}")
            return {'average': 0, 'latest': 0, 'count': 0}

    async def _analyze_social(self, social_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        try:
            results = {}
            for platform, posts in social_data.items():
                sentiments = []
                for post in posts:
                    vader_score = self.sia.polarity_scores(post['content'])
                    textblob_score = TextBlob(post['content']).sentiment.polarity
                    combined_score = (vader_score['compound'] + textblob_score) / 2
                    sentiments.append(combined_score)

                results[platform] = {
                    'average': float(np.mean(sentiments)) if sentiments else 0,
                    'latest': float(sentiments[-1]) if sentiments else 0,
                    'count': len(sentiments)
                }

            return results

        except Exception as e:
            self.logger.error(f"Social sentiment analysis failed: {e}")
            return {}

    def _calculate_overall_sentiment(self, sources: Dict[str, Any]) -> float:
        try:
            weights = {
                'news': 0.6,
                'social': 0.4
            }

            weighted_sum = 0
            total_weight = 0

            for source, weight in weights.items():
                if source in sources:
                    score = sources[source].get('average', 0)
                    weighted_sum += score * weight
                    total_weight += weight

            return float(weighted_sum / total_weight) if total_weight > 0 else 0

        except Exception as e:
            self.logger.error(f"Overall sentiment calculation failed: {e}")
            return 0