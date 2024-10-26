import logging
from typing import Dict, Any
from datetime import datetime
import numpy as np

class RiskAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.risk')

    async def analyze_risk(
        self,
        market_data: Dict[str, Any],
        portfolio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            volatility_risk = self._calculate_volatility_risk(market_data)
            exposure_risk = self._calculate_exposure_risk(portfolio_data)
            correlation_risk = self._calculate_correlation_risk(market_data)
            liquidity_risk = self._calculate_liquidity_risk(market_data)
            
            overall_risk = self._calculate_overall_risk({
                'volatility': volatility_risk,
                'exposure': exposure_risk,
                'correlation': correlation_risk,
                'liquidity': liquidity_risk
            })
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_risk': overall_risk,
                'components': {
                    'volatility_risk': volatility_risk,
                    'exposure_risk': exposure_risk,
                    'correlation_risk': correlation_risk,
                    'liquidity_risk': liquidity_risk
                }
            }
        except Exception as e:
            self.logger.error(f"Risk analysis failed: {e}")
            return {}

    def _calculate_volatility_risk(self, data: Dict[str, Any]) -> float:
        try:
            prices = data.get('price_history', [])
            if not prices:
                return 0.0
                
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns) * np.sqrt(365)
            
            # Normalize volatility to 0-1 scale
            return float(min(1.0, volatility))
            
        except Exception as e:
            self.logger.error(f"Volatility risk calculation failed: {e}")
            return 0.0

    def _calculate_exposure_risk(self, portfolio: Dict[str, Any]) -> float:
        try:
            total_value = sum(
                position['value']
                for position in portfolio.values()
            )
            
            # Calculate concentration risk
            max_position = max(
                (position['value'] for position in portfolio.values()),
                default=0
            )
            
            if total_value == 0:
                return 0.0
                
            concentration = max_position / total_value
            return float(concentration)
            
        except Exception as e:
            self.logger.error(f"Exposure risk calculation failed: {e}")
            return 0.0

    def _calculate_correlation_risk(self, data: Dict[str, Any]) -> float:
        try:
            assets = data.get('assets', {})
            if not assets:
                return 0.0
                
            correlations = []
            prices = {
                asset: data['price_history']
                for asset, data in assets.items()
            }
            
            for asset1 in prices:
                for asset2 in prices:
                    if asset1 < asset2:
                        corr = np.corrcoef(prices[asset1], prices[asset2])[0, 1]
                        correlations.append(abs(corr))
            
            return float(np.mean(correlations)) if correlations else 0.0
            
        except Exception as e:
            self.logger.error(f"Correlation risk calculation failed: {e}")
            return 0.0

    def _calculate_liquidity_risk(self, data: Dict[str, Any]) -> float:
        try:
            volume = data.get('volume_history', [])
            if not volume:
                return 0.0
                
            avg_volume = np.mean(volume)
            recent_volume = np.mean(volume[-5:])
            
            # Higher score means higher liquidity risk
            liquidity_risk = 1 - (recent_volume / avg_volume)
            return float(max(0.0, min(1.0, liquidity_risk)))
            
        except Exception as e:
            self.logger.error(f"Liquidity risk calculation failed: {e}")
            return 0.0

    def _calculate_overall_risk(self, components: Dict[str, float]) -> float:
        weights = {
            'volatility': 0.3,
            'exposure': 0.3,
            'correlation': 0.2,
            'liquidity': 0.2
        }
        
        weighted_sum = sum(
            score * weights[component]
            for component, score in components.items()
        )
        
        return float(weighted_sum)