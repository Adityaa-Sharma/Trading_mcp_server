import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from upstox.helper_functions import (
    place_order, cancel_order, get_order_book, get_order_details,
    get_portfolio, get_positions, get_funds, get_profile, search_instruments,
    get_market_quotes
)

# Initialize FastMCP server
mcp = FastMCP("UpstoxTradingServer", "1.0.0")

@mcp.tool()
async def buy_stock(
    symbol: str,
    quantity: int,
    order_type: str = "MARKET",
    price: float = 0,
    product: str = "D",
    validity: str = "DAY"
) -> Dict[str, Any]:
    """
    Buy stocks on Upstox platform
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        quantity: Number of shares to buy
        order_type: Order type (MARKET, LIMIT, SL, SL-M)
        price: Price for limit orders
        product: Product type (D=Delivery, I=Intraday, M=Margin)
        validity: Order validity (DAY, IOC)
    
    Returns:
        Order placement response
    """
    try:
        # Search for instrument token
        search_result = await search_instruments(symbol)
        
        if not search_result.get('data') or len(search_result['data']) == 0:
            return {"error": f"Symbol {symbol} not found"}
        
        # Get the first matching instrument (NSE equity preferred)
        instrument = None
        for inst in search_result['data']:
            if inst.get('exchange') == 'NSE' and inst.get('segment') == 'EQ':
                instrument = inst
                break
        
        if not instrument:
            instrument = search_result['data'][0]  # Fallback to first result
        
        instrument_token = instrument['instrument_key']
        
        # Place buy order
        result = await place_order(
            instrument_token=instrument_token,
            quantity=quantity,
            transaction_type="BUY",
            order_type=order_type,
            product=product,
            price=price,
            validity=validity,
            is_amo=False
        )
        
        return {
            "status": "success",
            "action": "BUY",
            "symbol": symbol,
            "instrument_token": instrument_token,
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "timestamp": datetime.now().isoformat(),
            "order_response": result
        }
        
    except Exception as e:
        return {"error": f"Failed to place buy order for {symbol}: {str(e)}"}

@mcp.tool()
async def sell_stock(
    symbol: str,
    quantity: int,
    order_type: str = "MARKET",
    price: float = 0,
    product: str = "D",
    validity: str = "DAY"
) -> Dict[str, Any]:
    """
    Sell stocks on Upstox platform
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        quantity: Number of shares to sell
        order_type: Order type (MARKET, LIMIT, SL, SL-M)
        price: Price for limit orders
        product: Product type (D=Delivery, I=Intraday, M=Margin)
        validity: Order validity (DAY, IOC)
    
    Returns:
        Order placement response
    """
    try:
        # Search for instrument token
        search_result = await search_instruments(symbol)
        
        if not search_result.get('data') or len(search_result['data']) == 0:
            return {"error": f"Symbol {symbol} not found"}
        
        # Get the first matching instrument (NSE equity preferred)
        instrument = None
        for inst in search_result['data']:
            if inst.get('exchange') == 'NSE' and inst.get('segment') == 'EQ':
                instrument = inst
                break
        
        if not instrument:
            instrument = search_result['data'][0]  # Fallback to first result
        
        instrument_token = instrument['instrument_key']
        
        # Place sell order
        result = await place_order(
            instrument_token=instrument_token,
            quantity=quantity,
            transaction_type="SELL",
            order_type=order_type,
            product=product,
            price=price,
            validity=validity,
            is_amo=False
        )
        
        return {
            "status": "success",
            "action": "SELL",
            "symbol": symbol,
            "instrument_token": instrument_token,
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "timestamp": datetime.now().isoformat(),
            "order_response": result
        }
        
    except Exception as e:
        return {"error": f"Failed to place sell order for {symbol}: {str(e)}"}

@mcp.tool()
async def place_amo_order(
    symbol: str,
    quantity: int,
    transaction_type: str,
    order_type: str = "MARKET",
    price: float = 0,
    product: str = "D"
) -> Dict[str, Any]:
    """
    Place After Market Order (AMO) on Upstox platform
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        quantity: Number of shares
        transaction_type: 'BUY' or 'SELL'
        order_type: Order type (MARKET, LIMIT, SL, SL-M)
        price: Price for limit orders
        product: Product type (D=Delivery, I=Intraday, M=Margin)
    
    Returns:
        AMO placement response
    """
    try:
        # Search for instrument token
        search_result = await search_instruments(symbol)
        
        if not search_result.get('data') or len(search_result['data']) == 0:
            return {"error": f"Symbol {symbol} not found"}
        
        # Get the first matching instrument (NSE equity preferred)
        instrument = None
        for inst in search_result['data']:
            if inst.get('exchange') == 'NSE' and inst.get('segment') == 'EQ':
                instrument = inst
                break
        
        if not instrument:
            instrument = search_result['data'][0]  # Fallback to first result
        
        instrument_token = instrument['instrument_key']
        
        # Place AMO order
        result = await place_order(
            instrument_token=instrument_token,
            quantity=quantity,
            transaction_type=transaction_type.upper(),
            order_type=order_type,
            product=product,
            price=price,
            validity="DAY",
            is_amo=True,  # This makes it an After Market Order
            tag="AMO_order"
        )
        
        return {
            "status": "success",
            "action": f"AMO_{transaction_type.upper()}",
            "symbol": symbol,
            "instrument_token": instrument_token,
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "is_amo": True,
            "timestamp": datetime.now().isoformat(),
            "order_response": result
        }
        
    except Exception as e:
        return {"error": f"Failed to place AMO order for {symbol}: {str(e)}"}

