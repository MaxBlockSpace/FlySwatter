import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta

class RiskAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.portfolio.risk')
        
    def analyze_risk(self, asset_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            volatility = self._calculate_volatility(asset_data)
            liquidity = self._assess_liquidity(asset_data)
            market_risk = self._assess_market_risk(market_data)
            correlation = self._calculate_correlation(asset_data, market_data)
            
            risk_score = self._compute_risk_score(
                volatility=volatility,
                liquidity=liquidity,
                market_risk=market_risk,
                correlation=correlation
            )
            
            return {
                'score': risk_score,
                'components': {
                    'volatility': volatility,
                    'liquidity': liquidity,
                    'market_risk': market_risk,
                    'correlation': correlation
                },
                'level': self._risk_level(risk_score),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Risk analysis failed: {e}")
            return None

    def _calculate_volatility(self, data: Dict[str, Any]) -> float:
        prices = data.get('price_history', [])
        if not prices:
            return 0.0
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns) * np.sqrt(365))

    def _assess_liquidity(self, data: Dict[str, Any]) -> float:
        volume = data.get('24h_volume', 0)
        market_cap = data.get('market_cap', 0)
        if market_cap == 0:
            return 0.0
        return min(1.0, volume / market_cap)

    def _assess_market_risk(self, data: Dict[str, Any]) -> float:
        sentiment = data.get('market_sentiment', 0)
        trend = data.get('market_trend', 0)
        volatility = data.get('market_volatility', 0)
        
        return (abs(sentiment) + abs(trend) + volatility) / 3

    def _calculate_correlation(self, asset_data: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        asset_returns = np.diff(asset_data.get('price_history', []))
        market_returns = np.diff(market_data.get('price_history', []))
        
        if len(asset_returns) == len(market_returns) and len(asset_returns) > 0:
            return float(np.corrcoef(asset_returns, market_returns)[0, 1])
        return 0.0

    def _compute_risk_score(self, **components: Dict[str, float]) -> float:
        weights = {
            'volatility': 0.4,
            'liquidity': 0.2,
            'market_risk': 0.2,
            'correlation': 0.2
        }
        
        score = sum(
            component * weights[name]
            for name, component in components.items()
        )
        
        return min(1.0, max(0.0, score))

    def _risk_level(self, score: float) -> str:
        if score < 0.3:
            return 'low'
        elif score < 0.7:
            return 'medium'
        else:
            return 'high'