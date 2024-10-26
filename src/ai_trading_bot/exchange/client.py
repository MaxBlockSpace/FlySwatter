import logging
import aiohttp
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from datetime import datetime

class ExchangeClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.logger = logging.getLogger('ai_trading_bot.exchange.client')
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        timestamp = int(time.time() * 1000)
        params['timestamp'] = timestamp
        
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError("Client session not initialized")

        url = f"{self.base_url}{endpoint}"
        headers = {'X-API-KEY': self.api_key}
        
        if signed:
            signature = self._generate_signature(params or {})
            headers['X-SIGNATURE'] = signature

        try:
            async with self.session.request(
                method,
                url,
                params=params,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Request failed: {error_text}")
                    
                return await response.json()
                
        except Exception as e:
            self.logger.error(f"Exchange request failed: {e}")
            raise

    async def get_order_book(self, symbol: str) -> Dict[str, Any]:
        return await self._request('GET', f'/orderbook/{symbol}')

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return await self._request('GET', f'/ticker/{symbol}')

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if price:
            params['price'] = price

        return await self._request('POST', '/order', params, signed=True)

    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return await self._request('DELETE', '/order', params, signed=True)

    async def get_account_info(self) -> Dict[str, Any]:
        return await self._request('GET', '/account', signed=True)

    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params['symbol'] = symbol
        return await self._request('GET', '/openOrders', params, signed=True)

    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return await self._request('GET', '/order', params, signed=True)