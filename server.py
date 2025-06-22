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
    # search_instruments,
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

            # Place buy order with MARKET type (no price needed)
            order_result = await place_order(
                instrument_token=symbol,
                quantity=quantity,
                transaction_type="BUY",
                order_type="MARKET",
                product="I",
                is_amo=False,
            )

            result = {
            "status": "success",
            "action": "BUY",
            "symbol": symbol,
            "quantity": quantity,
            "order_type": "MARKET",
            "timestamp": datetime.now().isoformat(),
            "order_id": order_result.get("data", {}).get("order_id", "N/A"),
            }

        elif name == UpstoxTools.SELL_STOCK.value:
            symbol = arguments.get("symbol")
            quantity = arguments.get("quantity")
            if not symbol or not quantity:
                raise ValueError("Missing required arguments: symbol, quantity")

            # Place sell order with MARKET type (no price needed)
            order_result = await place_order(
                instrument_token=symbol,
                quantity=quantity,
                transaction_type="SELL",
                order_type="MARKET",
                product="I",
                is_amo=False,
            )

            result = {
            "status": "success",
            "action": "SELL",
            "symbol": symbol,
            "quantity": quantity,
            "order_type": "MARKET",
            "timestamp": datetime.now().isoformat(),
            "order_id": order_result.get("data", {}).get("order_id", "N/A"),
            }

        elif name == UpstoxTools.PLACE_AMO_ORDER.value:
            symbol = arguments.get("symbol")
            quantity = arguments.get("quantity")
            transaction_type = arguments.get("transaction_type")
            if not symbol or not quantity or not transaction_type:
                raise ValueError(
                    "Missing required arguments: symbol, quantity, transaction_type"
                )

            # Place AMO order with LIMIT type and a default price
            order_result = await place_order(
                instrument_token=symbol,
                quantity=quantity,
                transaction_type=transaction_type.upper(),
                order_type="LIMIT",
                product="I",
                is_amo=True,
            )

            result = {
            "status": "success",
            "action": f"AMO_{transaction_type.upper()}",
            "symbol": symbol,
            "quantity": quantity,
            "order_type": "LIMIT",
            "timestamp": datetime.now().isoformat(),
            "order_id": order_result.get("data", {}).get("order_id", "N/A"),
            }

        elif name == UpstoxTools.GET_PORTFOLIO.value:
            result = await get_portfolio()

        elif name == UpstoxTools.GET_FUNDS.value:
            result = await get_funds()

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
