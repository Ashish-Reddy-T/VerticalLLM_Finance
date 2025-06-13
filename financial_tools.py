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
            return data['quotes'][0]['symbol']
        return None # No responses found for `company_name`
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Direct API search failed - {e}")
        return None

def get_stock_quote(ticker_symbol: str) -> dict:
    """
    Fetches the latest stock quote data for a given ticker symbol.
    """
    print(f"Fetch Tool: Fetching quote for '{ticker_symbol}'...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="1d") # By default interval is set at 1d
        
        if data.empty:
            return {"ERROR": f"No data found for ticker: {ticker_symbol}. It may be delisted or invalid."}

        latest = data.iloc[-1] # Get last row - for latest info

        # print(latest) (To get the columns of `latest`)
        
        return {
            "symbol": ticker_symbol,
            "price": latest['Close'],
            "high": latest['High'],
            "low": latest['Low'],
            "open": latest['Open'],
            "volume": latest['Volume']
        }
    
    except Exception as e:
        return {"ERROR": f"An error occurred while fetching the quote: {e}"}

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