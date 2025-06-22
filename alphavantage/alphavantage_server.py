from typing import Any, Dict, List
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

from alphavantage.helper_function import (
    fetch_quote, fetch_intraday, fetch_daily_data, fetch_sma, fetch_rsi, 
    fetch_atr, fetch_news_sentiment, fetch_top_gainer_losers
)

# Initialize FastMCP servcer
mcp = FastMCP("AlphaVantageIndianStocks", "1.0.0")

def calculate_technical_signals(price_data: Dict, rsi_data: Dict, sma_data: Dict, atr_data: Dict) -> Dict[str, Any]:
    """Calculate buy/sell signals based on technical indicators"""
    try:
        # Get latest values
        latest_price = float(list(price_data.values())[0]['4. close'])
        latest_rsi = float(list(rsi_data.values())[0]['RSI'])
        latest_sma = float(list(sma_data.values())[0]['SMA'])
        latest_atr = float(list(atr_data.values())[0]['ATR'])
        
        # Calculate signals
        buy_score = 0
        sell_score = 0
        
        # RSI signals
        if latest_rsi < 30:  # Oversold
            buy_score += 30
        elif latest_rsi > 70:  # Overbought
            sell_score += 30
            
        # Price vs SMA signals
        if latest_price > latest_sma:  # Above moving average
            buy_score += 25
        else:  # Below moving average
            sell_score += 25
            
        # Momentum signals (simplified)
        price_change = (latest_price - latest_sma) / latest_sma * 100
        if price_change > 2:
            buy_score += 20
        elif price_change < -2:
            sell_score += 20
            
        # Normalize scores
        total_score = buy_score + sell_score
        if total_score > 0:
            buy_score = min(100, (buy_score / total_score) * 100)
            sell_score = min(100, (sell_score / total_score) * 100)
            
        confidence = min(max(total_score, 0), 100)
        
        return {
            "buy_score": round(buy_score, 2),
            "sell_score": round(sell_score, 2),
            "confidence": round(confidence, 2),
            "latest_price": latest_price,
            "rsi": latest_rsi,
            "sma": latest_sma,
            "atr": latest_atr
        }
    except Exception as e:
        return {"error": f"Error calculating signals: {str(e)}"}

@mcp.tool()
async def get_realtime_signal(symbol: str, strategy: str = "swing") -> Dict[str, Any]:
    """
    Get real-time buy/sell signals for Indian stocks
    
    Args:
        symbol: Indian stock symbol (e.g., RELIANCE.BSE, TCS.BSE)
        strategy: Trading strategy ('swing', 'intraday', 'long_term')
    
    Returns:
        Dictionary with buy_score, sell_score, and confidence
    """
    try:
        # Add .BSE suffix if not present for Indian stocks
        if not symbol.endswith(('.BSE', '.NSE')):
            symbol = f"{symbol}.BSE"
            
        # Fetch required data based on strategy
        interval = "60min" if strategy == "intraday" else "daily"
        
        # Get current quote
        quote_data = await fetch_quote(symbol)
        
        # Get technical indicators
        if strategy == "intraday":
            price_data = await fetch_intraday(symbol, interval="60min")
            rsi_data = await fetch_rsi(symbol, interval="60min")
            sma_data = await fetch_sma(symbol, interval="60min", time_period=20)
            atr_data = await fetch_atr(symbol, interval="60min")
        else:
            price_data = await fetch_daily_data(symbol)
            rsi_data = await fetch_rsi(symbol, interval="daily")
            sma_data = await fetch_sma(symbol, interval="daily", time_period=20)
            atr_data = await fetch_atr(symbol, interval="daily")
            
        # Extract time series data
        if strategy == "intraday":
            time_series_key = f"Time Series ({interval})"
        else:
            time_series_key = "Time Series (Daily)"
            
        price_series = price_data.get(time_series_key, {})
        rsi_series = rsi_data.get("Technical Analysis: RSI", {})
        sma_series = sma_data.get("Technical Analysis: SMA", {})
        atr_series = atr_data.get("Technical Analysis: ATR", {})
        
        # Calculate signals
        signals = calculate_technical_signals(price_series, rsi_series, sma_series, atr_series)
        
        return {
            "symbol": symbol,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
            **signals
        }
        
    except Exception as e:
        return {"error": f"Failed to get signals for {symbol}: {str(e)}"}

