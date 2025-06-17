import yfinance as yf, requests, talib, pandas as pd, time
from typing import Dict, List, Tuple

# def find_ticker_symbol(company_name: str) -> str | None: 
#     """
#     See if ticker is mentioned in company_name
#     """
#     print(f"Primary Search Tool: Searching for ticker for '{company_name}'...")

#     try:
#         ticker = yf.Ticker(company_name)
#         if ticker.info and 'symbol' in ticker.info:
#             return ticker.info['symbol']
#         raise Exception("`yfinance.Ticker` found no info.") # HTTP Error 404: 

#     except Exception:
#         # If ticker=yf.Ticker fails, execute secondary search
#         return search_by_stock_list(company_name)

# def search_by_stock_list(company_name: str) -> str | None:
#     """
#     Try to find ticker from SEC Trustworthy List
#     """
#     print(f"Secondary Search Tool: Searching for ticker from SEC JSON list for '{company_name}'...")
#     path = Path(__file__).parent / "stock_list.json"
#     with open(path, 'r') as f:
#         data = json.load(f)
    
#     for entry in data.values(): # {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'} --> entry
#         if company_name.lower() in entry['title'].lower():
#             return entry['ticker']
#     # Tertiary search
#     return search_yahoo_api(company_name)
    
def search_yahoo_api(company_name: str) -> str | None:
    """
    Use direct API call if direct neither of the two work!
    """
    print(f"Search Tool: Trying direct API fallback for '{company_name}'...")

    # Special request for BTC-USD
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
        trend = "upward" if closes.iloc[-1] > closes.iloc[0] else "downward"
        volatility = closes.std() / closes.mean() * 100
        
        # Moving averages
        ma_short = closes.rolling(window=max(5, int(len(closes)*0.08))).mean().iloc[-1]
        ma_long = closes.rolling(window=max(10, int(len(closes)*0.8))).mean().iloc[-1]

        res = {
            "symbol": ticker_symbol,
            "period": period,
            "trend_direction": trend,
            "volatility_pct": volatility,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "highest_price": closes.max(),
            "lowest_price": closes.min(),
            "avg_daily_volume": volumes.mean(),
            "total_return_pct": ((closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0]) * 100
        }

        # Debugging
        # print("\n", "-"*10, "HIST. ANALYSIS", "-"*10)
        # print(res, "\n")
        
        return res
    
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

    # Debugging            
    # print("\n", "-"*10, "COMPARISON", "-"*10)
    # print(comparison)
    
    return comparison

def get_multi_timeframe_data(symbol: str, timeframes: List[str] = ['15m', '1hr', '4hr', '1d'], period: str = '3d') -> Dict:
    """
    Fetch candlestick data across multiple timeframes
    """
    multi_data = {}

    for tf in timeframes:
        yf_interval = {
            '15m': '15m', 
            '1h': '1h', 
            '4h': '4h', 
            '1d': '1d'
        }.get(tf, '1h')

        data = yf.Ticker(symbol).history(period=period, interval=yf_interval)
        if not data.empty:
            multi_data[tf] = {
                'ohlc': data,
                'patterns': detect_candlestick_patterns(data),
                'timeframe': tf
            }
    
    return multi_data

