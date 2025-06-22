import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class UpstoxClient:
    def __init__(self):
        self.session = None
        self.client_context = None
        
    async def connect(self):
        """Connect to the Upstox MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=["main.py", "--server", "upstox"]
        )
        
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
    
    async def buy_stock(self, symbol: str, quantity: int, order_type: str = "MARKET", price: float = 0, product: str = "D"):
        """Buy stock"""
        result = await self.session.call_tool("buy_stock", {
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "product": product
        })
        return json.loads(result.content[0].text)
    
    async def sell_stock(self, symbol: str, quantity: int, order_type: str = "MARKET", price: float = 0, product: str = "D"):
        """Sell stock"""
        result = await self.session.call_tool("sell_stock", {
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "product": product
        })
        return json.loads(result.content[0].text)
    
    async def place_amo(self, symbol: str, quantity: int, transaction_type: str, order_type: str = "MARKET", price: float = 0):
        """Place After Market Order"""
        result = await self.session.call_tool("place_amo_order", {
            "symbol": symbol,
            "quantity": quantity,
            "transaction_type": transaction_type,
            "order_type": order_type,
            "price": price
        })
        return json.loads(result.content[0].text)
    
    async def get_portfolio(self):
        """Get portfolio"""
        result = await self.session.call_tool("get_user_portfolio", {})
        return json.loads(result.content[0].text)
    
    async def get_orders(self, order_id: str = None):
        """Get order status"""
        params = {}
        if order_id:
            params["order_id"] = order_id
        result = await self.session.call_tool("get_order_status", params)
        return json.loads(result.content[0].text)
    
    async def cancel_order(self, order_id: str):
        """Cancel order"""
        result = await self.session.call_tool("cancel_order_by_id", {
            "order_id": order_id
        })
        return json.loads(result.content[0].text)
    
    async def get_market_data(self, symbols: list):
        """Get market data"""
        result = await self.session.call_tool("get_market_data", {
            "symbols": symbols
        })
        return json.loads(result.content[0].text)

async def interactive_demo():
    """Interactive demo of the Upstox client"""
    client = UpstoxClient()
    
    try:
        print("Connecting to Upstox MCP Server...")
        await client.connect()
        print("✅ Connected successfully!\n")
        
        while True:
            print("\n" + "="*60)
            print("🏛️  UPSTOX TRADING MCP SERVER")
            print("="*60)
            print("1. 🛒 Buy Stock")
            print("2. 🏷️  Sell Stock")
            print("3. 🌙 Place After Market Order (AMO)")
            print("4. 💼 Get Portfolio")
            print("5. 📋 Get Order Status")
            print("6. ❌ Cancel Order")
            print("7. 📊 Get Market Data")
            print("8. 🚪 Exit")
            
            choice = input("\nSelect an option (1-8): ").strip()
            
            if choice == "1":
                symbol = input("Enter stock symbol (e.g., RELIANCE): ").strip().upper()
                quantity = int(input("Enter quantity: ").strip())
                order_type = input("Enter order type (MARKET/LIMIT) [MARKET]: ").strip().upper() or "MARKET"
                price = 0
                if order_type == "LIMIT":
                    price = float(input("Enter limit price: ").strip())
                product = input("Enter product type (D/I/M) [D]: ").strip().upper() or "D"
                
                print(f"\n🛒 Placing BUY order for {quantity} shares of {symbol}...")
                result = await client.buy_stock(symbol, quantity, order_type, price, product)
                print(json.dumps(result, indent=2))
                
            elif choice == "2":
                symbol = input("Enter stock symbol (e.g., TCS): ").strip().upper()
                quantity = int(input("Enter quantity: ").strip())
                order_type = input("Enter order type (MARKET/LIMIT) [MARKET]: ").strip().upper() or "MARKET"
                price = 0
                if order_type == "LIMIT":
                    price = float(input("Enter limit price: ").strip())
                product = input("Enter product type (D/I/M) [D]: ").strip().upper() or "D"
                
                print(f"\n🏷️ Placing SELL order for {quantity} shares of {symbol}...")
                result = await client.sell_stock(symbol, quantity, order_type, price, product)
                print(json.dumps(result, indent=2))
                
            elif choice == "3":
                symbol = input("Enter stock symbol (e.g., INFY): ").strip().upper()
                quantity = int(input("Enter quantity: ").strip())
                transaction_type = input("Enter transaction type (BUY/SELL): ").strip().upper()
                order_type = input("Enter order type (MARKET/LIMIT) [MARKET]: ").strip().upper() or "MARKET"
                price = 0
                if order_type == "LIMIT":
                    price = float(input("Enter limit price: ").strip())
                
                print(f"\n🌙 Placing AMO {transaction_type} order for {quantity} shares of {symbol}...")
                result = await client.place_amo(symbol, quantity, transaction_type, order_type, price)
                print(json.dumps(result, indent=2))
                
            elif choice == "4":
                print("\n💼 Getting portfolio data...")
                result = await client.get_portfolio()
                print(json.dumps(result, indent=2))
                
            elif choice == "5":
                order_id = input("Enter order ID (leave blank for all orders): ").strip() or None
                
                if order_id:
                    print(f"\n📋 Getting status for order {order_id}...")
                else:
                    print("\n📋 Getting all orders...")
                result = await client.get_orders(order_id)
                print(json.dumps(result, indent=2))
                
            elif choice == "6":
                order_id = input("Enter order ID to cancel: ").strip()
                
                print(f"\n❌ Cancelling order {order_id}...")
                result = await client.cancel_order(order_id)
                print(json.dumps(result, indent=2))
                
            elif choice == "7":
                symbols_input = input("Enter stock symbols separated by commas (e.g., RELIANCE,TCS,INFY): ").strip()
                symbols = [s.strip().upper() for s in symbols_input.split(',')]
                
                print(f"\n📊 Getting market data for {len(symbols)} symbols...")
                result = await client.get_market_data(symbols)
                print(json.dumps(result, indent=2))
                
            elif choice == "8":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("🚀 Starting Interactive Upstox MCP Client...")
    asyncio.run(interactive_demo())
if __name__ == "__main__":
    print("🚀 Starting Interactive Upstox MCP Client...")
    asyncio.run(interactive_demo())
