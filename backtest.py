import logging
import yfinance as yf
import pandas as pd
from .backtest_core import PortfolioManager, MarketDataContext
from .signal_generator import SignalGenerator
from .new_technical import IncrementalTechnicalAnalyzer
from .new_fundamental import FundamentalAnalyzer
from .new_sentimental import SentimentAnalyzer

class BacktestEngine:
    def __init__(self, symbols, start_date, end_date, initial_capital, strategy_params: dict):
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        
        # Unpack strategy parameters
        self.portfolio_manager = PortfolioManager(
            initial_capital,
            stop_loss_pct=strategy_params['stop_loss_pct'],
            portfolio_risk_pct=strategy_params['portfolio_risk_pct'],
            max_portfolio_exposure=0.90, # Keep these fixed for now
            max_position_concentration=0.50
        )
        self.signal_generator = SignalGenerator(
            buy_threshold=strategy_params['buy_threshold'],
            sell_threshold=strategy_params['sell_threshold'],
            technical_weight=0.6 # Keep fixed for now
        )

        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_analyzer = IncrementalTechnicalAnalyzer([('SMA', 20), ('RSI', 14), ('BBANDS', 20, 2)])
        self.market_context = MarketDataContext(symbols, history_window=250)
        self.market_context.portfolio_manager = self.portfolio_manager

    def _fetch_data(self):
        # ... no changes ...
        self.logger.info(f"Fetching historical data for {self.symbols} and SPY from {self.start_date} to {self.end_date}...")
        try:
            all_symbols = self.symbols + ['SPY']
            data = yf.download(all_symbols, start=self.start_date, end=self.end_date, auto_adjust=True)
            if data.empty: return None
            self.logger.info("Historical data fetched successfully.")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data: {e}")
            return None

    def run(self):
        # ... no changes to the start of this method ...
        self.logger.info(f"--- Starting Backtest Run for {self.symbols} ---")
        historical_data = self._fetch_data()
        if historical_data is None or 'SPY' not in historical_data['Close'].columns: return
        market_regime = 'NEUTRAL'
        for date, daily_bar in historical_data.iterrows():
            if pd.isna(daily_bar[('Close', 'SPY')]): continue
            self.market_context.update(date, daily_bar, self.technical_analyzer)
            if len(historical_data.loc[:date]) >= 200:
                spy_close = daily_bar[('Close', 'SPY')]
                spy_sma_200 = historical_data.loc[:date, ('Close', 'SPY')].rolling(window=200).mean().iloc[-1]
                new_regime = 'RISK_ON' if spy_close > spy_sma_200 else 'RISK_OFF'
                if new_regime != market_regime:
                    self.logger.info(f"REGIME CHANGE: Market is now {new_regime}")
                    market_regime = new_regime
            self.portfolio_manager.check_risk_limits(self.market_context)
            for symbol in self.symbols:
                final_signal = self.signal_generator.generate_signal(self.market_context, symbol, market_regime)    
                if final_signal == 'BUY':
                    current_price = self.market_context.history[symbol][-1]['Close']
                    # Pass the full context to the trade execution method
                    self.portfolio_manager.execute_trade(symbol, final_signal, current_price, date, self.market_context)
            self.portfolio_manager.update_equity_curve(self.market_context)
        self.logger.info("--- Backtest Run Completed ---")
        return self.portfolio_manager.get_summary()