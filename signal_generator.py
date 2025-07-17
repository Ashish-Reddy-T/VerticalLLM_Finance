import logging

class SignalGenerator:
    """
    Generates trading signals, now with a volatility filter to avoid
    choppy market conditions.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SignalGenerator initialized.")

    def _is_indicator_ready(self, market_context, symbol: str, indicators: list) -> bool:
        for indicator in indicators:
            if market_context.indicators[symbol].get(indicator) is None:
                return False
        return True

    def generate_signal(self, market_context, symbol: str) -> str:
        required_indicators = ['SMA_20', 'RSI', 'BBANDS']
        if not self._is_indicator_ready(market_context, symbol, required_indicators):
            self.logger.debug(f"[{symbol}] Indicators not ready. Holding.")
            return 'HOLD'

        # Retrieve indicator values
        current_price = market_context.history[symbol][-1]['Close']
        sma_20 = market_context.indicators[symbol]['SMA_20']
        rsi_value = market_context.indicators[symbol]['RSI']['value']
        bbands = market_context.indicators[symbol]['BBANDS']

        # --- 1. Volatility Filter (The New Logic) ---
        # Calculate Bollinger Band Width Percentage
        band_width_pct = (bbands['upper'] - bbands['lower']) / bbands['middle']
        
        # Define a threshold. If volatility is too high (e.g., bands are more than 15% wide),
        # we do not take new trades. This is our "choppiness" filter.
        volatility_threshold = 0.15 

        if band_width_pct > volatility_threshold:
            self.logger.info(f"[{symbol}] VOLATILITY FILTER ENGAGED. Band Width: {band_width_pct:.2%}. Forcing HOLD.")
            # If we are in a position, the trailing stop will still protect us.
            # But we do not enter any *new* trades in this volatile environment.
            has_position = symbol in market_context.portfolio_manager.positions # A bit of a reach, but for clarity
            if not has_position:
                return 'HOLD'

        # --- 2. Existing Strategy Logic ---
        # This logic now only runs if the market is not too volatile.
        is_uptrend = current_price > sma_20
        is_not_overbought = rsi_value < 70
        
        if is_uptrend and is_not_overbought:
            signal = 'BUY'
        elif not is_uptrend:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        return signal