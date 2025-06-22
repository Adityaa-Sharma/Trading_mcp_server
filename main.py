import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alphavantage.alphavantage_server import mcp

if __name__ == "__main__":
    mcp.run()
