import logging
from typing import Dict, Any
from datetime import datetime
import numpy as np

class RiskAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.portfolio.risk')

    async def analyze_risk(
        self,
        portfolio: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            volatility_risk = self._calculate_volatility_risk(portfolio, market_data)
            exposure_risk = self._calculate_exposure_risk(portfolio)
            correlation_risk = self._calculate_correlation_risk(portfolio, market_data)
            
            overall_risk = self._calculate_overall_risk({
                'volatility': volatility_risk,
                'exposure': exposure_risk,
                'correlation': correlation_risk
            })
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_risk': overall_risk,
                'components': {
                    'volatility_risk': volatility_risk,
                    'exposure_risk': exposure_risk,
                    'correlation_risk': correlation_risk
                }
            }
        except Exception as e:
            self.logger.error(f"Risk analysis failed: {e}")
            return {}

    def _calculate_volatility_risk(
        self,
        portfolio: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> float:
        try:
            weighted_vol = 0
            total_value = sum(pos['value'] for pos in portfolio.values())
            
            for asset, position in portfolio.items():
                weight = position['value'] / total_value if total_value > 0 else 0
                volatility = market_data.get('volatility', {}).get(asset, 0)
                weighted_vol += weight * volatility
                
            return float(weighted_vol)
            
        except Exception as e:
            self.logger.error(f"Volatility risk calculation failed: {e}")
            return 0

    def _calculate_exposure_risk(self, portfolio: Dict[str, Any]) -> float:
        try:
            if not portfolio:
                return 0
                
            total_value = sum(pos['value'] for pos in portfolio.values())
            max_exposure = max(pos['value'] for pos in portfolio.values())
            
            return float(max_exposure / total_value if total_value > 0 else 0)
            
        except Exception as e:
            self.logger.error(f"Exposure risk calculation failed: {e}")
            return 0

    def _calculate_correlation_risk(
        self,
        portfolio: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> float:
        try:
            if len(portfolio) < 2:
                return 0
                
            correlations = []
            assets = list(portfolio.keys())
            
            for i in range(len(assets)):
                for j in range(i + 1, len(assets)):
                    corr = self._calculate_pair_correlation(
                        assets[i],
                        assets[j],
                        market_data
                    )
                    correlations.append(abs(corr))
                    
            return float(np.mean(correlations)) if correlations else 0
            
        except Exception as e:
            self.logger.error(f"Correlation risk calculation failed: {e}")
            return 0

    def _calculate_pair_correlation(
        self,
        asset1: str,
        asset2: str,
        market_data: Dict[str, Any]
    ) -> float:
        returns1 = market_data.get('returns', {}).get(asset1, [])
        returns2 = market_data.get('returns', {}).get(asset2, [])
        
        if len(returns1) != len(returns2) or len(returns1) < 2:
            return 0
            
        return float(np.corrcoef(returns1, returns2)[0, 1])

    def _calculate_overall_risk(self, components: Dict[str, float]) -> float:
        weights = {
            'volatility': 0.4,
            'exposure': 0.3,
            'correlation': 0.3
        }
        
        return float(sum(
            score * weights[component]
            for component, score in components.items()
        ))