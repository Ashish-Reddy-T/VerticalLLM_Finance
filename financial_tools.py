import yfinance as yf, requests, yaml
from pathlib import Path

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
    
def search_yahoo_api(company_name: str) -> str | None:
    """
    Use direct API call if direct neither of the two work!
    """
    # Special request for BTC-USD
    # print("OKay")
    # if isinstance(company_name, list):
    #     company_name = company_name[0]
    
    # print(company_name)
    if isinstance(company_name, str):
        keywords = ('btc', 'bitcoin', 'btcusd', 'usdbtc')
        for keyword in keywords:
            if company_name.lower() in keyword:
                company_name = 'BTC-USD'
                break

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
                print(f"Agent: Found symbol: {data['quotes'][0]['symbol']}")
                return data['quotes'][0]['symbol']
        return None # No responses found for `company_name`
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Direct API search failed - {e}")
        return None

def get_stock_quote(ticker_symbol: str, period: str = "1d") -> dict:
    """
    Fetches stock quote data for a given ticker symbol and period.
    """
    print(f"Agent: Fetching quote for '{ticker_symbol}' (period: {period})...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            return {"ERROR": f"No data found for ticker: {ticker_symbol}. It may be delisted or invalid."}

        latest = data.iloc[-1]
        first = data.iloc[0] if len(data) > 1 else latest
        
        # Calculate period performance
        period_change = ((latest['Close'] - first['Open']) / first['Open']) * 100
        
        res = {
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

        # Debugging
        # print("\n", "-"*10, "CURR. ANALYSIS", "-"*10)
        # print(res, "\n")

        return res
    
    except Exception as e:
        return {"ERROR": f"An error occurred while fetching the quote: {e}"}

def compare_stock_data(stock_results: dict, period: str = "1mo") -> dict:
    """
    Compares multiple stocks' performance.
    """
    print(f"Agent: Comparing {len(stock_results)} stocks over {period}...")
    
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

    # Debugging            
    # print("\n", "-"*10, "COMPARISON", "-"*10)
    # print(comparison)
    
    return comparison