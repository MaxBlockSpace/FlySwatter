import logging
from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class LearningPattern:
    pattern_id: str
    pattern_type: str
    effectiveness: float
    last_seen: datetime
    success_rate: float
    market_conditions: Dict[str, Any]
    outcomes: List[Dict[str, Any]]

class AdaptiveLearner:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.learning.adaptive')
        self.patterns: Dict[str, LearningPattern] = {}
        self.strategy_effectiveness: Dict[str, float] = defaultdict(float)
        self.market_memory: List[Dict[str, Any]] = []
        self.adaptation_threshold = 0.6
        self.learning_rate = 0.1

    async def analyze_and_adapt(
        self,
        market_data: Dict[str, Any],
        trading_results: Dict[str, Any],
        manipulation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            # Identify new patterns
            new_patterns = self._identify_new_patterns(market_data, manipulation_data)
            
            # Update existing patterns
            self._update_pattern_effectiveness(trading_results)
            
            # Adapt strategies
            adaptations = self._generate_adaptations(market_data)
            
            # Evolve decision weights
            self._evolve_decision_weights(trading_results)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'new_patterns': new_patterns,
                'adaptations': adaptations,
                'effectiveness': dict(self.strategy_effectiveness)
            }
            
        except Exception as e:
            self.logger.error(f"Adaptation analysis failed: {e}")
            return {}

    def _identify_new_patterns(
        self,
        market_data: Dict[str, Any],
        manipulation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        new_patterns = []
        
        # Analyze market behavior patterns
        current_patterns = self._extract_market_patterns(market_data)
        
        # Check for previously unknown patterns
        for pattern in current_patterns:
            pattern_id = self._generate_pattern_id(pattern)
            
            if pattern_id not in self.patterns:
                # New pattern discovered
                new_pattern = LearningPattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern['type'],
                    effectiveness=0.5,  # Initial neutral effectiveness
                    last_seen=datetime.now(),
                    success_rate=0.0,
                    market_conditions=market_data.get('conditions', {}),
                    outcomes=[]
                )
                
                self.patterns[pattern_id] = new_pattern
                new_patterns.append(pattern)
                
                self.logger.info(f"New pattern discovered: {pattern['type']}")
        
        return new_patterns

    def _extract_market_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        patterns = []
        
        # Price action patterns
        if price_pattern := self._analyze_price_pattern(market_data):
            patterns.append(price_pattern)
        
        # Volume patterns
        if volume_pattern := self._analyze_volume_pattern(market_data):
            patterns.append(volume_pattern)
        
        # Order flow patterns
        if order_pattern := self._analyze_order_pattern(market_data):
            patterns.append(order_pattern)
        
        return patterns

    def _analyze_price_pattern(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prices = data.get('price_history', [])
        if len(prices) < 10:
            return None
            
        recent_prices = prices[-10:]
        price_changes = np.diff(recent_prices)
        
        pattern = {
            'type': 'price_pattern',
            'direction': 'up' if sum(price_changes) > 0 else 'down',
            'volatility': float(np.std(price_changes)),
            'magnitude': float(abs(sum(price_changes)))
        }
        
        return pattern

    def _analyze_volume_pattern(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        volumes = data.get('volume_history', [])
        if len(volumes) < 10:
            return None
            
        recent_volumes = volumes[-10:]
        volume_changes = np.diff(recent_volumes)
        
        pattern = {
            'type': 'volume_pattern',
            'trend': 'increasing' if sum(volume_changes) > 0 else 'decreasing',
            'volatility': float(np.std(volume_changes)),
            'magnitude': float(abs(sum(volume_changes)))
        }
        
        return pattern

    def _analyze_order_pattern(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        orders = data.get('order_history', [])
        if len(orders) < 10:
            return None
            
        buy_orders = sum(1 for order in orders if order['side'] == 'buy')
        sell_orders = len(orders) - buy_orders
        
        pattern = {
            'type': 'order_pattern',
            'buy_pressure': buy_orders / len(orders),
            'sell_pressure': sell_orders / len(orders),
            'imbalance': abs(buy_orders - sell_orders) / len(orders)
        }
        
        return pattern

    def _update_pattern_effectiveness(self, trading_results: Dict[str, Any]) -> None:
        for pattern_id, pattern in self.patterns.items():
            # Update pattern with recent trading results
            if relevant_trades := self._find_relevant_trades(pattern, trading_results):
                success_rate = sum(
                    1 for trade in relevant_trades if trade['success']
                ) / len(relevant_trades)
                
                # Update pattern effectiveness using exponential moving average
                pattern.effectiveness = (
                    pattern.effectiveness * (1 - self.learning_rate) +
                    success_rate * self.learning_rate
                )
                
                pattern.success_rate = success_rate
                pattern.outcomes.extend(relevant_trades)
                
                # Trim old outcomes to prevent memory bloat
                if len(pattern.outcomes) > 100:
                    pattern.outcomes = pattern.outcomes[-100:]

    def _find_relevant_trades(
        self,
        pattern: LearningPattern,
        trading_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        relevant_trades = []
        
        for trade in trading_results.get('trades', []):
            if self._is_trade_relevant_to_pattern(trade, pattern):
                relevant_trades.append(trade)
                
        return relevant_trades

    def _is_trade_relevant_to_pattern(
        self,
        trade: Dict[str, Any],
        pattern: LearningPattern
    ) -> bool:
        # Check if trade occurred under similar market conditions
        trade_conditions = trade.get('market_conditions', {})
        pattern_conditions = pattern.market_conditions
        
        similarity_score = self._calculate_condition_similarity(
            trade_conditions,
            pattern_conditions
        )
        
        return similarity_score > 0.8

    def _calculate_condition_similarity(
        self,
        conditions1: Dict[str, Any],
        conditions2: Dict[str, Any]
    ) -> float:
        if not conditions1 or not conditions2:
            return 0.0
            
        common_keys = set(conditions1.keys()) & set(conditions2.keys())
        if not common_keys:
            return 0.0
            
        similarities = []
        for key in common_keys:
            if isinstance(conditions1[key], (int, float)) and isinstance(conditions2[key], (int, float)):
                similarity = 1 - min(abs(conditions1[key] - conditions2[key]) / max(abs(conditions1[key]), abs(conditions2[key])), 1)
                similarities.append(similarity)
                
        return float(np.mean(similarities)) if similarities else 0.0

    def _generate_adaptations(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        adaptations = []
        
        # Analyze pattern effectiveness
        for pattern_id, pattern in self.patterns.items():
            if pattern.effectiveness > self.adaptation_threshold:
                # Pattern is proven effective
                adaptation = self._create_adaptation_strategy(pattern, market_data)
                if adaptation:
                    adaptations.append(adaptation)
            elif pattern.effectiveness < (1 - self.adaptation_threshold):
                # Pattern is proven ineffective
                self._deprecate_pattern(pattern_id)
                
        return adaptations

    def _create_adaptation_strategy(
        self,
        pattern: LearningPattern,
        market_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            current_conditions = market_data.get('conditions', {})
            
            if self._are_conditions_similar(current_conditions, pattern.market_conditions):
                return {
                    'pattern_id': pattern.pattern_id,
                    'type': pattern.pattern_type,
                    'effectiveness': pattern.effectiveness,
                    'recommended_action': self._determine_best_action(pattern),
                    'confidence': self._calculate_confidence(pattern)
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create adaptation strategy: {e}")
            return None

    def _determine_best_action(self, pattern: LearningPattern) -> str:
        successful_actions = defaultdict(int)
        
        for outcome in pattern.outcomes:
            if outcome.get('success'):
                action = outcome.get('action', 'unknown')
                successful_actions[action] += 1
                
        if not successful_actions:
            return 'wait'
            
        return max(successful_actions.items(), key=lambda x: x[1])[0]

    def _calculate_confidence(self, pattern: LearningPattern) -> float:
        # Consider pattern effectiveness and number of observations
        n_observations = len(pattern.outcomes)
        
        if n_observations < 10:
            confidence_penalty = 0.5  # Low confidence for few observations
        elif n_observations < 50:
            confidence_penalty = 0.2
        else:
            confidence_penalty = 0
            
        return max(0, pattern.effectiveness - confidence_penalty)

    def _are_conditions_similar(
        self,
        conditions1: Dict[str, Any],
        conditions2: Dict[str, Any]
    ) -> bool:
        similarity = self._calculate_condition_similarity(conditions1, conditions2)
        return similarity > 0.8

    def _deprecate_pattern(self, pattern_id: str) -> None:
        if pattern_id in self.patterns:
            self.logger.info(f"Deprecating ineffective pattern: {pattern_id}")
            del self.patterns[pattern_id]

    def _evolve_decision_weights(self, trading_results: Dict[str, Any]) -> None:
        for strategy, trades in self._group_trades_by_strategy(trading_results).items():
            success_rate = self._calculate_strategy_success_rate(trades)
            
            # Update strategy effectiveness using exponential moving average
            current_effectiveness = self.strategy_effectiveness[strategy]
            self.strategy_effectiveness[strategy] = (
                current_effectiveness * (1 - self.learning_rate) +
                success_rate * self.learning_rate
            )

    def _group_trades_by_strategy(
        self,
        trading_results: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        grouped_trades = defaultdict(list)
        
        for trade in trading_results.get('trades', []):
            strategy = trade.get('strategy', 'unknown')
            grouped_trades[strategy].append(trade)
            
        return grouped_trades

    def _calculate_strategy_success_rate(
        self,
        trades: List[Dict[str, Any]]
    ) -> float:
        if not trades:
            return 0.0
            
        successful_trades = sum(1 for trade in trades if trade.get('success'))
        return successful_trades / len(trades)

    def _generate_pattern_id(self, pattern: Dict[str, Any]) -> str:
        # Create unique identifier for pattern
        pattern_str = f"{pattern['type']}_{sorted(pattern.items())}"
        return str(abs(hash(pattern_str)))