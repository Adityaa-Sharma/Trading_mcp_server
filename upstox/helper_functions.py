import os
import httpx
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


async def place_order(
    instrument_token: str,
    quantity: int,
    transaction_type: str,  # 'BUY' or 'SELL'
    order_type: str = "MARKET",  # Default to MARKET for simplicity
    price: float = 0,  # Default price to 0
    product: str = "I",  # Intraday
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
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()


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


# async def search_instruments(query: str) -> Dict[str, Any]:
#     """Search for instruments"""
#     url = f"{API_BASE_URL}/search/instruments"

#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#     }

#     params = {"query": query}

    # async with httpx.AsyncClient() as client:
    #     response = await client.get(url, headers=headers, params=params)
    #     response.raise_for_status()
    #     return response.json()
