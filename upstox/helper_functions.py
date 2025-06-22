import os
import httpx
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("UPSTOCKS_API_KEY")
API_SECRET = os.getenv("UPSTOCKS_API_SECRET")
ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")

if not API_KEY or not API_SECRET:
    raise ValueError(
        "UPSTOCKS_API_KEY and UPSTOCKS_API_SECRET environment variables required"
    )

API_BASE_URL = "https://api.upstox.com/v2"

# Common NSE instrument tokens mapping
INSTRUMENT_TOKENS = {
    "RELIANCE": "NSE_EQ|INE002A01018",
    "TCS": "NSE_EQ|INE467B01029", 
    "ITC": "NSE_EQ|INE154A01025",
    "HDFC": "NSE_EQ|INE040A01034",
    "INFY": "NSE_EQ|INE009A01021",
    "HDFCBANK": "NSE_EQ|INE040A01026",
    "ICICIBANK": "NSE_EQ|INE090A01021",
    "SBIN": "NSE_EQ|INE062A01020",
    "BHARTIARTL": "NSE_EQ|INE397D01024",
    "KOTAKBANK": "NSE_EQ|INE237A01028"
}

def get_instrument_token(symbol: str) -> str:
    """Get instrument token for a symbol"""
    symbol_upper = symbol.upper()
    if symbol_upper in INSTRUMENT_TOKENS:
        return INSTRUMENT_TOKENS[symbol_upper]
    else:
        # Default format for NSE stocks
        return f"NSE_EQ|{symbol_upper}"

async def place_order(
    instrument_token: str,
    quantity: int,
    transaction_type: str,  # 'BUY' or 'SELL'
    order_type: str = "MARKET",  # Default to MARKET for simplicity
    price: float = 0,  # Default price to 0
    product: str = "D",  # Intraday
    validity: str = "DAY",
    is_amo: bool = False,
    tag: str = "mcp_order",
) -> Dict[str, Any]:
    """Place an order on Upstox platform"""
    url = f"{API_BASE_URL}/order/place"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    # For MARKET orders, price should be 0
    if order_type == "MARKET":
        price = 0
    
    data = {
        "quantity": quantity,
        "product": product,
        "validity": validity,
        "tag": tag,
        "instrument_token": instrument_token,
        "order_type": order_type,
        "transaction_type": transaction_type,
        "disclosed_quantity": 0,
        "trigger_price": 0,
        "is_amo": is_amo,
        "price": price,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            
            # Debug: Print response details
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Text: {response.text}")
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
            if not response.text.strip():
                return {
                    "status": "error", 
                    "message": "Empty response from server",
                    "data": None
                }
                
            return response.json()
            
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"Invalid JSON response: {str(e)}. Response: {response.text}",
                "data": None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Request failed: {str(e)}",
                "data": None
            }

async def cancel_order(order_id: str) -> Dict[str, Any]:
    """Cancel an order by order ID"""
    url = f"{API_BASE_URL}/order/cancel"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json", 
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    
    data = {"order_id": order_id}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, json=data, headers=headers)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
            return response.json()
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Cancel order failed: {str(e)}",
                "data": None
            }

async def get_order_book() -> Dict[str, Any]:
    """Get order book"""
    url = f"{API_BASE_URL}/order/retrieve-all"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Get order book failed: {str(e)}",
                "data": None
            }

async def get_order_status(order_id: str) -> Dict[str, Any]:
    """Get order status by order ID"""
    url = f"{API_BASE_URL}/order/details"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    
    params = {"order_id": order_id}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Get order status failed: {str(e)}",
                "data": None
            }

async def get_portfolio() -> Dict[str, Any]:
    """Get portfolio holdings"""
    url = f"{API_BASE_URL}/portfolio/long-term-holdings"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def get_funds() -> Dict[str, Any]:
    """Get account funds and margins"""
    url = f"{API_BASE_URL}/user/get-funds-and-margin"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def search_instruments(query: str) -> Dict[str, Any]:
    """Search for instruments"""
    url = f"{API_BASE_URL}/search/instruments"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    params = {"query": query}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
