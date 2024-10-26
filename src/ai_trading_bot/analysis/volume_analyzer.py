import logging
from typing import Dict, Any
import numpy as np
from datetime import datetime

class VolumeAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.volume')

    async def analyze_volume(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            volume_profile = self._calculate_volume_profile(market_data)
            liquidity_analysis = self._analyze_liquidity(market_data)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'volume_profile': volume_profile,
                'liquidity': liquidity_analysis
            }
        except Exception as e:
            self.logger.error(f"Volume analysis failed: {e}")
            return {}

    def _calculate_volume_profile(self, data: Dict[str, Any]) -> Dict[str, float]:
        volumes = data.get('volume_history', [])
        if not volumes:
            return {}
            
        return {
            'average_volume': float(np.mean(volumes)),
            'recent_volume': float(np.mean(volumes[-24:])),
            'volume_trend': float(np.mean(volumes[-24:]) / np.mean(volumes))
        }

    def _analyze_liquidity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        order_book = data.get('order_book', {})
        if not order_book:
            return {}
            
        return {
            'bid_depth': self._calculate_depth(order_book.get('bids', [])),
            'ask_depth': self._calculate_depth(order_book.get('asks', [])),
            'spread': self._calculate_spread(order_book)
        }

    def _calculate_depth(self, orders: list) -> float:
        return sum(order['amount'] for order in orders[:10])

    def _calculate_spread(self, order_book: Dict[str, list]) -> float:
        if not order_book.get('bids') or not order_book.get('asks'):
            return 0.0
        best_bid = max(bid['price'] for bid in order_book['bids'])
        best_ask = min(ask['price'] for ask in order_book['asks'])
        return (best_ask - best_bid) / best_bid