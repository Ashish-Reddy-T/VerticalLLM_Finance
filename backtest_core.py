import logging, pandas as pd
from collections import deque

from new_technical import IncrementalTechnicalAnalyzer

class PortfolioManager:
    def __init__(self, initial_capital):    
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {'SYMBOL': {'shares': X, 'entry_price': Y}}
        self.trade_log = []
        self.equity_curve = []
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"PortfolioManager initialized with initial capital: ${self.initial_capital:,.2f}")
    
    def get_current_holdings_value(self, market_context):
        value = 0.0
        for symbol, position in self.positions.items():
            current_price = market_context.history[symbol][-1]['Close']
            value += position['shares'] * current_price
        return value
    
    def update_equity_curve(self, market_context):
        current_holding_value = self.get_current_holdings_value(market_context)
        total_equity = self.cash + current_holding_value
        self.equity_curve.append((market_context.current_date, total_equity))
        self.logger.debug(f"Equity updated on {market_context.current_date.strftime('%Y-%m-%d')}: ${total_equity:,.2f}")

    def execute_trade(self, symbol, signal, current_price, quantity, current_date):
        has_position = symbol in self.positions

        if signal == 'BUY':
            # (This is a simple long-only, no-pyramiding strategy). We'll look into advanced stuff afterwards
            if not has_position:
                cost = current_price * quantity
                if self.cash >= cost:
                    self.cash -= cost
                    self.positions[symbol] = {'shares': quantity, 'entry_price': current_price}
                    trade_record = f"BOUGHT {quantity} {symbol} @ ${current_price:.2f}"
                    self.logger.info(trade_record)
                    self.trade_log.append((current_date, trade_record))
                else:
                    self.logger.warning(f"[{symbol}] Insufficient cash to BUY")
            else:
                self.logger.debug(f"[{symbol}] HOLD signal received, but already have a position. HOLDING.")
        
        elif signal == "SELL":
            if has_position:
                proceeds = current_price * quantity
                self.cash += proceeds
                entry_price = self.positions[symbol]['entry_price']
                profit = (current_price - entry_price) * quantity
                trade_record = (f"SOLD {quantity} {symbol} @ ${current_price:.2f} | Entry: ${entry_price:.2f} | P/L: ${profit:,.2f}")
                self.logger.info(trade_record)
                self.trade_log.append((current_date, trade_record))
                del self.positions[symbol]
            else:
                self.logger.debug(f"[{symbol}] SELL signal received, but no position. No action taken.")

    def print_summary(self):
        final_equity = self.equity_curve[-1][1]
        total_return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        total_trades = len(self.trade_log)

        self.logger.info("--- Backtest Performance Summary ---")
        self.logger.info(f"Initial Capital:       ${self.initial_capital:,.2f}")
        self.logger.info(f"Final Portfolio Value: ${final_equity:,.2f}")
        self.logger.info(f"Total Return:          {total_return_pct:.2f}%")
        self.logger.info(f"Total Trades Executed: {total_trades}")
        self.logger.info("------------------------------------")
        
        self.logger.info("--- Detailed Trade Log ---")
        for trade_date, trade in self.trade_log:
            self.logger.info(f"{trade_date.strftime('%Y-%m-%d')}: {trade}")
        self.logger.info("--------------------------")

class MarketDataContext:
    def __init__(self, symbols, history_window = 252):
        self.symbols = symbols
        self.current_date = None
        self.history = {symbol: deque(maxlen=history_window) for symbol in symbols}
        self.indicators = {symbol: {} for symbol in symbols}
        self.fundamentals = {symbol: {} for symbol in symbols}
        self.sentiment = {symbol: {} for symbol in symbols}
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"MarketDataContext initialized for symbols: {self.symbols} with a history window of {history_window} days.")

    def update(self, date, daily_data_for_all_symbols, technical_analyzer):
        self.current_date = date
        for symbol in self.symbols:
            if pd.isna(daily_data_for_all_symbols[('Close', symbol)]):
                self.logger.debug(f"Skipping update for {symbol} on {date.strftime('%Y-%m-%d')} due to missing data.")
                continue
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