def detect_candlestick_patterns(data: pd.DataFrame) -> Dict:
    """
    Detect multiple candlestick patterns using TA-lib
    Returns pattern signals with confidence scores
    """ 
    patterns = {}

    open_prices = data['Open'].values
    high_prices = data['High'].values
    low_prices = data['Low'].values
    close_prices = data['Close'].values
    
    # All values for reliability and profit potential are based on stats!
    patterns['inverted_hammer'] = {
        'signal': talib.CDLINVERTEDHAMMER(open=open_prices, high=high_prices, low=low_prices, close=close_prices),
        'reliability': 0.6,        
        'profit_potential': 1.12    
    }
    patterns['bearish_marubozu'] = {
        'signal': talib.CDLMARUBOZU(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.561,
        'profit_potential': 0.80
    }
    patterns['gravestone_doji'] = {
        'signal': talib.CDLGRAVESTONEDOJI(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.57,
        'profit_potential': 0.65
    }
    engulfing_signal = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)
    patterns['bearish_engulfing'] = {
        'signal': [s if s < 0 else 0 for s in engulfing_signal], # Keep only negative values
        'reliability': 0.57,
        'profit_potential': 0.61
    }
    patterns['bullish_engulfing'] = {
        'signal': [s if s > 0 else 0 for s in engulfing_signal], # Keep only positive values
        'reliability': 0.57,
        'profit_potential': 0.58
    }
    patterns['shooting_star'] = {
        'signal': talib.CDLSHOOTINGSTAR(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.571,
        'profit_potential': 0.56
    }
    patterns['hammer'] = {
        'signal': talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.54,
        'profit_potential': 0.52
    }
    patterns['hanging_man'] = {
        'signal': talib.CDLHANGINGMAN(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.54,
        'profit_potential': 0.48
    }
    patterns['morning_star'] = {
        'signal': talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.54,
        'profit_potential': 0.45
    }
    patterns['evening_star'] = {
        'signal': talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices),
        'reliability': 0.53,
        'profit_potential': 0.42
    }

    return patterns

def analyze_pattern_confluence(multi_timeframe_data: Dict) -> Dict:
    """
    Analyze pattern confluence across timeframes
    Higher confluence = stronger signal
    """
    confluence_analysis = {
        'bullish_signals': 0,
        'bearish_signals': 0,          
        'confluence_score': 0,          # Total signals (bullish + bearish)
        'recommendation': 'NEUTRAL',    # Whether bullish or bearish is higher to get BUY or SELL
        'confidence': 0,                # If BUY, bullish_signals/total_signals
        'detected_patterns': []         # Patterns etc.
    }

    timeframe_weights = {'1d': 0.40, '4h': 0.35, '1h': 0.15, '15m': 0.10}

    for tf, data in multi_timeframe_data.items():
        patterns = data['patterns']           # Gives you candlestick patterns function's output
        weight = timeframe_weights.get(tf, 0.1)
        
        for pattern_name, pattern_data in patterns.items():
            latest_signal = pattern_data['signal'][-1] if len(pattern_data['signal']) > 0 else 0
            
            if latest_signal != 0:  # Pattern detected
                reliability = pattern_data['reliability']
                signal_strength = abs(latest_signal) / 100 * reliability * weight
                
                confluence_analysis['detected_patterns'].append({
                    'pattern': pattern_name,
                    'timeframe': tf,
                    'signal': latest_signal,
                    'reliability': reliability,
                    'strength': signal_strength
                })
                
                if latest_signal > 0:  # Bullish
                    confluence_analysis['bullish_signals'] += signal_strength
                else:                   # Bearish
                    confluence_analysis['bearish_signals'] += signal_strength
    
    # Calculate overall confluence
    total_signals = confluence_analysis['bullish_signals'] + confluence_analysis['bearish_signals']
    
    if total_signals > 0:
        if confluence_analysis['bullish_signals'] > confluence_analysis['bearish_signals']:
            confluence_analysis['recommendation'] = 'BUY'
            confluence_analysis['confidence'] = confluence_analysis['bullish_signals'] / total_signals
        else:
            confluence_analysis['recommendation'] = 'SELL'  
            confluence_analysis['confidence'] = confluence_analysis['bearish_signals'] / total_signals
        
        confluence_analysis['confluence_score'] = total_signals
    
    return confluence_analysis


if __name__ == "__main__":
    start_time = time.time()
    multi_data = get_multi_timeframe_data('BTC-USD', period='1mo')
    # for key, value in multi_data.items():
    #     print(key, "-"*10)
    #     for key1, value1 in value.items():
    #         print(f"{key1}: {value1}")

    confluenze_analysis = analyze_pattern_confluence(multi_data)
    for key, value in confluenze_analysis.items():
        print(f"{key}: {value}")
    
    print("Time taken:", time.time()-start_time)