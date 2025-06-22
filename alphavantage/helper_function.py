import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)  


API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

if not API_KEY:
    raise ValueError("ALPHAVANTAGE_API_KEY environment variable required")


API_BASE_URL = "https://www.alphavantage.co/query"


async def fetch_quote(symbol: str, datatype: str = "json") -> dict[str, str] | str:
    """
    Fetch a stock quote from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.
    :argument: datatype (str): The response data type (default: "json").

    :returns: The stock quote data.
    """

    https_params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "datatype": datatype,
        "apikey": API_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text if datatype == "csv" else response.json()


async def fetch_company_overview(symbol: str) -> dict[str, str]:
    """
    Fetch company overview from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.

    :returns: The company overview data.
    """

    https_params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.json()


async def fetch_top_gainer_losers() -> dict[str, str]:
    """
    Fetch the top gainers or losers from the Alpha Vantage API.

    :returns: The top gainers or losers data.
    """

    https_params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": API_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.json()


async def fetch_sma(
    symbol: str,
    interval: str,
    time_period: int = 20,
    series_type: str = "close",
    datatype: str = "json",
) -> dict[str, str] | str:
    """
    Fetch Simple Moving Average (SMA) data from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.
    :argument: interval (str): The time interval for the data.
    :argument: time_period (int): The time period for SMA calculation.
    :argument: series_type (str): The price series type.
    :argument: datatype (str): The response data type.

    :returns: The SMA data.
    """
    https_params = {
        "function": "SMA",
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "datatype": datatype,
        "apikey": API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text if datatype == "csv" else response.json()


async def fetch_daily_data(
    symbol: str, outputsize: str = "compact", datatype: str = "json"
) -> dict[str, str] | str:
    """
    Fetch daily stock data from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.
    :argument: outputsize (str): The output size for the data (default: "compact").
    :argument: datatype (str): The response data type (default: "json").

    :returns: The daily stock data.
    """
    https_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": outputsize,
        "datatype": datatype,
        "apikey": API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text if datatype == "csv" else response.json()
