import logging
import yfinance as yf
from backtest_core import PortfolioManager, MarketDataContext
from new_technical import IncrementalTechnicalAnalyzer

class BacktestEngine:
    def __init__(self, symbols, start_date, end_date, initial_capital):
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        
        self.portfolio_manager = PortfolioManager(initial_capital)
        # In later lessons, we will add the signal generator and other components here.
        # self.signal_generator = SignalGenerator() 
        indicators = [('SMA', 20)]
        self.technical_analyzer = IncrementalTechnicalAnalyzer(indicators)
        
        # NOTE: The history window should be large enough for the longest indicator we plan to use.
        self.market_context = MarketDataContext(symbols, history_window=50) 

    def _fetch_data(self):
        self.logger.info(f"Fetching historical data for {self.symbols} from {self.start_date} to {self.end_date}...")
        try:
            data = yf.download(self.symbols, start=self.start_date, end=self.end_date)
            if data.empty:
                self.logger.error("Data fetching failed - Tickers or Date Range may be incorrect.")
                return None
            self.logger.info("Historical data fetched successfully.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data: {e}")
            return None

    def run(self):
        self.logger.info(f"--- Starting Backtest Run for {self.symbols} ---")
        
        historical_data = self._fetch_data()
        if historical_data is None:
            return

        for date, daily_bar in historical_data.iterrows():
            self.logger.info(f"--- Processing Date: {date.strftime('%Y-%m-%d')} ---")
            
            # 1. Update the market context with the new day's data.
            self.market_context.update(date, daily_bar, self.technical_analyzer)
            
            # 2. (Future Lesson) Generate signals based on the new context.
            # signal = self.signal_generator.generate_signal(self.market_context)

            # 3. (Future Lesson) Execute trades based on the signal.
            # self.portfolio_manager.execute_trade(signal)
            
        self.logger.info("--- Backtest Run Completed ---")
        # 4. (Future Lesson) Print final portfolio summary.
        # self.portfolio_manager.print_summary()