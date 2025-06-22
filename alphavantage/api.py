import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
if not API_KEY:
    raise ValueError("ALPHAVANTAGE_API_KEY environment variable required")

API_BASE_URL = "https://www.alphavantage.co/query"

