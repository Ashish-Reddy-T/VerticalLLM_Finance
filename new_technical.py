import logging, pandas as pd

class IncrementalTechnicalAnalyzer:
    def __init__(self, indicators_to_calculate):
        self.logger = logging.getLogger(__name__)
        self.indicators_to_calculate = indicators_to_calculate
        self.logger.info(f"IncrementalTechnicalAnalyzer initialized for: {self.indicators_to_calculate}")

    def update_indicators(self, market_context, symbol):
        for indicator_info in self.indicators_to_calculate:
            indicator_type = indicator_info[0]
            period = indicator_info[1]

            if indicator_type == "SMA":
                self._update_sma(market_context, symbol, period)
            elif indicator_type == "RSI":
                self._update_rsi(market_context, symbol, period)
            elif indicator_type == "BBANDS":
                self._update_bbands(market_context, symbol, period, std_dev=indicator_info[2])
            
        
    def _update_sma(self, market_context, symbol, period):
        history = market_context.history[symbol]
        indicator_key = f"SMA_{period}"
        if len(history) < period:
            market_context.indicators[symbol][indicator_key] = None
            return
        new_price = history[-1]['Close']
        # Get the previous day's SMA from our context
        # On the first day we have enough data, the previous SMA is None.
        prev_sma = market_context.indicators[symbol][indicator_key]
        if prev_sma is None:
            current_sum = sum(bar['Close'] for bar in history)
            new_sma = current_sum / period
            self.logger.debug(f"[{symbol}] First SMA_{period} calculation: {new_sma:.2f}")
        else:
            old_price = history[0]['Close']
            new_sma = prev_sma - (old_price / period) + (new_price / period)
            self.logger.debug(f"[{symbol}] Incremental SMA_{period} update: {new_sma:.2f}")

        market_context.indicators[symbol][indicator_key] = new_sma
    
    def _update_rsi(self, market_context, symbol, period):
        history = market_context.history[symbol]
        indicator_key = 'RSI'
        
        # We need at least period + 1 bars to calculate the first RSI
        if len(history) < period + 1:
            market_context.indicators[symbol][indicator_key] = None
            return

        # RSI calculation needs price changes, so we need the last two prices.
        price_today = history[-1]['Close']
        price_yesterday = history[-2]['Close']
        change = price_today - price_yesterday
        
        gain = max(change, 0)
        loss = abs(min(change, 0))

        # Get the previous state from our context
        prev_rsi_state = market_context.indicators[symbol][indicator_key]

        if prev_rsi_state is None:
            # First time calculation: Wilder's smoothing method
            # We need to look at the last `period` changes.
            changes = [history[i]['Close'] - history[i-1]['Close'] for i in range(1, len(history))]
            initial_gains = sum(max(c, 0) for c in changes)
            initial_losses = sum(abs(min(c, 0)) for c in changes)
            
            avg_gain = initial_gains / period
            avg_loss = initial_losses / period
        else:
            # Incremental update using Wilder's smoothing
            prev_avg_gain = prev_rsi_state['avg_gain']
            prev_avg_loss = prev_rsi_state['avg_loss']
            
            avg_gain = ((prev_avg_gain * (period - 1)) + gain) / period
            avg_loss = ((prev_avg_loss * (period - 1)) + loss) / period

        if avg_loss == 0:
            rsi = 100 # Avoid division by zero
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        market_context.indicators[symbol][indicator_key] = {
            'value': rsi,
            'avg_gain': avg_gain,
            'avg_loss': avg_loss
        }
        self.logger.debug(f"[{symbol}] RSI updated: {rsi:.2f}")

    
    def _update_bbands(self, market_context, symbol, period, std_dev):
        history = market_context.history[symbol]
        indicator_key = 'BBANDS'

        if len(history) < period:
            market_context.indicators[symbol][indicator_key] = None
            return

        close_prices = [bar['Close'] for bar in history]
        
        series = pd.Series(close_prices)
        middle_band = series.rolling(window=period).mean().iloc[-1]
        std_deviation = series.rolling(window=period).std().iloc[-1]
        
        upper_band = middle_band + (std_deviation * std_dev)
        lower_band = middle_band - (std_deviation * std_dev)

        market_context.indicators[symbol][indicator_key] = {
            'middle': middle_band,
            'upper': upper_band,
            'lower': lower_band
        }
        self.logger.debug(f"[{symbol}] BBands updated: L={lower_band:.2f} M={middle_band:.2f} U={upper_band:.2f}")