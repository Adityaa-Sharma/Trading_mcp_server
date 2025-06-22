import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
if not API_KEY:
    raise ValueError("ALPHAVANTAGE_API_KEY environment variable required")


API_BASE_URL = "https://www.alphavantage.co/query"

async def fetch_intraday(
    symbol: str,
    interval: str = "60min",
    datatype: str = "json",
    adjusted: bool = True,
    extended_hours: bool = True,
    outputsize: str = "compact",
    month: str = None,
) -> dict[str, str] | str:
    """
    Fetch intraday stock data from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.
    :argument: interval (str): The time interval for the data (default: "5min").
    :argument: datatype (str): The response data type (default: "json").
    :argument: adjusted (bool): The adjusted data flag (default: True).
    :argument: extended_hours (bool): The extended hours flag (default: True).
    :argument: outputsize (str): The output size for the data (default: "compact").
    :argument: month (str): The month of the data (default: None).

    :returns: The intraday stock data.
    """

    https_params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "datatype": datatype,
        "adjusted": adjusted,
        "outputsize": outputsize,
        "extended_hours": extended_hours,
        "month": month,
        "apikey": API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text if datatype == "csv" else response.json()



async def fetch_news_sentiment(
    tickers: list[str],
    datatype: str = "json",
    topics: list[str] = None,
    time_from: str = None,
    time_to: str = None,
    sort: str = "LATEST",
    limit: int = 50,
) -> dict[str, str] | str:
    """
    Fetch news sentiment data from the Alpha Vantage API.

    :argument: tickers (list[str]): The stock tickers to fetch.
    :argument: datatype (str): The response data type (default: "json").
    :argument: topics (list[str]): The news topics (default: None).
    :argument: time_from (str): The start time (default: None).
    :argument: time_to (str): The end time (default: None).
    :argument: sort (str): The sort order (default: "LATEST").
    :argument: limit (int): The number of news articles to fetch (default: 50).

    :returns: The news sentiment data.
    """

    https_params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ",".join(tickers),
        "datatype": datatype,
        "topics": ",".join(topics) if topics else None,
        "time_from": time_from,
        "time_to": time_to,
        "sort": sort,
        "limit": limit,
        "apikey": API_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text if datatype == "csv" else response.json()
    
    
async def fetch_market_status() -> dict[str, str] | str:
    """
    Fetch the market status from the Alpha Vantage API.

    :returns: The market status.
    """

    https_params = {"function": "MARKET_STATUS", "apikey": API_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.json()
    
    
async def fetch_analytics_fixed_window(
    symbols: list[str],
    interval: str,
    series_range: str = "full",
    ohlc: str = "close",
    calculations: list[str] = None,
) -> dict[str, str]:
    """
    Fetch analytics data from the Alpha Vantage API.

    :argument: symbol (list[str]): The stock symbols to fetch.
    :argument: range (str): The range of the data (default: "full").
    :argument: interval (str): The time interval for the data.
    :argument: ohlc (str): The OHLC data type (default: "close").
    :argument: calculations (list[str]): The analytics calculations (default: None).

    :returns: The analytics data.
    """

    https_params = {
        "function": "ANALYTICS_FIXED_WINDOW",
        "symbol": ",".join(symbols),
        "range": series_range,
        "interval": interval,
        "ohlc": ohlc,
        "calculations": ",".join(calculations) if calculations else None,
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
       
async def fetch_atr(
    symbol: str,
    interval: str = None,
    month: str = None,
    time_period: int = 14,
    datatype: str = "json",
) -> dict[str, str] | str:
    """
    Fetch average true range (ATR) data from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.
    :argument: interval (str): The time interval for the data.
    :argument: month (str): The month for the data.
    :argument: time_period (int): The time period for the data.
    :argument: datatype (str): The response data type (default: "json").

    :returns: Average true range (ATR) data.
    """

    https_params = {
        "function": "ATR",
        "symbol": symbol,
        "interval": interval,
        "month": month,
        "time_period": time_period,
        "datatype": datatype,
        "apikey": API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text if datatype == "csv" else response.json()
    

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

async def fetch_daily_data(
    symbol: str,
    outputsize: str = "compact",
    datatype: str = "json"
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

async def fetch_sma(
    symbol: str,
    interval: str,
    time_period: int = 20,
    series_type: str = "close",
    datatype: str = "json"
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

async def fetch_rsi(
    symbol: str,
    interval: str,
    time_period: int = 14,
    series_type: str = "close",
    datatype: str = "json"
) -> dict[str, str] | str:
    """
    Fetch Relative Strength Index (RSI) data from the Alpha Vantage API.
    
    :argument: symbol (str): The stock symbol to fetch.
    :argument: interval (str): The time interval for the data.
    :argument: time_period (int): The time period for RSI calculation.
    :argument: series_type (str): The price series type.
    :argument: datatype (str): The response data type.
    
    :returns: The RSI data.
    """
    https_params = {
        "function": "RSI",
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


async def fetch_earnings_calendar(
    symbol: str, horizon: str = "3month"
) -> str:
    """
    Fetch companies earnings calendar data from the Alpha Vantage API.

    :argument: symbol (str): The stock symbol to fetch.
    :argument: horizon (str): The earning calendar horizon (default: "3month").

    :returns: The company earning calendar data using CSV format
    """

    https_params = {
        "function": "EARNINGS_CALENDAR",
        "horizon": horizon,
        "apikey": API_KEY,
    }
    if symbol:
        https_params["symbol"] = symbol

    async with httpx.AsyncClient() as client:
        response = await client.get(API_BASE_URL, params=https_params)
        response.raise_for_status()
        return response.text