import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class PositionManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.portfolio.position')

    def calculate_position_size(
        self,
        asset: str,
        portfolio_value: float,
        risk_metrics: Dict[str, Any],
        strategy_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            max_position_size = portfolio_value * strategy_params.get('max_position_pct', 0.2)
            risk_adjusted_size = self._adjust_for_risk(max_position_size, risk_metrics)
            optimal_size = self._optimize_for_liquidity(risk_adjusted_size, risk_metrics)
            
            return {
                'asset': asset,
                'optimal_size': optimal_size,
                'max_size': max_position_size,
                'risk_adjusted': risk_adjusted_size,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Position size calculation failed: {e}")
            return None

    def _adjust_for_risk(self, base_size: float, risk_metrics: Dict[str, Any]) -> float:
        risk_score = risk_metrics['score']
        risk_multiplier = 1 - (risk_score * 0.5)  # Reduce position size as risk increases
        return base_size * risk_multiplier

    def _optimize_for_liquidity(self, size: float, risk_metrics: Dict[str, Any]) -> float:
        liquidity = risk_metrics['components']['liquidity']
        # Ensure position size doesn't exceed 10% of daily volume
        max_liquidity_size = liquidity * 0.1
        return min(size, max_liquidity_size)

    def calculate_rebalancing_trades(
        self,
        current_positions: Dict[str, Any],
        target_positions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        trades = []
        
        for asset, target in target_positions.items():
            current = current_positions.get(asset, {'amount': 0})
            difference = target['amount'] - current['amount']
            
            if abs(difference) > 0:
                trades.append({
                    'asset': asset,
                    'action': 'buy' if difference > 0 else 'sell',
                    'amount': abs(difference),
                    'reason': 'rebalancing'
                })
        
        return trades

    def validate_position_limits(
        self,
        position: Dict[str, Any],
        limits: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        if position['amount'] > limits.get('max_position_size', float('inf')):
            return False, "Position exceeds maximum size limit"
            
        if position['value'] > limits.get('max_position_value', float('inf')):
            return False, "Position exceeds maximum value limit"
            
        return True, None