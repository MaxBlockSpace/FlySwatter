import logging
from typing import Dict, Any, List
from datetime import datetime

class DecisionEngine:
    def __init__(self, adaptive_learner):
        self.logger = logging.getLogger('ai_trading_bot.analysis.decision')
        self.adaptive_learner = adaptive_learner
        self.decision_weights = {
            'market_score': 0.3,
            'sentiment_score': 0.2,
            'manipulation_score': 0.2,
            'learned_patterns': 0.3
        }

    async def make_decisions(
        self,
        market_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        manipulation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        try:
            decisions = []
            
            # Get learned adaptations
            learning_results = await self.adaptive_learner.analyze_and_adapt(
                market_data,
                self.last_trading_results,
                manipulation_data
            )
            
            # Adjust weights based on strategy effectiveness
            self._adjust_weights(learning_results['effectiveness'])
            
            # Consider learned patterns in decision making
            pattern_score = self._evaluate_patterns(learning_results['new_patterns'])
            
            # Calculate weighted scores
            market_score = self._evaluate_market(market_data) * self.decision_weights['market_score']
            sentiment_score = self._evaluate_sentiment(sentiment_data) * self.decision_weights['sentiment_score']
            manipulation_risk = manipulation_data['manipulation_score'] * self.decision_weights['manipulation_score']
            pattern_influence = pattern_score * self.decision_weights['learned_patterns']
            
            # Combine scores
            total_score = market_score + sentiment_score - manipulation_risk + pattern_influence
            
            if self._should_trade(total_score):
                decision = self._create_trade_decision(
                    market_data,
                    total_score,
                    learning_results['adaptations']
                )
                decisions.append(decision)

            return decisions

        except Exception as e:
            self.logger.error(f"Decision making failed: {e}")
            return []

    def _adjust_weights(self, strategy_effectiveness: Dict[str, float]) -> None:
        # Dynamically adjust decision weights based on strategy performance
        total_effectiveness = sum(strategy_effectiveness.values())
        if total_effectiveness > 0:
            for strategy, effectiveness in strategy_effectiveness.items():
                if strategy in self.decision_weights:
                    self.decision_weights[strategy] = effectiveness / total_effectiveness

    def _evaluate_patterns(self, patterns: List[Dict[str, Any]]) -> float:
        if not patterns:
            return 0.0
            
        pattern_scores = []
        for pattern in patterns:
            if pattern['type'] == 'price_pattern':
                score = self._evaluate_price_pattern(pattern)
            elif pattern['type'] == 'volume_pattern':
                score = self._evaluate_volume_pattern(pattern)
            elif pattern['type'] == 'order_pattern':
                score = self._evaluate_order_pattern(pattern)
            else:
                score = 0.5  # Neutral score for unknown patterns
                
            pattern_scores.append(score)
            
        return float(np.mean(pattern_scores))

    def _evaluate_price_pattern(self, pattern: Dict[str, Any]) -> float:
        direction_score = 1.0 if pattern['direction'] == 'up' else 0.0
        volatility_penalty = min(pattern['volatility'], 1.0)
        return max(0, direction_score - volatility_penalty * 0.5)

    def _evaluate_volume_pattern(self, pattern: Dict[str, Any]) -> float:
        trend_score = 1.0 if pattern['trend'] == 'increasing' else 0.0
        volatility_penalty = min(pattern['volatility'], 1.0)
        return max(0, trend_score - volatility_penalty * 0.3)

    def _evaluate_order_pattern(self, pattern: Dict[str, Any]) -> float:
        imbalance = pattern['imbalance']
        buy_pressure = pattern['buy_pressure']
        
        if buy_pressure > 0.6:  # Strong buying pressure
            return min(1.0, buy_pressure + imbalance)
        elif buy_pressure < 0.4:  # Strong selling pressure
            return max(0.0, buy_pressure - imbalance)
        return 0.5  # Neutral pressure

    def _create_trade_decision(
        self,
        market_data: Dict[str, Any],
        score: float,
        adaptations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        decision = {
            'timestamp': datetime.now().isoformat(),
            'action': 'buy' if score > 0.7 else 'sell',
            'confidence': score,
            'adaptations_applied': [
                adaptation['pattern_id']
                for adaptation in adaptations
                if adaptation['confidence'] > 0.7
            ]
        }

        # Add protection measures
        decision['protection_measures'] = self._determine_protection_measures(
            score,
            adaptations
        )

        return decision

    def _determine_protection_measures(
        self,
        score: float,
        adaptations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        measures = {
            'confirmation_blocks': 1,
            'slippage_tolerance': 0.01,
            'timeout': 300
        }
        
        # Adjust based on confidence
        if score < 0.6:
            measures['confirmation_blocks'] += 1
            measures['slippage_tolerance'] *= 0.5
            
        # Consider pattern-specific protections
        for adaptation in adaptations:
            if adaptation['confidence'] > 0.8:
                pattern_measures = self._get_pattern_protection_measures(adaptation)
                measures = self._merge_protection_measures(measures, pattern_measures)
                
        return measures

    def _get_pattern_protection_measures(
        self,
        adaptation: Dict[str, Any]
    ) -> Dict[str, Any]:
        pattern_type = adaptation['type']
        
        if pattern_type == 'price_pattern':
            return {
                'confirmation_blocks': 2,
                'slippage_tolerance': 0.02
            }
        elif pattern_type == 'volume_pattern':
            return {
                'timeout': 600,
                'slippage_tolerance': 0.015
            }
        elif pattern_type == 'order_pattern':
            return {
                'confirmation_blocks': 3,
                'timeout': 450
            }
            
        return {}

    def _merge_protection_measures(
        self,
        base_measures: Dict[str, Any],
        new_measures: Dict[str, Any]
    ) -> Dict[str, Any]:
        merged = base_measures.copy()
        
        # Take the more conservative value for each measure
        for key, value in new_measures.items():
            if key in merged:
                if key in ['confirmation_blocks', 'timeout']:
                    merged[key] = max(merged[key], value)
                elif key == 'slippage_tolerance':
                    merged[key] = min(merged[key], value)
                    
        return merged