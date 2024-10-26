import logging
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

class ManipulationDetector:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.analysis.manipulation')
        self.known_patterns = {
            'floor_sweep': {
                'indicators': ['sudden_volume_spike', 'quick_cancellation'],
                'weight': 0.8
            },
            'wash_trading': {
                'indicators': ['circular_trades', 'self_trading'],
                'weight': 0.9
            },
            'rbf_manipulation': {
                'indicators': ['replace_by_fee', 'transaction_replacement'],
                'weight': 0.7
            }
        }

    async def detect_manipulation(
        self,
        market_data: Dict[str, Any],
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            floor_sweep = self._detect_floor_sweep(market_data, order_data)
            wash_trading = self._detect_wash_trading(market_data)
            rbf_manipulation = self._detect_rbf_manipulation(order_data)

            risk_score = self._calculate_risk_score([
                floor_sweep,
                wash_trading,
                rbf_manipulation
            ])

            return {
                'timestamp': datetime.now().isoformat(),
                'risk_score': risk_score,
                'detections': {
                    'floor_sweep': floor_sweep,
                    'wash_trading': wash_trading,
                    'rbf_manipulation': rbf_manipulation
                }
            }
        except Exception as e:
            self.logger.error(f"Manipulation detection failed: {e}")
            return {}

    def _detect_floor_sweep(
        self,
        market_data: Dict[str, Any],
        order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            # Check for sudden large orders
            orders = order_data.get('orders', [])
            volumes = [order['volume'] for order in orders]
            mean_vol = np.mean(volumes) if volumes else 0
            std_vol = np.std(volumes) if volumes else 0

            suspicious_orders = []
            for order in orders:
                # Check for orders significantly larger than average
                if order['volume'] > mean_vol + (3 * std_vol):
                    # Check if order was quickly cancelled
                    if order.get('cancelled_at'):
                        time_diff = (
                            datetime.fromisoformat(order['cancelled_at']) -
                            datetime.fromisoformat(order['created_at'])
                        ).total_seconds()
                        if time_diff < 60:  # Less than 1 minute
                            suspicious_orders.append(order)

            return {
                'detected': len(suspicious_orders) > 0,
                'confidence': min(len(suspicious_orders) * 0.2, 1.0),
                'suspicious_orders': suspicious_orders
            }
        except Exception as e:
            self.logger.error(f"Floor sweep detection failed: {e}")
            return {'detected': False, 'confidence': 0}

    def _detect_wash_trading(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            trades = market_data.get('trades', [])
            suspicious_trades = []
            addresses = set()

            for trade in trades:
                # Check for circular trading
                if trade['buyer'] in addresses and trade['seller'] in addresses:
                    suspicious_trades.append(trade)
                addresses.add(trade['buyer'])
                addresses.add(trade['seller'])

            return {
                'detected': len(suspicious_trades) > 0,
                'confidence': min(len(suspicious_trades) * 0.2, 1.0),
                'suspicious_trades': suspicious_trades
            }
        except Exception as e:
            self.logger.error(f"Wash trading detection failed: {e}")
            return {'detected': False, 'confidence': 0}

    def _detect_rbf_manipulation(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            transactions = order_data.get('transactions', [])
            suspicious_txs = []

            for tx in transactions:
                if tx.get('rbf_enabled'):
                    # Check for rapid replacements
                    replacements = tx.get('replacements', [])
                    if len(replacements) > 2:  # Multiple replacements
                        suspicious_txs.append({
                            'tx_id': tx['id'],
                            'replacements': len(replacements),
                            'fee_increase': tx.get('fee_increase', 0)
                        })

            return {
                'detected': len(suspicious_txs) > 0,
                'confidence': min(len(suspicious_txs) * 0.2, 1.0),
                'suspicious_transactions': suspicious_txs
            }
        except Exception as e:
            self.logger.error(f"RBF manipulation detection failed: {e}")
            return {'detected': False, 'confidence': 0}

    def _calculate_risk_score(self, detections: List[Dict[str, Any]]) -> float:
        try:
            total_score = 0
            total_weight = 0

            for detection, pattern in zip(detections, self.known_patterns.values()):
                if detection['detected']:
                    total_score += detection['confidence'] * pattern['weight']
                    total_weight += pattern['weight']

            return total_score / total_weight if total_weight > 0 else 0
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {e}")
            return 0