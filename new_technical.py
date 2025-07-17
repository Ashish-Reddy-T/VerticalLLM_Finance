import logging

class IncrementalTechnicalAnalyzer:
    def __init__(self, indicators_to_calculate):
        self.logger = logging.getLogger(__name__)
        self.indicators_to_calculate = indicators_to_calculate
        self.logger.info(f"IncrementalTechnicalAnalyzer initialized for: {self.indicators_to_calculate}")

    def update_indicators(self, market_context, symbol):
        for indicator_type, period in self.indicators_to_calculate:
            if indicator_type == 'SMA':
                self._update_sma(market_context, symbol, period)
            # In future lessons, we would add:
            # elif indicator_type == 'RSI':
            #     self._update_rsi(market_context, symbol, period)
        
    def _update_sma(self, market_context, symbol, period):
        history = market_context.history[symbol]
        indicator_key = f"SMA_{period}"

        if len(history) < period:
            market_context.indicators[symbol][indicator_key] = None
            return

        new_price = history[-1]['Close']

        # Get the previous day's SMA from our context
        # On the first day we have enough data, the previous SMA is None.
        prev_sma = market_context.indicators[symbol].get(indicator_key)

        if prev_sma is None:
            # First time calculation: compute the full sum
            # This happens only once per symbol per SMA period.
            current_sum = sum(bar['Close'] for bar in history)
            new_sma = current_sum / period
            self.logger.debug(f"[{symbol}] First SMA_{period} calculation: {new_sma:.2f}")
        else:
            # Incremental update (the O(1) magic)
            # Get the price that just fell off the deque
            old_price = history[0]['Close'] # This works because the new price is at the end, old at the start
            
            # Efficiently update the SMA
            new_sma = prev_sma - (old_price / period) + (new_price / period)
            self.logger.debug(f"[{symbol}] Incremental SMA_{period} update: {new_sma:.2f}")

        # Store the newly calculated SMA back into the market context
        market_context.indicators[symbol][indicator_key] = new_sma