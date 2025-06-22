import asyncio
import sys
import os
from server import main as run_server

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    print ("Starting server...")
    print (os.getenv("ALPHAVANTAGE_API_KEY"))
    asyncio.run(run_server())
