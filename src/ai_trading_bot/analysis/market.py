import logging
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.market')

    async def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            volatility = self._calculate_volatility(market_data)
            trend = self._analyze_trend(market_data)
            volume = self._analyze_volume(market_data)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'volatility': volatility,
                    'trend': trend,
                    'volume': volume
                }
            }
        except Exception as e:
            self.logger.error(f"Market analysis failed: {e}")
            return {}

    def _calculate_volatility(self, data: Dict[str, Any]) -> Dict[str, float]:
        try:
            prices = data.get('prices', [])
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
            prices = data.get('prices', [])
            if not prices:
                return {'direction': 'neutral', 'strength': 0}

            ma20 = np.mean(prices[-20:])
            ma50 = np.mean(prices[-50:])
            
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

    def _analyze_volume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            volumes = data.get('volumes', [])
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