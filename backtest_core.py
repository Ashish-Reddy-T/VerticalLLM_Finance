import logging
from collections import deque

class PortfolioManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {'SYMBOL': {'shares': X, 'entry_price': Y}}
        self.trade_log = []
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"PortfolioManager initialized with initial capital: ${self.initial_capital:,.2f}"
        )

class MarketDataContext:
    def __init__(self, symbols, history_window = 252):
        self.symbols = symbols
        self.current_date = None
        # Use a deque for efficient, fixed-size rolling data windows
        self.history = {symbol: deque(maxlen=history_window) for symbol in symbols}
        self.indicators = {symbol for symbol in symbols}
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"MarketDataContext initialized for symbols: {self.symbols} "
            f"with a history window of {history_window} days."
        )