import logging
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

class PatternRecognizer:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.learning.pattern')
        self.known_patterns = {}
        self.pattern_history = []

    async def analyze_patterns(
        self,
        market_data: Dict[str, Any],
        manipulation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            # Identify market patterns
            market_patterns = self._identify_market_patterns(market_data)
            
            # Identify manipulation patterns
            manipulation_patterns = self._identify_manipulation_patterns(
                manipulation_data
            )
            
            # Update pattern history
            self._update_pattern_history(market_patterns, manipulation_patterns)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'market_patterns': market_patterns,
                'manipulation_patterns': manipulation_patterns,
                'pattern_evolution': self._analyze_pattern_evolution()
            }
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return {}

    def _identify_market_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        patterns = []
        
        # Price patterns
        if price_pattern := self._analyze_price_pattern(data):
            patterns.append(price_pattern)
            
        # Volume patterns
        if volume_pattern := self._analyze_volume_pattern(data):
            patterns.append(volume_pattern)
            
        # Order patterns
        if order_pattern := self._analyze_order_pattern(data):
            patterns.append(order_pattern)
            
        return patterns

    def _identify_manipulation_patterns(
        self,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        patterns = []
        
        # Floor sweep patterns
        if sweep_pattern := self._analyze_sweep_pattern(data):
            patterns.append(sweep_pattern)
            
        # Wash trading patterns
        if wash_pattern := self._analyze_wash_pattern(data):
            patterns.append(wash_pattern)
            
        # RBF patterns
        if rbf_pattern := self._analyze_rbf_pattern(data):
            patterns.append(rbf_pattern)
            
        return patterns

    def _analyze_price_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prices = data.get('prices', [])
            if len(prices) < 10:
                return None
                
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns)
            trend = np.mean(returns)
            
            return {
                'type': 'price',
                'volatility': float(volatility),
                'trend': float(trend),
                'confidence': self._calculate_confidence(len(prices))
            }
        except Exception as e:
            self.logger.error(f"Price pattern analysis failed: {e}")
            return None

    def _analyze_volume_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            volumes = data.get('volumes', [])
            if len(volumes) < 10:
                return None
                
            vol_changes = np.diff(volumes)
            vol_trend = np.mean(vol_changes)
            vol_volatility = np.std(vol_changes)
            
            return {
                'type': 'volume',
                'trend': float(vol_trend),
                'volatility': float(vol_volatility),
                'confidence': self._calculate_confidence(len(volumes))
            }
        except Exception as e:
            self.logger.error(f"Volume pattern analysis failed: {e}")
            return None

    def _analyze_order_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            orders = data.get('orders', [])
            if len(orders) < 10:
                return None
                
            buy_ratio = sum(1 for o in orders if o['side'] == 'buy') / len(orders)
            
            return {
                'type': 'order',
                'buy_pressure': float(buy_ratio),
                'sell_pressure': float(1 - buy_ratio),
                'confidence': self._calculate_confidence(len(orders))
            }
        except Exception as e:
            self.logger.error(f"Order pattern analysis failed: {e}")
            return None

    def _analyze_sweep_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            sweeps = data.get('floor_sweeps', [])
            if not sweeps:
                return None
                
            return {
                'type': 'floor_sweep',
                'frequency': len(sweeps),
                'average_size': float(np.mean([s['size'] for s in sweeps])),
                'confidence': self._calculate_confidence(len(sweeps))
            }
        except Exception as e:
            self.logger.error(f"Sweep pattern analysis failed: {e}")
            return None

    def _analyze_wash_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            wash_trades = data.get('wash_trades', [])
            if not wash_trades:
                return None
                
            return {
                'type': 'wash_trading',
                'frequency': len(wash_trades),
                'volume_ratio': float(
                    sum(t['volume'] for t in wash_trades) /
                    data.get('total_volume', 1)
                ),
                'confidence': self._calculate_confidence(len(wash_trades))
            }
        except Exception as e:
            self.logger.error(f"Wash pattern analysis failed: {e}")
            return None

    def _analyze_rbf_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            rbf_events = data.get('rbf_events', [])
            if not rbf_events:
                return None
                
            return {
                'type': 'rbf',
                'frequency': len(rbf_events),
                'average_fee_increase': float(
                    np.mean([e['fee_increase'] for e in rbf_events])
                ),
                'confidence': self._calculate_confidence(len(rbf_events))
            }
        except Exception as e:
            self.logger.error(f"RBF pattern analysis failed: {e}")
            return None

    def _calculate_confidence(self, sample_size: int) -> float:
        # More samples = higher confidence, up to a point
        return min(sample_size / 100, 1.0)

    def _update_pattern_history(
        self,
        market_patterns: List[Dict[str, Any]],
        manipulation_patterns: List[Dict[str, Any]]
    ) -> None:
        self.pattern_history.append({
            'timestamp': datetime.now().isoformat(),
            'market_patterns': market_patterns,
            'manipulation_patterns': manipulation_patterns
        })
        
        # Keep last 1000 patterns
        if len(self.pattern_history) > 1000:
            self.pattern_history = self.pattern_history[-1000:]

    def _analyze_pattern_evolution(self) -> Dict[str, Any]:
        if len(self.pattern_history) < 2:
            return {}
            
        try:
            # Analyze how patterns have changed over time
            changes = {
                'market': self._calculate_pattern_changes(
                    [p['market_patterns'] for p in self.pattern_history]
                ),
                'manipulation': self._calculate_pattern_changes(
                    [p['manipulation_patterns'] for p in self.pattern_history]
                )
            }
            
            return {
                'changes': changes,
                'trend': self._determine_pattern_trend(changes)
            }
        except Exception as e:
            self.logger.error(f"Pattern evolution analysis failed: {e}")
            return {}

    def _calculate_pattern_changes(
        self,
        pattern_sequence: List[List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        changes = {}
        
        for pattern_type in ['price', 'volume', 'order', 'floor_sweep', 'wash_trading', 'rbf']:
            type_patterns = [
                [p for p in patterns if p['type'] == pattern_type]
                for patterns in pattern_sequence
            ]
            
            if all(type_patterns):
                changes[pattern_type] = self._calculate_type_change(type_patterns)
                
        return changes

    def _calculate_type_change(
        self,
        type_patterns: List[List[Dict[str, Any]]]
    ) -> float:
        # Calculate rate of change for pattern metrics
        changes = []
        
        for i in range(1, len(type_patterns)):
            prev = type_patterns[i-1][0]
            curr = type_patterns[i][0]
            
            for key in prev:
                if isinstance(prev[key], (int, float)):
                    change = (curr[key] - prev[key]) / prev[key] if prev[key] != 0 else 0
                    changes.append(change)
                    
        return float(np.mean(changes)) if changes else 0

    def _determine_pattern_trend(self, changes: Dict[str, Dict[str, float]]) -> str:
        # Analyze overall trend direction
        market_change = np.mean(list(changes['market'].values()))
        manipulation_change = np.mean(list(changes['manipulation'].values()))
        
        if manipulation_change > 0.1:
            return 'increasing_manipulation'
        elif manipulation_change < -0.1:
            return 'decreasing_manipulation'
        else:
            return 'stable'