import os
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("UPSTOCKS_API_KEY")
API_SECRET = os.getenv("UPSTOCKS_API_SECRET")
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")  # You'll need to set this after OAuth

if not API_KEY or not API_SECRET:
    raise ValueError("UPSTOCKS_API_KEY and UPSTOCKS_API_SECRET environment variables required")

API_BASE_URL = "https://api.upstox.com/v2"

async def place_order(
    instrument_token: str,
    quantity: int,
    transaction_type: str,  # 'BUY' or 'SELL'
    order_type: str = "MARKET",  # 'MARKET', 'LIMIT', 'SL', 'SL-M'
    product: str = "D",  # 'D' for Delivery, 'I' for Intraday, 'M' for Margin
    price: float = 0,
    trigger_price: float = 0,
    validity: str = "DAY",
    disclosed_quantity: int = 0,
    is_amo: bool = False,
    tag: str = "mcp_order"
) -> Dict[str, Any]:
    """
    Place an order on Upstox platform
    
    Args:
        instrument_token: Instrument token (e.g., 'NSE_EQ|INE669E01016')
        quantity: Number of shares
        transaction_type: 'BUY' or 'SELL'
        order_type: Order type (MARKET, LIMIT, SL, SL-M)
        product: Product type (D, I, M)
        price: Price for limit orders
        trigger_price: Trigger price for stop loss orders
        validity: Order validity (DAY, IOC)
        disclosed_quantity: Disclosed quantity
        is_amo: After Market Order flag
        tag: Order tag
    
    Returns:
        Order response dictionary
    """
    url = f"{API_BASE_URL}/order/place"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    data = {
        'quantity': quantity,
        'product': product,
        'validity': validity,
        'price': price,
        'tag': tag,
        'instrument_token': instrument_token,
        'order_type': order_type,
        'transaction_type': transaction_type,
        'disclosed_quantity': disclosed_quantity,
        'trigger_price': trigger_price,
        'is_amo': is_amo,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

async def modify_order(
    order_id: str,
    quantity: Optional[int] = None,
    price: Optional[float] = None,
    order_type: Optional[str] = None,
    validity: Optional[str] = None,
    disclosed_quantity: Optional[int] = None,
    trigger_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Modify an existing order
    
    Args:
        order_id: Order ID to modify
        quantity: New quantity
        price: New price
        order_type: New order type
        validity: New validity
        disclosed_quantity: New disclosed quantity
        trigger_price: New trigger price
    
    Returns:
        Modification response dictionary
    """
    url = f"{API_BASE_URL}/order/modify"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    data = {'order_id': order_id}
    if quantity is not None:
        data['quantity'] = quantity
    if price is not None:
        data['price'] = price
    if order_type is not None:
        data['order_type'] = order_type
    if validity is not None:
        data['validity'] = validity
    if disclosed_quantity is not None:
        data['disclosed_quantity'] = disclosed_quantity
    if trigger_price is not None:
        data['trigger_price'] = trigger_price
    
    async with httpx.AsyncClient() as client:
        response = await client.put(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

async def cancel_order(order_id: str) -> Dict[str, Any]:
    """
    Cancel an existing order
    
    Args:
        order_id: Order ID to cancel
    
    Returns:
        Cancellation response dictionary
    """
    url = f"{API_BASE_URL}/order/cancel"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    data = {'order_id': order_id}
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_order_book() -> Dict[str, Any]:
    """
    Get order book (all orders)
    
    Returns:
        Order book data
    """
    url = f"{API_BASE_URL}/order/retrieve-all"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_order_details(order_id: str) -> Dict[str, Any]:
    """
    Get details of a specific order
    
    Args:
        order_id: Order ID
    
    Returns:
        Order details
    """
    url = f"{API_BASE_URL}/order/details"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    params = {'order_id': order_id}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

async def get_portfolio() -> Dict[str, Any]:
    """
    Get portfolio holdings
    
    Returns:
        Portfolio data
    """
    url = f"{API_BASE_URL}/portfolio/long-term-holdings"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_positions() -> Dict[str, Any]:
    """
    Get current positions
    
    Returns:
        Positions data
    """
    url = f"{API_BASE_URL}/portfolio/short-term-positions"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_funds() -> Dict[str, Any]:
    """
    Get account funds and margins
    
    Returns:
        Funds data
    """
    url = f"{API_BASE_URL}/user/get-funds-and-margin"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_profile() -> Dict[str, Any]:
    """
    Get user profile
    
    Returns:
        Profile data
    """
    url = f"{API_BASE_URL}/user/profile"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

async def search_instruments(query: str) -> Dict[str, Any]:
    """
    Search for instruments
    
    Args:
        query: Search query (e.g., 'RELIANCE', 'TCS')
    
    Returns:
        Search results
    """
    url = f"{API_BASE_URL}/search/instruments"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    params = {'query': query}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

async def get_market_quotes(instruments: List[str]) -> Dict[str, Any]:
    """
    Get market quotes for instruments
    
    Args:
        instruments: List of instrument tokens
    
    Returns:
        Market quotes data
    """
    url = f"{API_BASE_URL}/market-quote/quotes"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    
    params = {'instrument_key': ','.join(instruments)}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()



