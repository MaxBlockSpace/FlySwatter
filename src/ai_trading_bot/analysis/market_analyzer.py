import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.market')

    async def analyze_market(
        self,
        market_data: Dict[str, Any],
        timeframe: str = '1h'
    ) -> Dict[str, Any]:
        try:
            volatility = self._calculate_volatility(market_data)
            trend = self._analyze_trend(market_data)
            support_resistance = self._find_support_resistance(market_data)
            volume_profile = self._analyze_volume(market_data)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe,
                'metrics': {
                    'volatility': volatility,
                    'trend': trend,
                    'support_resistance': support_resistance,
                    'volume_profile': volume_profile
                }
            }
        except Exception as e:
            self.logger.error(f"Market analysis failed: {e}")
            return {}

    def _calculate_volatility(self, data: Dict[str, Any]) -> Dict[str, float]:
        try:
            prices = data.get('price_history', [])
            if not prices:
                return {'current': 0, 'average': 0, 'trend': 0}

            returns = np.diff(prices) / prices[:-1]
            current_vol = float(np.std(returns[-20:]) * np.sqrt(365))
            avg_vol = float(np.std(returns) * np.sqrt(365))
            vol_trend = float(current_vol - avg_vol)

            return {
                'current': current_vol,
                'average': avg_vol,
                'trend': vol_trend
            }
        except Exception as e:
            self.logger.error(f"Volatility calculation failed: {e}")
            return {'current': 0, 'average': 0, 'trend': 0}

    def _analyze_trend(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prices = data.get('price_history', [])
            if not prices:
                return {'direction': 'neutral', 'strength': 0}

            # Calculate moving averages
            ma20 = np.mean(prices[-20:])
            ma50 = np.mean(prices[-50:])
            
            # Determine trend direction
            if ma20 > ma50:
                direction = 'uptrend'
                strength = (ma20 - ma50) / ma50
            elif ma20 < ma50:
                direction = 'downtrend'
                strength = (ma50 - ma20) / ma50
            else:
                direction = 'neutral'
                strength = 0

            return {
                'direction': direction,
                'strength': float(strength),
                'ma20': float(ma20),
                'ma50': float(ma50)
            }
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {'direction': 'neutral', 'strength': 0}

    def _find_support_resistance(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, List[float]]:
        try:
            prices = data.get('price_history', [])
            if not prices:
                return {'support': [], 'resistance': []}

            # Find local minima and maxima
            support_levels = self._find_local_minima(prices)
            resistance_levels = self._find_local_maxima(prices)

            return {
                'support': support_levels,
                'resistance': resistance_levels
            }
        except Exception as e:
            self.logger.error(f"Support/Resistance analysis failed: {e}")
            return {'support': [], 'resistance': []}

    def _analyze_volume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            volumes = data.get('volume_history', [])
            if not volumes:
                return {'profile': 'neutral', 'strength': 0}

            avg_volume = np.mean(volumes)
            recent_volume = np.mean(volumes[-5:])
            
            if recent_volume > avg_volume * 1.5:
                profile = 'increasing'
                strength = (recent_volume / avg_volume) - 1
            elif recent_volume < avg_volume * 0.5:
                profile = 'decreasing'
                strength = 1 - (recent_volume / avg_volume)
            else:
                profile = 'neutral'
                strength = 0

            return {
                'profile': profile,
                'strength': float(strength),
                'average': float(avg_volume),
                'recent': float(recent_volume)
            }
        except Exception as e:
            self.logger.error(f"Volume analysis failed: {e}")
            return {'profile': 'neutral', 'strength': 0}

    def _find_local_minima(self, prices: List[float]) -> List[float]:
        minima = []
        window_size = 10

        for i in range(window_size, len(prices) - window_size):
            window = prices[i-window_size:i+window_size+1]
            if prices[i] == min(window):
                minima.append(prices[i])

        return minima[-3:] if minima else []  # Return last 3 support levels

    def _find_local_maxima(self, prices: List[float]) -> List[float]:
        maxima = []
        window_size = 10

        for i in range(window_size, len(prices) - window_size):
            window = prices[i-window_size:i+window_size+1]
            if prices[i] == max(window):
                maxima.append(prices[i])

        return maxima[-3:] if maxima else []  # Return last 3 resistance levels