import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from dataclasses import dataclass

@dataclass
class Strategy:
    id: str
    name: str
    parameters: Dict[str, Any]
    performance: Dict[str, float]
    last_updated: datetime

class StrategyOptimizer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.learning.strategy')
        self.strategies: Dict[str, Strategy] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.learning_rate = 0.1
        self.exploration_rate = 0.2

    async def optimize_strategies(
        self,
        market_data: Dict[str, Any],
        trading_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            # Update strategy performance
            self._update_performance(trading_results)
            
            # Generate optimized parameters
            optimizations = self._generate_optimizations(market_data)
            
            # Evolve strategies
            evolved_strategies = self._evolve_strategies()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'optimizations': optimizations,
                'evolved_strategies': evolved_strategies,
                'performance_metrics': self._calculate_performance_metrics()
            }
        except Exception as e:
            self.logger.error(f"Strategy optimization failed: {e}")
            return {}

    def _update_performance(self, trading_results: Dict[str, Any]) -> None:
        for strategy_id, strategy in self.strategies.items():
            # Calculate strategy performance
            performance = self._calculate_strategy_performance(
                strategy,
                trading_results
            )
            
            # Update strategy with new performance data
            strategy.performance.update(performance)
            strategy.last_updated = datetime.now()
            
            # Add to performance history
            self.performance_history.append({
                'strategy_id': strategy_id,
                'timestamp': datetime.now().isoformat(),
                'performance': performance
            })

    def _calculate_strategy_performance(
        self,
        strategy: Strategy,
        trading_results: Dict[str, Any]
    ) -> Dict[str, float]:
        strategy_trades = [
            trade for trade in trading_results.get('trades', [])
            if trade.get('strategy_id') == strategy.id
        ]
        
        if not strategy_trades:
            return {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0
            }

        # Calculate win rate
        wins = sum(1 for trade in strategy_trades if trade.get('profit', 0) > 0)
        win_rate = wins / len(strategy_trades)

        # Calculate profit factor
        profits = sum(trade.get('profit', 0) for trade in strategy_trades if trade.get('profit', 0) > 0)
        losses = abs(sum(trade.get('profit', 0) for trade in strategy_trades if trade.get('profit', 0) < 0))
        profit_factor = profits / losses if losses > 0 else float('inf')

        # Calculate Sharpe ratio
        returns = [trade.get('profit', 0) / trade.get('investment', 1) for trade in strategy_trades]
        if len(returns) > 1:
            sharpe_ratio = float(np.mean(returns) / np.std(returns) * np.sqrt(365))
        else:
            sharpe_ratio = 0.0

        return {
            'win_rate': float(win_rate),
            'profit_factor': float(profit_factor),
            'sharpe_ratio': float(sharpe_ratio)
        }

    def _generate_optimizations(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        optimizations = []
        
        for strategy in self.strategies.values():
            # Generate parameter optimizations
            optimal_params = self._optimize_parameters(strategy, market_data)
            
            if optimal_params != strategy.parameters:
                optimizations.append({
                    'strategy_id': strategy.id,
                    'current_params': strategy.parameters,
                    'optimal_params': optimal_params,
                    'expected_improvement': self._estimate_improvement(
                        strategy,
                        optimal_params
                    )
                })

        return optimizations

    def _optimize_parameters(
        self,
        strategy: Strategy,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        optimized = strategy.parameters.copy()
        
        # Optimize each parameter
        for param, value in strategy.parameters.items():
            if isinstance(value, (int, float)):
                # Try variations around current value
                variations = [
                    value * (1 - self.learning_rate),
                    value,
                    value * (1 + self.learning_rate)
                ]
                
                # Evaluate each variation
                scores = [
                    self._evaluate_parameters(
                        strategy,
                        {**optimized, param: var},
                        market_data
                    )
                    for var in variations
                ]
                
                # Select best variation
                best_idx = np.argmax(scores)
                optimized[param] = variations[best_idx]

        return optimized

    def _evaluate_parameters(
        self,
        strategy: Strategy,
        parameters: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> float:
        # Simulate strategy with given parameters
        simulation_results = self._simulate_strategy(
            strategy,
            parameters,
            market_data
        )
        
        # Calculate score based on multiple metrics
        score = (
            simulation_results.get('win_rate', 0) * 0.3 +
            min(simulation_results.get('profit_factor', 0), 3) / 3 * 0.4 +
            min(simulation_results.get('sharpe_ratio', 0), 3) / 3 * 0.3
        )
        
        return float(score)

    def _simulate_strategy(
        self,
        strategy: Strategy,
        parameters: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, float]:
        # Implement strategy simulation logic
        return {
            'win_rate': 0.5,
            'profit_factor': 1.5,
            'sharpe_ratio': 1.0
        }

    def _estimate_improvement(
        self,
        strategy: Strategy,
        new_params: Dict[str, Any]
    ) -> float:
        current_performance = np.mean(list(strategy.performance.values()))
        
        # Estimate improvement based on parameter changes
        param_changes = [
            abs(new_params[k] - strategy.parameters[k]) / strategy.parameters[k]
            for k in new_params
            if isinstance(strategy.parameters.get(k), (int, float))
        ]
        
        if not param_changes:
            return 0.0
            
        # More conservative improvement estimate for larger changes
        avg_change = float(np.mean(param_changes))
        return min(avg_change * self.learning_rate, 0.1)

    def _evolve_strategies(self) -> List[Dict[str, Any]]:
        evolved = []
        
        for strategy in self.strategies.values():
            if self._should_evolve(strategy):
                # Create evolved version of strategy
                evolved_strategy = self._create_evolved_strategy(strategy)
                
                evolved.append({
                    'original_id': strategy.id,
                    'evolved_id': evolved_strategy.id,
                    'changes': self._describe_evolution(
                        strategy,
                        evolved_strategy
                    )
                })
                
                # Add evolved strategy to pool
                self.strategies[evolved_strategy.id] = evolved_strategy

        return evolved

    def _should_evolve(self, strategy: Strategy) -> bool:
        # Check if strategy performance is stagnant
        recent_performance = [
            p['performance']
            for p in self.performance_history[-10:]
            if p['strategy_id'] == strategy.id
        ]
        
        if len(recent_performance) < 10:
            return False
            
        # Calculate performance trend
        performance_values = [
            np.mean(list(p.values()))
            for p in recent_performance
        ]
        
        trend = np.polyfit(range(len(performance_values)), performance_values, 1)[0]
        
        return trend < 0.01  # Evolve if improvement is minimal

    def _create_evolved_strategy(self, strategy: Strategy) -> Strategy:
        # Create new strategy with evolved parameters
        evolved_params = strategy.parameters.copy()
        
        # Add random variations to parameters
        for param, value in evolved_params.items():
            if isinstance(value, (int, float)):
                variation = np.random.normal(0, self.exploration_rate)
                evolved_params[param] = value * (1 + variation)

        return Strategy(
            id=f"{strategy.id}_evolved_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=f"{strategy.name}_evolved",
            parameters=evolved_params,
            performance={},
            last_updated=datetime.now()
        )

    def _describe_evolution(
        self,
        original: Strategy,
        evolved: Strategy
    ) -> Dict[str, Any]:
        changes = {}
        
        for param in original.parameters:
            if param in evolved.parameters:
                orig_value = original.parameters[param]
                new_value = evolved.parameters[param]
                
                if isinstance(orig_value, (int, float)):
                    pct_change = (new_value - orig_value) / orig_value
                    changes[param] = {
                        'original': orig_value,
                        'evolved': new_value,
                        'pct_change': float(pct_change)
                    }

        return changes

    def _calculate_performance_metrics(self) -> Dict[str, float]:
        if not self.performance_history:
            return {}
            
        recent_performance = self.performance_history[-100:]
        
        metrics = {}
        for key in ['win_rate', 'profit_factor', 'sharpe_ratio']:
            values = [
                p['performance'].get(key, 0)
                for p in recent_performance
            ]
            metrics[f'avg_{key}'] = float(np.mean(values))
            metrics[f'{key}_trend'] = float(
                np.polyfit(range(len(values)), values, 1)[0]
            )
            
        return metrics