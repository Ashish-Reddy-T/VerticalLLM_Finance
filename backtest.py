import logging
import yfinance as yf
from .backtest_core import PortfolioManager, MarketDataContext
from .signal_generator import SignalGenerator
from .new_technical import IncrementalTechnicalAnalyzer
from .new_fundamental import FundamentalAnalyzer
from .new_sentimental import SentimentAnalyzer

class BacktestEngine:
    def __init__(self, symbols, start_date, end_date, initial_capital):
        # ... no changes to __init__ ...
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio_manager = PortfolioManager(initial_capital, stop_loss_pct=0.10, portfolio_risk_pct=0.01)
        self.signal_generator = SignalGenerator()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        indicators = [('SMA', 20), ('RSI', 14), ('BBANDS', 20, 2)]
        self.technical_analyzer = IncrementalTechnicalAnalyzer(indicators)
        self.market_context = MarketDataContext(symbols, history_window=50)

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
            
            # Gated Analysis Triggers
            if date.is_quarter_start:
                for symbol in self.symbols:
                    score = self.fundamental_analyzer.analyze(symbol, date)
                    self.market_context.fundamentals[symbol]['score'] = score
            if date.weekday() == 0:
                for symbol in self.symbols:
                    score = self.sentiment_analyzer.analyze(symbol, self.market_context)
                    self.market_context.sentiment[symbol]['score'] = score

            # Risk Management
            self.portfolio_manager.check_risk_limits(self.market_context)

            # --- Unified Signal Generation & Execution ---
            for symbol in self.symbols:
                # Call the main generate_signal method which now does everything
                final_signal = self.signal_generator.generate_signal(self.market_context, symbol)
                
                if final_signal != 'HOLD':
                    self.logger.info(f"[{symbol}] Final Signal Generated: {final_signal}")

                if final_signal in ['BUY', 'SELL']:
                    current_price = self.market_context.history[symbol][-1]['Close']
                    self.portfolio_manager.execute_trade(symbol, final_signal, current_price, date)
            
            self.portfolio_manager.update_equity_curve(self.market_context)
            
        self.logger.info("--- Backtest Run Completed ---")
        self.portfolio_manager.print_summary()