@mcp.tool()
async def assess_position_risk(symbol: str, quantity: int) -> Dict[str, Any]:
    """
    Assess position risk for Indian stocks
    
    Args:
        symbol: Indian stock symbol
        quantity: Number of shares
    
    Returns:
        Dictionary with risk_score, max_loss, stop_price
    """
    try:
        if not symbol.endswith(('.BSE', '.NSE')):
            symbol = f"{symbol}.BSE"
            
        # Get current price and ATR for volatility
        quote_data = await fetch_quote(symbol)
        atr_data = await fetch_atr(symbol, interval="daily")
        
        current_price = float(quote_data["Global Quote"]["05. price"])
        atr_value = float(list(atr_data.get("Technical Analysis: ATR", {}).values())[0]["ATR"])
        
        # Calculate risk metrics
        position_value = current_price * quantity
        daily_volatility = atr_value / current_price  # As percentage
        
        # Risk scoring (0-100, higher = riskier)
        risk_score = min(100, daily_volatility * 1000)  # Scale volatility
        
        # Calculate stop loss (2 ATR below current price)
        stop_price = current_price - (2 * atr_value)
        max_loss = (current_price - stop_price) * quantity
        
        return {
            "symbol": symbol,
            "quantity": quantity,
            "current_price": round(current_price, 2),
            "position_value": round(position_value, 2),
            "risk_score": round(risk_score, 2),
            "max_loss": round(max_loss, 2),
            "stop_price": round(stop_price, 2),
            "daily_volatility": round(daily_volatility * 100, 2),
            "atr": round(atr_value, 2)
        }
        
    except (ValueError, KeyError, TypeError, IndexError) as e:
        # Handle specific exceptions related to data processing and calculation
        return {"error": f"Failed to assess risk for {symbol}: {str(e)}"}
    except Exception as e:
        # Log unexpected exceptions but provide a general error message
        print(f"Unexpected error in assess_position_risk: {str(e)}")
        return {"error": f"An unexpected error occurred while assessing risk for {symbol}"}

