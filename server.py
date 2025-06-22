import asyncio
from datetime import datetime
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp import types
from mcp.server.models import InitializationOptions

# AlphaVantage imports
from alphavantage.helper_function import (
    fetch_quote,
    fetch_company_overview,
    fetch_top_gainer_losers,
    fetch_sma,
    fetch_daily_data,
)
from alphavantage.tools import AlphavantageTools

# Upstox imports
from upstox.helper_functions import (
    place_order,
    get_portfolio,
    get_funds,
    cancel_order,
    get_order_book,
    get_order_status,
    get_instrument_token,
)
from upstox.tools import UpstoxTools


def get_version() -> str:
    '''Get the version of the server.'''
    return "1.0.0"


# Create MCP server instance
server = Server("combined_trading_server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools from both AlphaVantage and Upstox."""
    return [
        # AlphaVantage Tools
        types.Tool(
            name=AlphavantageTools.STOCK_QUOTE.value,
            description="Get current stock quote from AlphaVantage",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "datatype": {
                        "type": "string",
                        "description": "Data type (json or csv)",
                        "default": "json",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.COMPANY_OVERVIEW.value,
            description="Get company overview from AlphaVantage",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.TOP_GAINERS_LOSERS.value,
            description="Get top gainers and losers from AlphaVantage",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AlphavantageTools.SMA.value,
            description="Get Simple Moving Average (SMA) data from AlphaVantage",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "interval": {
                        "type": "string",
                        "description": "Time interval (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)",
                    },
                    "time_period": {
                        "type": "integer",
                        "description": "Time period for SMA calculation",
                        "default": 20,
                    },
                    "series_type": {
                        "type": "string",
                        "description": "Price series type (close, open, high, low)",
                        "default": "close",
                    },
                    "datatype": {
                        "type": "string",
                        "description": "Data type (json or csv)",
                        "default": "json",
                    },
                },
                "required": ["symbol", "interval"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.INTRADAY.value,
            description="Get intraday stock data from AlphaVantage",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "interval": {
                        "type": "string",
                        "description": "Time interval (1min, 5min, 15min, 30min, 60min)",
                        "default": "60min",
                    },
                    "adjusted": {
                        "type": "boolean",
                        "description": "Adjusted data flag",
                        "default": True,
                    },
                    "outputsize": {
                        "type": "string",
                        "description": "Output size (compact or full)",
                        "default": "compact",
                    },
                    "datatype": {
                        "type": "string",
                        "description": "Data type (json or csv)",
                        "default": "json",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AlphavantageTools.DAILY_DATA.value,
            description="Get daily stock data from AlphaVantage",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "outputsize": {
                        "type": "string",
                        "description": "Output size (compact or full)",
                        "default": "compact",
                    },
                    "datatype": {
                        "type": "string",
                        "description": "Data type (json or csv)",
                        "default": "json",
                    },
                },
                "required": ["symbol"],
            },
        ),
        # Upstox Tools
        types.Tool(
            name=UpstoxTools.BUY_STOCK.value,
            description="Buy stocks on Upstox platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., RELIANCE, TCS,ITC)",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares to buy",
                    },
                },
                "required": ["symbol", "quantity"],
            },
        ),
        types.Tool(
            name=UpstoxTools.SELL_STOCK.value,
            description="Sell stocks on Upstox platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., RELIANCE, TCS)",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares to sell",
                    },
                },
                "required": ["symbol", "quantity"],
            },
        ),
        types.Tool(
            name=UpstoxTools.PLACE_AMO_ORDER.value,
            description="Place After Market Order on Upstox",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "quantity": {"type": "integer", "description": "Number of shares"},
                    "transaction_type": {
                        "type": "string",
                        "description": "BUY or SELL",
                    },
                    "order_type": {
                        "type": "string", 
                        "description": "MARKET or LIMIT",
                        "default": "MARKET"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price for LIMIT orders",
                        "default": 0
                    }
                },
                "required": ["symbol", "quantity", "transaction_type"],
            },
        ),
        types.Tool(
            name=UpstoxTools.GET_PORTFOLIO.value,
            description="Get portfolio holdings from Upstox",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=UpstoxTools.GET_FUNDS.value,
            description="Get account funds and margins from Upstox",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=UpstoxTools.CANCEL_ORDER_BY_ID.value,
            description="Cancel an order by order ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID to cancel"}
                },
                "required": ["order_id"],
            },
        ),
        types.Tool(
            name=UpstoxTools.GET_ORDER_STATUS.value,
            description="Get order status by order ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID to check"}
                },
                "required": ["order_id"],
            },
        ),
        types.Tool(
            name=UpstoxTools.GET_ORDER_BOOK.value,
            description="Get all orders from order book",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests for both AlphaVantage and Upstox."""
    try:
        # AlphaVantage Tools
        if name == AlphavantageTools.STOCK_QUOTE.value:
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Missing required argument: symbol")
            datatype = arguments.get("datatype", "json")
            result = await fetch_quote(symbol, datatype)

        elif name == AlphavantageTools.COMPANY_OVERVIEW.value:
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Missing required argument: symbol")
            result = await fetch_company_overview(symbol)

        elif name == AlphavantageTools.TOP_GAINERS_LOSERS.value:
            result = await fetch_top_gainer_losers()

        elif name == AlphavantageTools.SMA.value:
            symbol = arguments.get("symbol")
            interval = arguments.get("interval")
            if not symbol or not interval:
                raise ValueError("Missing required arguments: symbol, interval")

            time_period = arguments.get("time_period", 20)
            series_type = arguments.get("series_type", "close")
            datatype = arguments.get("datatype", "json")
            result = await fetch_sma(
                symbol, interval, time_period, series_type, datatype
            )

        elif name == AlphavantageTools.DAILY_DATA.value:
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Missing required argument: symbol")

            outputsize = arguments.get("outputsize", "compact")
            datatype = arguments.get("datatype", "json")
            result = await fetch_daily_data(symbol, outputsize, datatype)

        # Upstox Tools
        elif name == UpstoxTools.BUY_STOCK.value:
            symbol = arguments.get("symbol")
            quantity = arguments.get("quantity")
            if not symbol or not quantity:
                raise ValueError("Missing required arguments: symbol, quantity")

            # Get proper instrument token
            instrument_token = get_instrument_token(symbol)
            
            # Place buy order with MARKET type (no price needed)
            order_result = await place_order(
                instrument_token=instrument_token,
                quantity=quantity,
                transaction_type="BUY",
                order_type="MARKET",
                product="D",
                is_amo=False,
            )

            if order_result.get("status") == "error":
                result = {
                    "status": "error",
                    "message": order_result.get("message"),
                    "symbol": symbol,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "status": "success",
                    "action": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "order_type": "MARKET",
                    "timestamp": datetime.now().isoformat(),
                    "order_id": order_result.get("data", {}).get("order_id", "N/A"),
                    "full_response": order_result
                }

        elif name == UpstoxTools.SELL_STOCK.value:
            symbol = arguments.get("symbol")
            quantity = arguments.get("quantity")
            if not symbol or not quantity:
                raise ValueError("Missing required arguments: symbol, quantity")

            # Get proper instrument token
            instrument_token = get_instrument_token(symbol)
            
            # Place sell order with MARKET type (no price needed)
            order_result = await place_order(
                instrument_token=instrument_token,
                quantity=quantity,
                transaction_type="SELL",
                order_type="MARKET",
                product="I",
                is_amo=False,
            )

            if order_result.get("status") == "error":
                result = {
                    "status": "error",
                    "message": order_result.get("message"),
                    "symbol": symbol,
                    "quantity": quantity,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "status": "success",
                    "action": "SELL",
                    "symbol": symbol,
                    "quantity": quantity,
                    "order_type": "MARKET",
                    "timestamp": datetime.now().isoformat(),
                    "order_id": order_result.get("data", {}).get("order_id", "N/A"),
                    "full_response": order_result
                }

        elif name == UpstoxTools.PLACE_AMO_ORDER.value:
            symbol = arguments.get("symbol")
            quantity = arguments.get("quantity")
            transaction_type = arguments.get("transaction_type")
            order_type = arguments.get("order_type", "MARKET")
            price = arguments.get("price", 0)
            
            if not symbol or not quantity or not transaction_type:
                raise ValueError(
                    "Missing required arguments: symbol, quantity, transaction_type"
                )

            # Get proper instrument token
            instrument_token = get_instrument_token(symbol)
            
            # Place AMO order
            order_result = await place_order(
                instrument_token=instrument_token,
                quantity=quantity,
                transaction_type=transaction_type.upper(),
                order_type=order_type,
                price=price,
                product="I",
                is_amo=True,
            )

            if order_result.get("status") == "error":
                result = {
                    "status": "error",
                    "message": order_result.get("message"),
                    "symbol": symbol,
                    "quantity": quantity,
                    "transaction_type": transaction_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "status": "success",
                    "action": f"AMO_{transaction_type.upper()}",
                    "symbol": symbol,
                    "quantity": quantity,
                    "order_type": order_type,
                    "price": price,
                    "timestamp": datetime.now().isoformat(),
                    "order_id": order_result.get("data", {}).get("order_id", "N/A"),
                    "full_response": order_result
                }

        elif name == UpstoxTools.GET_PORTFOLIO.value:
            result = await get_portfolio()

        elif name == UpstoxTools.GET_FUNDS.value:
            result = await get_funds()

        elif name == UpstoxTools.CANCEL_ORDER_BY_ID.value:
            order_id = arguments.get("order_id")
            if not order_id:
                raise ValueError("Missing required argument: order_id")
            result = await cancel_order(order_id)

        elif name == UpstoxTools.GET_ORDER_STATUS.value:
            order_id = arguments.get("order_id")
            if not order_id:
                raise ValueError("Missing required argument: order_id")
            result = await get_order_status(order_id)

        elif name == UpstoxTools.GET_ORDER_BOOK.value:
            result = await get_order_book()

        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=str(result))]

    except ValueError as error:
        return [types.TextContent(type="text", text=f"Value Error: {str(error)}")]
    except ConnectionError as error:
        return [types.TextContent(type="text", text=f"Connection Error: {str(error)}")]
    except TypeError as error:
        return [types.TextContent(type="text", text=f"Type Error: {str(error)}")]
    except KeyError as error:
        return [types.TextContent(type="text", text=f"Key Error: {str(error)}")]
    except Exception as error:
        return [types.TextContent(type="text", text=f"Unexpected Error: {str(error)}")]


async def run_stdio_server():
    """Run the MCP stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="combined_trading_server",
                server_version=get_version(),
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )



async def main():
    """Main entry point"""
    await run_stdio_server()
    if __name__ == "__main__":
        asyncio.run(main())
