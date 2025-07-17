import logging
from datetime import datetime
from collections import deque
import pandas as pd
from .new_technical import IncrementalTechnicalAnalyzer

class PortfolioManager:
    """
    Manages the portfolio, now with an understanding of inter-stock correlation risk.
    """
    def __init__(self, initial_capital: float, stop_loss_pct: float, portfolio_risk_pct: float,
                max_portfolio_exposure: float, max_position_concentration: float,
                correlation_threshold: float = 0.80):

        self.initial_capital: float = initial_capital
        self.cash: float = initial_capital
        self.positions: dict = {}
        self.trade_log: list = []
        self.equity_curve: list = []
        self.logger = logging.getLogger(__name__)

        self.stop_loss_pct = stop_loss_pct
        self.portfolio_risk_pct = portfolio_risk_pct
        self.max_portfolio_exposure = max_portfolio_exposure
        self.max_position_concentration = max_position_concentration
        self.correlation_threshold = correlation_threshold

        self.logger.info(f"PortfolioManager initialized with initial capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"Risk settings: Trailing Stop={self.stop_loss_pct:.1%}, Trade Risk={self.portfolio_risk_pct:.1%}, "
                       f"Max Exposure={self.max_portfolio_exposure:.1%}, Max Position Size={self.max_position_concentration:.1%}, "
                       f"Correlation Threshold={self.correlation_threshold:.1%}")

    def _check_correlation_risk(self, new_symbol: str, market_context) -> bool:
        if not self.positions:
            return False

        price_data = {}
        price_data[new_symbol] = [bar['Close'] for bar in market_context.history[new_symbol]]
        for symbol in self.positions.keys():
            price_data[symbol] = [bar['Close'] for bar in market_context.history[symbol]]
        
        # Ensure all lists have the same length by padding shorter ones if necessary
        max_len = max(len(v) for v in price_data.values())
        for symbol in price_data:
            if len(price_data[symbol]) < max_len:
                padding = [None] * (max_len - len(price_data[symbol]))
                price_data[symbol] = padding + price_data[symbol]

        price_df = pd.DataFrame(price_data)
        corr_matrix = price_df.corr()
        
        for existing_symbol in self.positions.keys():
            correlation = corr_matrix.loc[new_symbol, existing_symbol]
            if correlation > self.correlation_threshold:
                self.logger.warning(f"[{new_symbol}] BUY BLOCKED: High correlation with existing position '{existing_symbol}'. "
                                  f"Correlation: {correlation:.2%}")
                return True
        return False

    def execute_trade(self, symbol: str, signal: str, price: float, current_date: datetime, market_context, triggered_by='SIGNAL'):
        has_position = symbol in self.positions

        if signal == 'BUY' and not has_position:
            if self._check_correlation_risk(symbol, market_context):
                return
            
            stop_loss_price = price * (1 - self.stop_loss_pct)
            total_equity = self.cash + self.get_current_holdings_value(market_context)
            quantity = self.calculate_position_size(symbol, price, stop_loss_price, total_equity)

            if quantity == 0: return
            cost = price * quantity
            
            projected_exposure = (self.get_current_holdings_value(market_context) + cost) / total_equity
            if projected_exposure > self.max_portfolio_exposure:
                self.logger.warning(f"[{symbol}] BUY BLOCKED: Exceeds max exposure.")
                return

            projected_concentration = cost / total_equity
            if projected_concentration > self.max_position_concentration:
                self.logger.warning(f"[{symbol}] BUY BLOCKED: Exceeds max concentration.")
                return

            if self.cash >= cost:
                self.cash -= cost
                self.positions[symbol] = { 'shares': quantity, 'entry_price': price, 'stop_loss': stop_loss_price, 'high_water_mark': price }
                trade_record = f"BOUGHT {quantity} {symbol} @ ${price:.2f} (SL: {stop_loss_price:.2f})"
                self.logger.info(trade_record)
                self.trade_log.append((current_date, trade_record))

        elif signal == 'SELL' and has_position:
            quantity = self.positions[symbol]['shares']
            proceeds = price * quantity
            self.cash += proceeds
            entry_price = self.positions[symbol]['entry_price']
            profit = (price - entry_price) * quantity
            trade_record = f"SOLD {quantity} {symbol} @ ${price:.2f} | Entry: ${entry_price:.2f} | P/L: ${profit:,.2f} | Trigger: {triggered_by}"
            self.logger.info(trade_record)
            self.trade_log.append((current_date, trade_record))
            del self.positions[symbol]
    
    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss_price: float, total_equity: float) -> int:
        amount_to_risk = total_equity * self.portfolio_risk_pct
        risk_per_share = entry_price - stop_loss_price
        if risk_per_share <= 0: return 0
        quantity = int(amount_to_risk / risk_per_share)
        self.logger.info(f"[{symbol}] Position Size Calculation: Amount to Risk=${amount_to_risk:.2f}, Risk/Share=${risk_per_share:.2f} -> Quantity={quantity}")
        return quantity

    def get_current_holdings_value(self, market_context=None) -> float:
        value = 0.0
        for symbol, position in self.positions.items():
            if market_context and len(market_context.history[symbol]) > 0:
                current_price = market_context.history[symbol][-1]['Close']
            else:
                current_price = position['entry_price']
            value += position['shares'] * current_price
        return value

    def check_risk_limits(self, market_context):
        forced_exits = []
        for symbol, position in list(self.positions.items()): # Use list to allow modification during iteration
            current_price = market_context.history[symbol][-1]['Close']
            new_high_water_mark = max(position['high_water_mark'], current_price)
            if new_high_water_mark > position['high_water_mark']:
                position['high_water_mark'] = new_high_water_mark
                position['stop_loss'] = new_high_water_mark * (1 - self.stop_loss_pct)
            if current_price <= position['stop_loss']:
                self.logger.info(f"[{symbol}] TRAILING STOP-LOSS TRIGGERED. Price: ${current_price:.2f}, Stop: ${position['stop_loss']:.2f}")
                forced_exits.append(symbol)
        for symbol in forced_exits:
            current_price = market_context.history[symbol][-1]['Close']
            self.execute_trade(symbol, 'SELL', current_price, market_context.current_date, market_context, triggered_by='TRAIL_STOP')

    def update_equity_curve(self, market_context):
        current_holdings_value = self.get_current_holdings_value(market_context)
        total_equity = self.cash + current_holdings_value
        self.equity_curve.append((market_context.current_date, total_equity))
    
    def get_summary(self):
        if not self.equity_curve:
            return {'total_return_pct': 0, 'total_trades': 0}
        final_equity = self.equity_curve[-1][1]
        total_return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        return {
            'total_return_pct': total_return_pct,
            'total_trades': len(self.trade_log)
        }

    def print_summary(self):
        # ... (unchanged)
        if not self.equity_curve: self.logger.warning("No equity data to generate summary."); return
        final_equity = self.equity_curve[-1][1]
        total_return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        total_trades = len(self.trade_log)
        self.logger.info("--- Backtest Performance Summary ---")
        self.logger.info(f"Initial Capital:       ${self.initial_capital:,.2f}")
        self.logger.info(f"Final Portfolio Value: ${final_equity:,.2f}")
        self.logger.info(f"Total Return:          {total_return_pct:.2f}%")
        self.logger.info(f"Total Trades Executed: {total_trades}")
        self.logger.info("--- Detailed Trade Log ---")
        for trade_date, trade in self.trade_log:
            self.logger.info(f"{trade_date.strftime('%Y-%m-%d')}: {trade}")


