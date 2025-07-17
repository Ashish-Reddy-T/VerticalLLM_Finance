import logging

class SignalGenerator:
    """
    Generates a raw technical signal. It no longer contains complex logic,
    which will be moved to the BacktestEngine.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SignalGenerator initialized.")

    def _is_indicator_ready(self, market_context, symbol: str, indicators: list) -> bool:
        for indicator in indicators:
            if market_context.indicators[symbol].get(indicator) is None:
                return False
        return True

    def generate_technical_signal(self, market_context, symbol: str) -> str:
        """This method now only generates the raw technical signal."""
        required_indicators = ['SMA_20', 'RSI', 'BBANDS']
        if not self._is_indicator_ready(market_context, symbol, required_indicators):
            return 'HOLD'

        current_price = market_context.history[symbol][-1]['Close']
        sma_20 = market_context.indicators[symbol]['SMA_20']
        
        if current_price > sma_20:
            return 'BUY'
        elif current_price < sma_20:
            return 'SELL'
        else:
            return 'HOLD'