@mcp.tool()
async def get_user_portfolio() -> Dict[str, Any]:
    """
    Get user's portfolio holdings and positions
    
    Returns:
        Complete portfolio data including holdings, positions, and funds
    """
    try:
        # Get all portfolio data
        holdings = await get_portfolio()
        positions = await get_positions()
        funds = await get_funds()
        profile = await get_profile()
        
        # Calculate portfolio summary
        total_value = 0
        total_pnl = 0
        
        if holdings.get('data'):
            for holding in holdings['data']:
                total_value += holding.get('current_value', 0)
                total_pnl += holding.get('pnl', 0)
        
        if positions.get('data'):
            for position in positions['data']:
                total_pnl += position.get('unrealised', 0)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_portfolio_value": round(total_value, 2),
                "total_pnl": round(total_pnl, 2),
                "available_margin": funds.get('data', {}).get('equity', {}).get('available_margin', 0) if funds.get('data') else 0
            },
            "holdings": holdings,
            "positions": positions,
            "funds": funds,
            "profile": profile
        }
        
    except Exception as e:
        return {"error": f"Failed to get portfolio data: {str(e)}"}

@mcp.tool()
async def get_order_status(order_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get order status - either specific order or all orders
    
    Args:
        order_id: Specific order ID (optional)
    
    Returns:
        Order status data
    """
    try:
        if order_id:
            # Get specific order details
            result = await get_order_details(order_id)
            return {
                "status": "success",
                "order_id": order_id,
                "timestamp": datetime.now().isoformat(),
                "order_details": result
            }
        else:
            # Get all orders
            result = await get_order_book()
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "order_book": result
            }
            
    except Exception as e:
        return {"error": f"Failed to get order status: {str(e)}"}

@mcp.tool()
async def cancel_order_by_id(order_id: str) -> Dict[str, Any]:
    """
    Cancel a specific order
    
    Args:
        order_id: Order ID to cancel
    
    Returns:
        Cancellation response
    """
    try:
        result = await cancel_order(order_id)
        
        return {
            "status": "success",
            "action": "CANCEL",
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "cancellation_response": result
        }
        
    except Exception as e:
        return {"error": f"Failed to cancel order {order_id}: {str(e)}"}

@mcp.tool()
async def get_market_data(symbols: List[str]) -> Dict[str, Any]:
    """
    Get market quotes for multiple symbols
    
    Args:
        symbols: List of stock symbols
    
    Returns:
        Market data for all symbols
    """
    try:
        # Get instrument tokens for all symbols
        instrument_tokens = []
        symbol_mapping = {}
        
        for symbol in symbols:
            search_result = await search_instruments(symbol)
            if search_result.get('data') and len(search_result['data']) > 0:
                # Prefer NSE equity
                instrument = None
                for inst in search_result['data']:
                    if inst.get('exchange') == 'NSE' and inst.get('segment') == 'EQ':
                        instrument = inst
                        break
                
                if not instrument:
                    instrument = search_result['data'][0]
                
                instrument_token = instrument['instrument_key']
                instrument_tokens.append(instrument_token)
                symbol_mapping[instrument_token] = symbol
        
        if not instrument_tokens:
            return {"error": "No valid instruments found"}
        
        # Get market quotes
        quotes_result = await get_market_quotes(instrument_tokens)
        
        # Format response
        market_data = {}
        if quotes_result.get('data'):
            for token, quote_data in quotes_result['data'].items():
                symbol = symbol_mapping.get(token, token)
                market_data[symbol] = {
                    "instrument_token": token,
                    "last_price": quote_data.get('last_price'),
                    "change": quote_data.get('net_change'),
                    "change_percent": quote_data.get('percentage_change'),
                    "volume": quote_data.get('volume'),
                    "high": quote_data.get('ohlc', {}).get('high'),
                    "low": quote_data.get('ohlc', {}).get('low'),
                    "open": quote_data.get('ohlc', {}).get('open'),
                    "close": quote_data.get('ohlc', {}).get('close')
                }
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "market_data": market_data
        }
        
    except Exception as e:
        return {"error": f"Failed to get market data: {str(e)}"}

if __name__ == "__main__":
    mcp.run()

