import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

class TechnicalAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.technical')

    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            indicators = {
                'moving_averages': self._calculate_moving_averages(market_data),
                'rsi': self._calculate_rsi(market_data),
                'macd': self._calculate_macd(market_data),
                'bollinger_bands': self._calculate_bollinger_bands(market_data)
            }
            
            signals = self._generate_signals(indicators)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'indicators': indicators,
                'signals': signals
            }
        except Exception as e:
            self.logger.error(f"Technical analysis failed: {e}")
            return {}

    def _calculate_moving_averages(self, data: Dict[str, Any]) -> Dict[str, float]:
        prices = data.get('price_history', [])
        if not len(prices) >= 50:
            return {}
            
        return {
            'sma_20': float(np.mean(prices[-20:])),
            'sma_50': float(np.mean(prices[-50:])),
            'ema_20': self._calculate_ema(prices, 20),
            'ema_50': self._calculate_ema(prices, 50)
        }

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        if not len(prices) >= period:
            return 0.0
            
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
            
        return float(ema)

    def _calculate_rsi(self, data: Dict[str, Any], period: int = 14) -> float:
        prices = data.get('price_history', [])
        if not len(prices) >= period:
            return 0.0
            
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        return float(100 - (100 / (1 + rs)))

    def _calculate_macd(self, data: Dict[str, Any]) -> Dict[str, float]:
        prices = data.get('price_history', [])
        if not len(prices) >= 26:
            return {}
            
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        signal_line = self._calculate_ema([macd_line], 9)
        
        return {
            'macd_line': float(macd_line),
            'signal_line': float(signal_line),
            'histogram': float(macd_line - signal_line)
        }

    def _calculate_bollinger_bands(
        self,
        data: Dict[str, Any],
        period: int = 20,
        std_dev: int = 2
    ) -> Dict[str, float]:
        prices = data.get('price_history', [])
        if not len(prices) >= period:
            return {}
            
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        return {
            'middle': float(sma),
            'upper': float(sma + (std_dev * std)),
            'lower': float(sma - (std_dev * std))
        }

    def _generate_signals(self, indicators: Dict[str, Any]) -> Dict[str, str]:
        signals = {}
        
        # Moving Average signals
        ma = indicators.get('moving_averages', {})
        if ma:
            if ma['sma_20'] > ma['sma_50']:
                signals['ma_trend'] = 'bullish'
            else:
                signals['ma_trend'] = 'bearish'
        
        # RSI signals
        rsi = indicators.get('rsi', 0)
        if rsi:
            if rsi > 70:
                signals['rsi'] = 'overbought'
            elif rsi < 30:
                signals['rsi'] = 'oversold'
            else:
                signals['rsi'] = 'neutral'
        
        # MACD signals
        macd = indicators.get('macd', {})
        if macd:
            if macd['histogram'] > 0:
                signals['macd'] = 'bullish'
            else:
                signals['macd'] = 'bearish'
        
        return signals