import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

class PatternRecognizer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.pattern')

    async def identify_patterns(
        self,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            candlestick_patterns = self._identify_candlestick_patterns(market_data)
            chart_patterns = self._identify_chart_patterns(market_data)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'patterns': {
                    'candlestick': candlestick_patterns,
                    'chart': chart_patterns
                }
            }
        except Exception as e:
            self.logger.error(f"Pattern recognition failed: {e}")
            return {}

    def _identify_candlestick_patterns(
        self,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        try:
            patterns = []
            candles = data.get('candles', [])
            
            if len(candles) < 3:
                return patterns

            # Check for common candlestick patterns
            patterns.extend(self._find_doji(candles))
            patterns.extend(self._find_hammer(candles))
            patterns.extend(self._find_engulfing(candles))
            
            return patterns
        except Exception as e:
            self.logger.error(f"Candlestick pattern recognition failed: {e}")
            return []

    def _identify_chart_patterns(
        self,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        try:
            patterns = []
            prices = data.get('price_history', [])
            
            if len(prices) < 20:
                return patterns

            # Check for common chart patterns
            patterns.extend(self._find_double_bottom(prices))
            patterns.extend(self._find_double_top(prices))
            patterns.extend(self._find_head_and_shoulders(prices))
            
            return patterns
        except Exception as e:
            self.logger.error(f"Chart pattern recognition failed: {e}")
            return []

    def _find_doji(self, candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        for i, candle in enumerate(candles[-5:]):  # Check last 5 candles
            if abs(candle['open'] - candle['close']) < (candle['high'] - candle['low']) * 0.1:
                patterns.append({
                    'type': 'doji',
                    'position': i,
                    'confidence': 0.8
                })
        return patterns

    def _find_hammer(self, candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        for i, candle in enumerate(candles[-5:]):
            body = abs(candle['open'] - candle['close'])
            lower_shadow = min(candle['open'], candle['close']) - candle['low']
            upper_shadow = candle['high'] - max(candle['open'], candle['close'])
            
            if (lower_shadow > body * 2) and (upper_shadow < body * 0.5):
                patterns.append({
                    'type': 'hammer',
                    'position': i,
                    'confidence': 0.7
                })
        return patterns

    def _find_engulfing(self, candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        for i in range(1, min(5, len(candles))):
            prev = candles[-i-1]
            curr = candles[-i]
            
            if (prev['close'] < prev['open'] and  # Previous red
                curr['close'] > curr['open'] and  # Current green
                curr['open'] < prev['close'] and  # Current opens below prev close
                curr['close'] > prev['open']):    # Current closes above prev open
                patterns.append({
                    'type': 'bullish_engulfing',
                    'position': i,
                    'confidence': 0.9
                })
        return patterns

    def _find_double_bottom(self, prices: List[float]) -> List[Dict[str, Any]]:
        patterns = []
        min_distance = 10  # Minimum distance between bottoms
        
        for i in range(min_distance, len(prices)-min_distance):
            if self._is_local_minimum(prices, i):
                for j in range(i+min_distance, len(prices)):
                    if self._is_local_minimum(prices, j):
                        if abs(prices[i] - prices[j]) < prices[i] * 0.02:  # 2% tolerance
                            patterns.append({
                                'type': 'double_bottom',
                                'positions': [i, j],
                                'confidence': 0.7
                            })
        return patterns

    def _find_double_top(self, prices: List[float]) -> List[Dict[str, Any]]:
        patterns = []
        min_distance = 10
        
        for i in range(min_distance, len(prices)-min_distance):
            if self._is_local_maximum(prices, i):
                for j in range(i+min_distance, len(prices)):
                    if self._is_local_maximum(prices, j):
                        if abs(prices[i] - prices[j]) < prices[i] * 0.02:
                            patterns.append({
                                'type': 'double_top',
                                'positions': [i, j],
                                'confidence': 0.7
                            })
        return patterns

    def _find_head_and_shoulders(self, prices: List[float]) -> List[Dict[str, Any]]:
        patterns = []
        min_distance = 5
        
        for i in range(min_distance, len(prices)-2*min_distance):
            if (self._is_local_maximum(prices, i) and
                self._is_local_maximum(prices, i+min_distance) and
                self._is_local_maximum(prices, i+2*min_distance)):
                
                head = prices[i+min_distance]
                left_shoulder = prices[i]
                right_shoulder = prices[i+2*min_distance]
                
                if (head > left_shoulder and
                    head > right_shoulder and
                    abs(left_shoulder - right_shoulder) < left_shoulder * 0.05):
                    patterns.append({
                        'type': 'head_and_shoulders',
                        'positions': [i, i+min_distance, i+2*min_distance],
                        'confidence': 0.8
                    })
        return patterns

    def _is_local_minimum(self, prices: List[float], index: int) -> bool:
        if index == 0 or index == len(prices) - 1:
            return False
        return prices[index] < prices[index-1] and prices[index] < prices[index+1]

    def _is_local_maximum(self, prices: List[float], index: int) -> bool:
        if index == 0 or index == len(prices) - 1:
            return False
        return prices[index] > prices[index-1] and prices[index] > prices[index+1]