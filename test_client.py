import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class TradingClient:
    """Client for interacting with the Trading MCP server"""

    def __init__(self):
        self.session = None
        self.client_context = None

    async def connect(self):
        """Connect to the MCP server"""
        server_params = StdioServerParameters(command="python", args=["main.py"])

        self.client_context = stdio_client(server_params)
        read, write = await self.client_context.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.client_context:
            await self.client_context.__aexit__(None, None, None)

    async def get_quote(self, symbol: str):
        """Get stock quote"""
        result = await self.session.call_tool("get_stock_quote", {"symbol": symbol})
        return json.loads(result.content[0].text)

    async def buy_stock(self, symbol: str, quantity: int, order_type: str = "MARKET"):
        """Buy stock"""
        result = await self.session.call_tool(
            "buy_stock",
            {"symbol": symbol, "quantity": quantity, "order_type": order_type},
        )
        return json.loads(result.content[0].text)

    async def sell_stock(self, symbol: str, quantity: int, order_type: str = "MARKET"):
        """Sell stock"""
        result = await self.session.call_tool(
            "sell_stock",
            {"symbol": symbol, "quantity": quantity, "order_type": order_type},
        )
        return json.loads(result.content[0].text)


async def interactive_demo():
    """Interactive demo"""
    client = TradingClient()

    try:
        print("Connecting to Trading MCP Server...")
        await client.connect()
        print("✅ Connected successfully!\n")

        while True:
            print("\n" + "=" * 50)
            print("Trading MCP Server Demo")
            print("=" * 50)
            print("1. Get Stock Quote")
            print("2. Buy Stock")
            print("3. Sell Stock")
            print("4. Exit")

            choice = input("\nSelect an option (1-4): ").strip()

            if choice == "1":
                symbol = input("Enter stock symbol: ").strip()
                print(f"\n📊 Getting quote for {symbol}...")
                result = await client.get_quote(symbol)
                print(json.dumps(result, indent=2))

            elif choice == "2":
                symbol = input("Enter stock symbol: ").strip()
                quantity = int(input("Enter quantity: "))
                order_type = (
                    input("Order type (MARKET/LIMIT) [MARKET]: ").strip() or "MARKET"
                )

                print(f"\n🛒 Buying {quantity} shares of {symbol}...")
                result = await client.buy_stock(symbol, quantity, order_type)
                print(json.dumps(result, indent=2))

            elif choice == "3":
                symbol = input("Enter stock symbol: ").strip()
                quantity = int(input("Enter quantity: "))
                order_type = (
                    input("Order type (MARKET/LIMIT) [MARKET]: ").strip() or "MARKET"
                )

                print(f"\n🏷️ Selling {quantity} shares of {symbol}...")
                result = await client.sell_stock(symbol, quantity, order_type)
                print(json.dumps(result, indent=2))

            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(interactive_demo())
