import logging
from typing import Dict, Any, Optional
from datetime import datetime
import hmac
import hashlib
import time
import aiohttp
from .base import BaseExchange

class BinanceExchange(BaseExchange):
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://testnet.binance.vision/api' if testnet else 'https://api.binance.com/api'
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self) -> None:
        self.session = aiohttp.ClientSession()
        self.logger.info("Connected to Binance")

    async def disconnect(self) -> None:
        if self.session:
            await self.session.close()
        self.logger.info("Disconnected from Binance")

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        query_string = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def _request(
        self,
        method: str,
        endpoint: str,
        signed: bool = False,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError("Session not initialized")

        url = f"{self.base_url}{endpoint}"
        headers = {'X-MBX-APIKEY': self.api_key}
        params = params or {}

        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)

        try:
            async with self.session.request(
                method,
                url,
                params=params,
                headers=headers
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Request failed: {error}")
                return await response.json()
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return await self._request('GET', '/v3/ticker/price', params={'symbol': symbol})

    async def get_orderbook(self, symbol: str) -> Dict[str, Any]:
        return await self._request('GET', '/v3/depth', params={'symbol': symbol, 'limit': 100})

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': amount
        }
        if price:
            params['price'] = price

        return await self._request('POST', '/v3/order', signed=True, params=params)

    async def cancel_order(self, order_id: str) -> bool:
        try:
            await self._request('DELETE', '/v3/order', signed=True, params={'orderId': order_id})
            return True
        except Exception:
            return False

    async def get_balance(self) -> Dict[str, float]:
        response = await self._request('GET', '/v3/account', signed=True)
        return {
            balance['asset']: float(balance['free'])
            for balance in response['balances']
            if float(balance['free']) > 0
        }

    async def get_position(self, symbol: str) -> Dict[str, Any]:
        response = await self._request(
            'GET',
            '/v3/openOrders',
            signed=True,
            params={'symbol': symbol}
        )
        return {
            'symbol': symbol,
            'orders': response
        }