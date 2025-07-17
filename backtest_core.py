import logging
from collections import deque

from new_technical import IncrementalTechnicalAnalyzer

class PortfolioManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {'SYMBOL': {'shares': X, 'entry_price': Y}}
        self.trade_log = []
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"PortfolioManager initialized with initial capital: ${self.initial_capital:,.2f}")

class MarketDataContext:
    def __init__(self, symbols, history_window = 252):
        self.symbols = symbols
        self.current_date = None
        # Use a deque for efficient, fixed-size rolling data windows
        self.history = {symbol: deque(maxlen=history_window) for symbol in symbols}
        self.indicators = {symbol: {} for symbol in symbols}
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"MarketDataContext initialized for symbols: {self.symbols} with a history window of {history_window} days.")

    def update(self, date, daily_data_for_all_symbols, technical_analyzer):
        self.current_date = date
        for symbol in self.symbols:
            symbol_data = {
                'Open': daily_data_for_all_symbols[('Open', symbol)],
                'High': daily_data_for_all_symbols[('High', symbol)],
                'Low': daily_data_for_all_symbols[('Low', symbol)],
                'Close': daily_data_for_all_symbols[('Close', symbol)],
                'Volume': daily_data_for_all_symbols[('Volume', symbol)]
            }
            self.history[symbol].append(symbol_data)
            technical_analyzer.update_indicators(self, symbol)
        
        self.logger.debug(f"Updated context for data: {self.current_date.strftime('%Y-%m-%d')}.")
        sma_20 = self.indicators['AAPL'].get('SMA_20')
        if sma_20 is not None:
            self.logger.info(f"[AAPL] Close: {self.history["AAPL"][-1]['Close']:.2f}, SMA_20: {sma_20:.2f}")
        else:
            self.logger.info(f"[AAPL] Close: {self.history['AAPL'][-1]['Close']:.2f}, SMA_20: Not yet available (History: {len(self.history['AAPL'])}/20)")