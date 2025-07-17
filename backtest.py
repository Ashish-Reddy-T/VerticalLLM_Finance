import logging
import yfinance as yf
from .backtest_core import PortfolioManager, MarketDataContext
from .new_technical import IncrementalTechnicalAnalyzer
from .signal_generator import SignalGenerator

class BacktestEngine:
    def __init__(self, symbols, start_date, end_date, initial_capital):
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        
        self.portfolio_manager = PortfolioManager(initial_capital, stop_loss_pct=0.10, portfolio_risk_pct=0.01)
        self.signal_generator = SignalGenerator()
        indicators = [('SMA', 20), ('RSI', 14), ('BBANDS', 20, 2)]
        self.technical_analyzer = IncrementalTechnicalAnalyzer(indicators)
        self.market_context = MarketDataContext(symbols, history_window=50)
        # Give market context access to portfolio manager to check for positions
        self.market_context.portfolio_manager = self.portfolio_manager

    def _fetch_data(self):
        # ... no changes ...
        self.logger.info(f"Fetching historical data for {self.symbols} from {self.start_date} to {self.end_date}...")
        try:
            data = yf.download(self.symbols, start=self.start_date, end=self.end_date, auto_adjust=True)
            if data.empty: return None
            self.logger.info("Historical data fetched successfully.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data: {e}")
            return None

    def run(self):
        self.logger.info(f"--- Starting Backtest Run for {self.symbols} ---")
        
        historical_data = self._fetch_data()
        if historical_data is None: return

        for date, daily_bar in historical_data.iterrows():
            self.market_context.update(date, daily_bar, self.technical_analyzer)
            
            self.portfolio_manager.check_risk_limits(self.market_context)

            for symbol in self.symbols:
                # The signal generator now needs the market context
                signal = self.signal_generator.generate_signal(self.market_context, symbol)
                if signal in ['BUY', 'SELL']:
                    current_price = self.market_context.history[symbol][-1]['Close']
                    self.portfolio_manager.execute_trade(symbol, signal, current_price, date)
            
            self.portfolio_manager.update_equity_curve(self.market_context)
            
        self.logger.info("--- Backtest Run Completed ---")
        self.portfolio_manager.print_summary()