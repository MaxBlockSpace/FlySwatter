import logging
from typing import Dict, Any, List
from datetime import datetime

class AlertManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.monitoring.alerts')
        self.alerts: List[Dict[str, Any]] = []

    async def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            new_alerts = []
            
            # Check system metrics
            system_alerts = self._check_system_metrics(metrics.get('system', {}))
            if system_alerts:
                new_alerts.extend(system_alerts)

            # Check trading metrics
            trading_alerts = self._check_trading_metrics(metrics.get('trading', {}))
            if trading_alerts:
                new_alerts.extend(trading_alerts)

            # Check performance metrics
            performance_alerts = self._check_performance_metrics(
                metrics.get('performance', {})
            )
            if performance_alerts:
                new_alerts.extend(performance_alerts)

            # Store new alerts
            self.alerts.extend(new_alerts)
            return new_alerts

        except Exception as e:
            self.logger.error(f"Alert check failed: {e}")
            return []

    def _check_system_metrics(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        alerts = []
        
        # Check CPU usage
        if metrics.get('cpu_usage', 0) > 80:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'message': 'High CPU usage',
                'timestamp': datetime.now().isoformat()
            })

        # Check memory usage
        if metrics.get('memory_usage', 0) > 80:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'message': 'High memory usage',
                'timestamp': datetime.now().isoformat()
            })

        return alerts

    def _check_trading_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        
        # Check error rate
        if metrics.get('error_rate', 0) > 0.1:
            alerts.append({
                'type': 'trading',
                'level': 'error',
                'message': 'High trade error rate',
                'timestamp': datetime.now().isoformat()
            })

        # Check failed orders
        orders = metrics.get('orders', {})
        if orders.get('failed', 0) > orders.get('successful', 0):
            alerts.append({
                'type': 'trading',
                'level': 'error',
                'message': 'High order failure rate',
                'timestamp': datetime.now().isoformat()
            })

        return alerts

    def _check_performance_metrics(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        alerts = []
        
        # Check latency
        if metrics.get('latency', 0) > 1000:  # 1 second
            alerts.append({
                'type': 'performance',
                'level': 'warning',
                'message': 'High latency detected',
                'timestamp': datetime.now().isoformat()
            })

        # Check throughput
        if metrics.get('throughput', 0) < 1:  # Less than 1 trade per second
            alerts.append({
                'type': 'performance',
                'level': 'warning',
                'message': 'Low throughput detected',
                'timestamp': datetime.now().isoformat()
            })

        return alerts

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self.alerts

    def clear_alerts(self) -> None:
        self.alerts = []