# --- THIS CLASS WAS MISSING IN THE PREVIOUS RESPONSE ---
class MarketDataContext:
    def __init__(self, symbols, history_window=252):
        self.symbols = symbols
        self.current_date = None
        self.history = {symbol: deque(maxlen=history_window) for symbol in symbols}
        self.indicators = {symbol: {} for symbol in symbols}
        self.fundamentals = {symbol: {} for symbol in symbols}
        self.sentiment = {symbol: {} for symbol in symbols}
        self.portfolio_manager = None
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"MarketDataContext initialized for symbols: {self.symbols} with a history window of {history_window} days.")

    def update(self, date: datetime, daily_data_for_all_symbols: pd.Series, technical_analyzer: IncrementalTechnicalAnalyzer):
        self.current_date = date
        for symbol in self.symbols:
            if pd.isna(daily_data_for_all_symbols.get(('Close', symbol))): continue
            symbol_data = {
                'Open': daily_data_for_all_symbols[('Open', symbol)],
                'High': daily_data_for_all_symbols[('High', symbol)],
                'Low': daily_data_for_all_symbols[('Low', symbol)],
                'Close': daily_data_for_all_symbols[('Close', symbol)],
                'Volume': daily_data_for_all_symbols[('Volume', symbol)]
            }
            self.history[symbol].append(symbol_data)
            technical_analyzer.update_indicators(self, symbol)