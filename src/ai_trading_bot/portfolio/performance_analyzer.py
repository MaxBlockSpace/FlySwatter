import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np

class PerformanceAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.portfolio.performance')

    def analyze_performance(
        self,
        portfolio_history: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        timeframe: str = '1d'
    ) -> Dict[str, Any]:
        try:
            returns = self._calculate_returns(portfolio_history)
            metrics = self._calculate_metrics(returns, market_data)
            analysis = self._analyze_attribution(portfolio_history)
            
            return {
                'metrics': metrics,
                'attribution': analysis,
                'timestamp': datetime.now().isoformat(),
                'timeframe': timeframe
            }
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
            return None

    def _calculate_returns(self, history: List[Dict[str, Any]]) -> Dict[str, float]:
        if not history:
            return {}
            
        values = [snapshot['total_value'] for snapshot in history]
        returns = np.diff(values) / values[:-1]
        
        return {
            'total_return': float((values[-1] / values[0]) - 1),
            'daily_returns': returns.tolist(),
            'annualized_return': float(((values[-1] / values[0]) ** (365 / len(history)) - 1)),
            'volatility': float(np.std(returns) * np.sqrt(365))
        }

    def _calculate_metrics(
        self,
        returns: Dict[str, float],
        market_data: Dict[str, Any]
    ) -> Dict[str, float]:
        risk_free_rate = market_data.get('risk_free_rate', 0.02)
        market_return = market_data.get('market_return', 0)
        
        sharpe = self._calculate_sharpe_ratio(
            returns['annualized_return'],
            returns['volatility'],
            risk_free_rate
        )
        
        sortino = self._calculate_sortino_ratio(
            returns['daily_returns'],
            risk_free_rate
        )
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': self._calculate_max_drawdown(returns['daily_returns']),
            'win_rate': self._calculate_win_rate(returns['daily_returns'])
        }

    def _analyze_attribution(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        attribution = {}
        
        for snapshot in history:
            for asset, position in snapshot['positions'].items():
                if asset not in attribution:
                    attribution[asset] = {
                        'contribution': 0,
                        'weight': 0,
                        'return': 0
                    }
                
                attribution[asset]['contribution'] += position['pnl']
                attribution[asset]['weight'] = position['value'] / snapshot['total_value']
                attribution[asset]['return'] = position['return']
        
        return attribution

    def _calculate_sharpe_ratio(
        self,
        returns: float,
        volatility: float,
        risk_free_rate: float
    ) -> float:
        if volatility == 0:
            return 0
        return (returns - risk_free_rate) / volatility

    def _calculate_sortino_ratio(
        self,
        returns: List[float],
        risk_free_rate: float
    ) -> float:
        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return 0
            
        downside_deviation = np.std(negative_returns) * np.sqrt(365)
        if downside_deviation == 0:
            return 0
            
        excess_return = np.mean(returns) * 365 - risk_free_rate
        return excess_return / downside_deviation

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative / running_max - 1
        return float(np.min(drawdowns))

    def _calculate_win_rate(self, returns: List[float]) -> float:
        if not returns:
            return 0
        wins = sum(1 for r in returns if r > 0)
        return float(wins / len(returns))