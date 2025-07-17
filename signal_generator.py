import logging

class SignalGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SignalGenerator initialized.")

    def generate_signal(self, market_context, symbol):
        indicator_key = 'SMA_20'
        sma_20 = market_context.indicators[symbol].get(indicator_key)

        if sma_20 is None:
            return 'HOLD'
        
        current_price = market_context.history[symbol][-1]['Close']

        if current_price > sma_20:
            signal = 'BUY'
        elif current_price < sma_20:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        self.logger.info(f"[{symbol}] Signal: {signal} (Price: {current_price:.2f}, SMA_20: {sma_20:.2f})")
