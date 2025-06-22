from enum import Enum


class AlphavantageTools(str, Enum):
    STOCK_QUOTE = "stock_quote"
    COMPANY_OVERVIEW = "company_overview"
    TOP_GAINERS_LOSERS = "top_gainers_losers"
    SMA = "sma"
    INTRADAY = "intraday"
    DAILY_DATA = "daily_data"
