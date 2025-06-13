import yfinance as yf, requests

def find_ticker_symbol(company_name: str) -> str | None: 
    """
    Primary search: If ticker is mentioned in company_name
    Secondary search: Falls back to API search, if not available!
    """
    print(f"Primary Search Tool: Searching for ticker for '{company_name}'...")
    try:
        ticker = yf.Ticker(company_name)
        if ticker.info and 'symbol' in ticker.info:
            return ticker.info['symbol']
        raise Exception("`yfinance.Ticker` found no info.") # HTTP Error 404: 

    except Exception:
        # If ticker=yf.Ticker fails, execute secondary search
        return search_yahoo_api(company_name)
    
def search_yahoo_api(company_name: str) -> str | None:
    """
    Use direct API call if direct ticker doesn't work!
    """
    print(f"Secondary Search Tool: Trying direct API fallback for '{company_name}'...")
    # User-Agent disguises 'bot search' to 'human search' and it connects directly to Yahoo Finance's __search endpoint__
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    # HTTP Get request
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raises exception if status code fails (like 400, 403, 404, 500 etc.)
        data = response.json() # Converts <class 'requests.models.Response'> to <class 'dict'> 
        
        # The API returns a list of quotes; we'll take the first, most relevant one.
        """
        Ex output of data:
        {
            "quotes": [
                {
                "symbol": "GOOGL",
                "shortname": "Alphabet Inc.",
                "exchange": "NAS",
                ...
                },
                ...
            ]
        }
        """
        if data.get('quotes'):
            print(f"Found symbol: {data['quotes'][0]['symbol']}")
            return data['quotes'][0]['symbol']
        return None # No responses found for `company_name`
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Direct API search failed - {e}")
        return None

def get_stock_quote(ticker_symbol: str, period: str = "1d") -> dict:
    """
    Fetches stock quote data for a given ticker symbol and period.
    """
    print(f"Fetch Tool: Fetching quote for '{ticker_symbol}' (period: {period})...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            return {"ERROR": f"No data found for ticker: {ticker_symbol}. It may be delisted or invalid."}

        latest = data.iloc[-1]
        first = data.iloc[0] if len(data) > 1 else latest
        
        # Calculate period performance
        period_change = ((latest['Close'] - first['Open']) / first['Open']) * 100
        
        return {
            "symbol": ticker_symbol,
            "current_price": latest['Close'],
            "period_high": data['High'].max(),
            "period_low": data['Low'].min(),
            "period_open": first['Open'],
            "latest_volume": latest['Volume'],
            "avg_volume": data['Volume'].mean(),
            "period_change_pct": period_change,
            "period": period,
            "data_points": len(data)
        }
    
    except Exception as e:
        return {"ERROR": f"An error occurred while fetching the quote: {e}"}

def get_historical_analysis(ticker_symbol: str, period: str = "1mo") -> dict:
    """
    Provides historical analysis including trends and patterns.
    """
    print(f"Analysis Tool: Analyzing historical data for '{ticker_symbol}' (period: {period})...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period=period)
        
        if data.empty or len(data) < 5:
            return {"ERROR": f"Insufficient data for analysis: {ticker_symbol}"}
        
        # Calculate various metrics
        closes = data['Close']
        volumes = data['Volume']
        
        # Trend analysis
        recent_trend = "upward" if closes.iloc[-1] > closes.iloc[-5] else "downward" # last 5 entries
        volatility = closes.std() / closes.mean() * 100
        
        # Moving averages
        ma_short = closes.rolling(window=min(5, len(closes))).mean().iloc[-1]
        ma_long = closes.rolling(window=min(10, len(closes))).mean().iloc[-1]
        
        return {
            "symbol": ticker_symbol,
            "period": period,
            "trend_direction": recent_trend,
            "volatility_pct": volatility,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "highest_price": closes.max(),
            "lowest_price": closes.min(),
            "avg_daily_volume": volumes.mean(),
            "total_return_pct": ((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]) * 100
        }
    
    except Exception as e:
        return {"ERROR": f"An error occurred during analysis: {e}"}

def compare_stock_data(stock_results: dict, period: str = "1mo") -> dict:
    """
    Compares multiple stocks' performance.
    """
    print(f"Comparison Tool: Comparing {len(stock_results)} stocks over {period}...")
    
    if not stock_results:
        return {"ERROR": "No valid stock data to compare"}
    
    comparison = {
        "period": period,
        "companies": {},
        "best_performer": None,
        "worst_performer": None,
        "most_volatile": None
    }
    
    best_return = float('-inf')
    worst_return = float('inf')
    highest_volatility = 0
    
    for company, data in stock_results.items():
        if isinstance(data, dict) and "period_change_pct" in data:
            comparison["companies"][company] = {
                "symbol": data.get("symbol", ""),
                "return_pct": data.get("period_change_pct", 0),
                "current_price": data.get("current_price", 0),
                "volatility": abs(data.get("period_change_pct", 0))  # Simplified volatility
            }
            
            # Track best/worst performers
            return_pct = data.get("period_change_pct", 0)
            if return_pct > best_return:
                best_return = return_pct
                comparison["best_performer"] = company
            if return_pct < worst_return:
                worst_return = return_pct
                comparison["worst_performer"] = company
            if abs(return_pct) > highest_volatility:
                highest_volatility = abs(return_pct)
                comparison["most_volatile"] = company
    
    return comparison

if __name__ == '__main__':
    print("--- Testing Financial Tools ---")
    company_to_find = "GOOGle"
    symbol = find_ticker_symbol(company_to_find)
    if symbol:
        print(f"SUCCESS Search: Found ticker '{symbol}' for '{company_to_find}'.")
        quote = get_stock_quote(symbol)
        
        if "ERROR" not in quote: # If get_stock_quote has ERROR or raises its exception flag
            print(f"SUCCESS Fetch: Fetched quote for {symbol}:")
            for key, value in quote.items():
                if isinstance(value, float):
                    print(f"  {key.capitalize()}: ${value:,.2f}")
                else:
                    print(f"  {key.capitalize()}: {value}")
        else:
            print(f"FAILURE: Could not get quote for {symbol}. Reason: {quote['ERROR']}")
    else:
        print(f"FAILURE: Could not find a ticker for '{company_to_find}'.")