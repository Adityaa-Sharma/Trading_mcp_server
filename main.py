import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description='Run MCP Trading Servers')
    parser.add_argument('--server', choices=['alphavantage', 'upstox'], 
                       default='upstox', help='Choose which server to run')
    
    args = parser.parse_args()
    
    if args.server == 'alphavantage':
        from alphavantage.alphavantage_server import mcp
        print("Starting AlphaVantage MCP Server...")
    elif args.server == 'upstox':
        from upstox.upstox_server import mcp
        print("Starting Upstox MCP Server...")
    
    mcp.run()

if __name__ == "__main__":
    main()
