import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AlphaVantageClient:
    '''Client for interacting with the AlphaVantage MCP server'''
    def __init__(self):
        self.session = None
        
    async def connect(self):
        """Connect to the MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=["main.py"]
        )
        
        self.client = stdio_client(server_params)
        self.read, self.write = await anext(self.client)
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        # No need to call __aexit__ on client as it's an async generator
    
    async def get_signal(self, symbol: str, strategy: str = "swing"):
        """Get trading signal for a stock"""
        result = await self.session.call_tool("get_realtime_signal", {
            "symbol": symbol,
            "strategy": strategy
        })
        return json.loads(result.content[0].text)
    
    async def assess_risk(self, symbol: str, quantity: int):
        """Assess position risk"""
        result = await self.session.call_tool("assess_position_risk", {
            "symbol": symbol,
            "quantity": quantity
        })
        return json.loads(result.content[0].text)
    
    
    async def analyze_portfolio(self, watchlist: list):
        """Analyze portfolio diversification"""
        result = await self.session.call_tool("analyze_portfolio", {
            "watchlist": watchlist
        })
        return json.loads(result.content[0].text)
    async def scan_catalysts(self, sector: str = "all"):
        """Scan for earnings catalysts"""
        result = await self.session.call_tool("scan_earnings_catalyst", {
            "sector": sector
        })
        return json.loads(result.content[0].text)

async def interactive_demo():
    """Interactive demo of the AlphaVantage client"""
    client = AlphaVantageClient()
    
    try:
        print("Connecting to AlphaVantage MCP Server...")
        await client.connect()
        print("✅ Connected successfully!\n")
        
        while True:
            print("\n" + "="*50)
            print("AlphaVantage Indian Stocks Trading Assistant")
            print("="*50)
            print("1. Get Trading Signal")
            print("2. Assess Position Risk")
            print("4. Analyze Portfolio")
            print("5. Scan Earnings Catalysts")
            print("6. Exit")
            
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == "1":
                symbol = input("Enter stock symbol (e.g., RELIANCE): ").strip()
                strategy = input("Enter strategy (swing/intraday/long_term) [swing]: ").strip() or "swing"
                
                print(f"\n🔍 Getting signal for {symbol}...")
                result = await client.get_signal(symbol, strategy)
                print(json.dumps(result, indent=2))
                
            elif choice == "2":
                symbol = input("Enter stock symbol: ").strip()
                quantity = int(input("Enter quantity: ").strip())
                
                print(f"\n⚠️ Assessing risk for {quantity} shares of {symbol}...")
                result = await client.assess_risk(symbol, quantity)
                print(json.dumps(result, indent=2))
                
            elif choice == "4":
                watchlist_input = input("Enter stocks separated by commas (e.g., RELIANCE,TCS,INFY): ").strip()
                watchlist = [s.strip() for s in watchlist_input.split(',')]
                
                print(f"\n📊 Analyzing portfolio with {len(watchlist)} stocks...")
                result = await client.analyze_portfolio(watchlist)
                print(json.dumps(result, indent=2))
                
            elif choice == "5":
                sector = input("Enter sector (tech/banking/auto/fmcg/all) [all]: ").strip() or "all"
                
                print(f"\n🎯 Scanning {sector} sector for catalysts...")
                result = await client.scan_catalysts(sector)
                print(json.dumps(result, indent=2))
                
            elif choice == "6":
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
