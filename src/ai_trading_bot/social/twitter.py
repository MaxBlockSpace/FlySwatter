import logging
import tweepy
from typing import Dict, Any
from datetime import datetime

class TwitterManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.social.twitter')
        self.api = None

    def initialize(self, credentials: Dict[str, str]) -> None:
        try:
            auth = tweepy.OAuthHandler(
                credentials['consumer_key'],
                credentials['consumer_secret']
            )
            auth.set_access_token(
                credentials['access_token'],
                credentials['access_token_secret']
            )
            self.api = tweepy.API(auth)
            self.logger.info("Twitter API initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API: {e}")
            raise

    async def post_update(self, content: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.api:
                raise RuntimeError("Twitter API not initialized")

            if content.get('type') == 'image':
                media = self.api.media_upload(content['image_path'])
                tweet = self.api.update_status(
                    status=content['text'],
                    media_ids=[media.media_id]
                )
            else:
                tweet = self.api.update_status(content['text'])

            return {
                'success': True,
                'tweet_id': tweet.id,
                'url': f"https://twitter.com/i/web/status/{tweet.id}"
            }

        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_sentiment(self) -> Dict[str, Any]:
        try:
            if not self.api:
                raise RuntimeError("Twitter API not initialized")

            tweets = self.api.search_tweets(
                q='$BTC OR #Bitcoin',
                lang='en',
                count=100,
                tweet_mode='extended'
            )

            return {
                'timestamp': datetime.now().isoformat(),
                'tweets': [
                    {
                        'id': tweet.id,
                        'text': tweet.full_text,
                        'created_at': tweet.created_at.isoformat(),
                        'user': tweet.user.screen_name,
                        'metrics': {
                            'followers': tweet.user.followers_count,
                            'retweets': tweet.retweet_count,
                            'likes': tweet.favorite_count
                        }
                    }
                    for tweet in tweets
                ]
            }

        except Exception as e:
            self.logger.error(f"Failed to get Twitter sentiment: {e}")
            return {'error': str(e)}

    async def get_engagement(self) -> Dict[str, Any]:
        try:
            if not self.api:
                raise RuntimeError("Twitter API not initialized")

            user = self.api.verify_credentials()
            tweets = self.api.user_timeline(count=100, tweet_mode='extended')

            total_engagement = sum(
                tweet.retweet_count + tweet.favorite_count
                for tweet in tweets
            )

            return {
                'timestamp': datetime.now().isoformat(),
                'followers': user.followers_count,
                'total_engagement': total_engagement,
                'engagement_rate': total_engagement / (len(tweets) * user.followers_count)
                if tweets and user.followers_count > 0 else 0
            }

        except Exception as e:
            self.logger.error(f"Failed to get Twitter engagement: {e}")
            return {'error': str(e)}