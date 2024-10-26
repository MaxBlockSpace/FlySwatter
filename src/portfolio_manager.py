import logging
import json
from datetime import datetime

class PortfolioManager:
    def __init__(self):
        self.logger = logging.getLogger('ai_trading_bot.portfolio')
        self.portfolio = {}
        self.history = []
        
    def load_portfolio(self, context):
        try:
            self.portfolio = context.get_portfolio()
            self.history = context.get_portfolio_history()
        except Exception as e:
            self.logger.error(f"Failed to load portfolio: {e}")
            
    def assess_portfolio(self, market_data, sentiment_data):
        assessment = {
            'timestamp': datetime.now().isoformat(),
            'holdings': self.portfolio.copy(),
            'recommendations': []
        }
        
        for asset, position in self.portfolio.items():
            risk_score = self._calculate_risk_score(asset, market_data, sentiment_data)
            profit_loss = self._calculate_profit_loss(asset, position, market_data)
            
            if risk_score > 0.8:
                assessment['recommendations'].append({
                    'asset': asset,
                    'action': 'reduce_position',
                    'reason': 'high_risk'
                })
            elif profit_loss > 20:
                assessment['recommendations'].append({
                    'asset': asset,
                    'action': 'take_profit',
                    'reason': 'profit_target_reached'
                })
                
        self.history.append(assessment)
        return assessment
        
    def update_position(self, asset, amount, price, action):
        timestamp = datetime.now().isoformat()
        
        if action == 'buy':
            if asset not in self.portfolio:
                self.portfolio[asset] = {
                    'amount': amount,
                    'average_price': price
                }
            else:
                current = self.portfolio[asset]
                total_amount = current['amount'] + amount
                total_cost = (current['amount'] * current['average_price']) + (amount * price)
                self.portfolio[asset] = {
                    'amount': total_amount,
                    'average_price': total_cost / total_amount
                }
        elif action == 'sell':
            if asset in self.portfolio:
                current = self.portfolio[asset]
                if amount >= current['amount']:
                    del self.portfolio[asset]
                else:
                    self.portfolio[asset]['amount'] -= amount
                    
        self._record_transaction(asset, amount, price, action, timestamp)
        
    def get_position(self, asset):
        return self.portfolio.get(asset)
        
    def get_total_value(self, market_data):
        total = 0
        for asset, position in self.portfolio.items():
            if asset in market_data:
                total += position['amount'] * market_data[asset]['price']
        return total
        
    def _calculate_risk_score(self, asset, market_data, sentiment_data):
        # Implement risk scoring logic
        return 0.5  # Placeholder
        
    def _calculate_profit_loss(self, asset, position, market_data):
        if asset not in market_data:
            return 0
            
        current_price = market_data[asset]['price']
        cost_basis = position['amount'] * position['average_price']
        current_value = position['amount'] * current_price
        
        return ((current_value - cost_basis) / cost_basis) * 100
        
    def _record_transaction(self, asset, amount, price, action, timestamp):
        transaction = {
            'timestamp': timestamp,
            'asset': asset,
            'amount': amount,
            'price': price,
            'action': action
        }
        self.history.append(transaction)