@mcp.tool()
async def analyze_portfolio(watchlist: List[str]) -> Dict[str, Any]:
    """
    Analyze portfolio diversification for Indian stocks
    
    Args:
        watchlist: List of Indian stock symbols
    
    Returns:
        Dictionary with correlations and sector_exposure
    """
    try:
        # Ensure Indian stock format
        formatted_watchlist = []
        for symbol in watchlist:
            if not symbol.endswith(('.BSE', '.NSE')):
                formatted_watchlist.append(f"{symbol}.BSE")
            else:
                formatted_watchlist.append(symbol)
        
        # Get quotes for all stocks
        portfolio_data = {}
        for symbol in formatted_watchlist:
            try:
                quote = await fetch_quote(symbol)
                portfolio_data[symbol] = {
                    "price": float(quote["Global Quote"]["05. price"]),
                    "change_percent": float(quote["Global Quote"]["10. change percent"].rstrip('%'))
                }
            except:
                continue
                
        # Simplified sector classification for Indian stocks
        sector_mapping = {
            "RELIANCE": "Energy", "TCS": "IT", "INFY": "IT", "WIPRO": "IT",
            "HDFCBANK": "Banking", "ICICIBANK": "Banking", "SBIN": "Banking",
            "ITC": "FMCG", "HUL": "FMCG", "BAJFINANCE": "Financial Services",
            "LT": "Construction", "MARUTI": "Automotive", "TATAMOTORS": "Automotive"
        }
        
        # Calculate sector exposure
        sector_exposure = {}
        for symbol in portfolio_data.keys():
            base_symbol = symbol.split('.')[0]
            sector = sector_mapping.get(base_symbol, "Others")
            sector_exposure[sector] = sector_exposure.get(sector, 0) + 1
            
        # Convert to percentages
        total_stocks = len(portfolio_data)
        sector_exposure = {k: round((v/total_stocks)*100, 2) for k, v in sector_exposure.items()}
        
        # Simple correlation analysis (based on price changes)
        correlations = {}
        symbols = list(portfolio_data.keys())
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                # Simplified correlation based on price change direction
                change1 = portfolio_data[sym1]["change_percent"]
                change2 = portfolio_data[sym2]["change_percent"]
                correlation = 1 if (change1 > 0 and change2 > 0) or (change1 < 0 and change2 < 0) else -1
                correlations[f"{sym1}-{sym2}"] = correlation
        
        return {
            "portfolio_size": total_stocks,
            "sector_exposure": sector_exposure,
            "correlations": correlations,
            "portfolio_data": portfolio_data,
            "diversification_score": round(100 - max(sector_exposure.values()), 2) if sector_exposure else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to analyze portfolio: {str(e)}"}

@mcp.tool()
async def scan_earnings_catalyst(sector: str = "all") -> Dict[str, Any]:
    """
    Scan for earnings catalysts in Indian stocks
    
    Args:
        sector: Sector to scan ('tech', 'banking', 'auto', 'fmcg', 'all')
    
    Returns:
        Dictionary with symbol, date, expected_move for earnings events
    """
    try:
        # Define Indian stock universe by sector
        sector_stocks = {
            "tech": ["TCS.BSE", "INFY.BSE", "WIPRO.BSE", "HCLTECH.BSE", "TECHM.BSE"],
            "banking": ["HDFCBANK.BSE", "ICICIBANK.BSE", "SBIN.BSE", "AXISBANK.BSE", "KOTAKBANK.BSE"],
            "auto": ["MARUTI.BSE", "TATAMOTORS.BSE", "M&M.BSE", "BAJAJ-AUTO.BSE", "EICHERMOT.BSE"],
            "fmcg": ["ITC.BSE", "HUL.BSE", "NESTLEIND.BSE", "BRITANNIA.BSE", "DABUR.BSE"],
            "energy": ["RELIANCE.BSE", "ONGC.BSE", "IOC.BSE", "BPCL.BSE", "GAIL.BSE"]
        }
        
        if sector.lower() == "all":
            stocks_to_scan = []
            for sector_list in sector_stocks.values():
                stocks_to_scan.extend(sector_list)
        else:
            stocks_to_scan = sector_stocks.get(sector.lower(), [])
            
        if not stocks_to_scan:
            return {"error": f"Invalid sector: {sector}"}
        
        # Get top gainers/losers for catalyst detection
        market_movers = await fetch_top_gainer_losers()
        
        # Scan for high volatility stocks (potential earnings catalyst)
        catalyst_opportunities = []
        
        for symbol in stocks_to_scan[:5]:  # Limit API calls
            try:
                # Get recent volatility
                atr_data = await fetch_atr(symbol, interval="daily")
                quote_data = await fetch_quote(symbol)
                
                current_price = float(quote_data["Global Quote"]["05. price"])
                change_percent = abs(float(quote_data["Global Quote"]["10. change percent"].rstrip('%')))
                atr_value = float(list(atr_data.get("Technical Analysis: ATR", {}).values())[0]["ATR"])
                
                # Calculate expected move (simplified)
                expected_move = (atr_value / current_price) * 100
                
                # Flag as potential catalyst if high volatility
                if change_percent > 3 or expected_move > 2:
                    # Simulate earnings date (next quarter)
                    next_earnings = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                    
                    catalyst_opportunities.append({
                        "symbol": symbol,
                        "current_price": round(current_price, 2),
                        "change_percent": round(change_percent, 2),
                        "expected_move": round(expected_move, 2),
                        "date": next_earnings,
                        "catalyst_type": "earnings",
                        "volatility_rank": "high" if expected_move > 3 else "medium"
                    })
                    
            except Exception as e:
                continue
                
        # Sort by expected move
        catalyst_opportunities.sort(key=lambda x: x["expected_move"], reverse=True)
        
        return {
            "sector": sector,
            "scan_date": datetime.now().isoformat(),
            "opportunities_found": len(catalyst_opportunities),
            "catalyst_events": catalyst_opportunities[:10],  # Top 10
            "market_summary": {
                "total_scanned": len(stocks_to_scan),
                "high_volatility_count": len([x for x in catalyst_opportunities if x["expected_move"] > 3])
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to scan catalysts: {str(e)}"}

if __name__ == "__main__":
    mcp.run()