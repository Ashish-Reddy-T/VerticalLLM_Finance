import logging

class SignalGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SignalGenerator initialized with a multi-factor model.")
        self.weights = {'technical': 0.6, 'fundamental': 0.2, 'sentiment': 0.2}
        self.buy_threshold = 0.3
        self.sell_threshold = -0.3

    def _get_technical_score(self, market_context, symbol) -> float:
        # ... no changes to this method ...
        required_indicators = ['SMA_20', 'RSI']
        if not all(market_context.indicators[symbol].get(ind) for ind in required_indicators):
            return 0.0
        current_price = market_context.history[symbol][-1]['Close']
        sma_20 = market_context.indicators[symbol]['SMA_20']
        rsi_value = market_context.indicators[symbol]['RSI']['value']
        trend_score = 0.5 if current_price > sma_20 else -0.5
        momentum_score = -((rsi_value - 50) / 50)
        technical_score = (trend_score * 0.7) + (momentum_score * 0.3)
        return technical_score

    def generate_signal(self, market_context, symbol: str, market_regime: str) -> str:
        """
        Main method to generate a signal, now accepting the market regime.
        """
        # --- 1. Master Regime Filter ---
        # If the market is in a "risk off" state, we do not permit any new BUY signals.
        # This acts as a global safety switch.
        if market_regime == 'RISK_OFF':
            has_position = symbol in market_context.portfolio_manager.positions
            # We can still generate SELL signals to exit positions, but no new entries.
            if not has_position:
                return 'HOLD'

        # --- 2. Blended Score Calculation (if regime allows) ---
        tech_score = self._get_technical_score(market_context, symbol)
        fundamental_score = market_context.fundamentals[symbol].get('score', 0.0)
        sentiment_score = market_context.sentiment[symbol].get('score', 0.0)
        
        final_score = (
            (tech_score * self.weights['technical']) +
            (fundamental_score * self.weights['fundamental']) +
            (sentiment_score * self.weights['sentiment'])
        )
        
        self.logger.debug(f"[{symbol}] Blended Score: {final_score:.2f} (Regime: {market_regime})")

        # --- 3. Final Signal Generation ---
        if final_score > self.buy_threshold:
            # We re-check the regime here as a final safeguard before returning BUY
            return 'BUY' if market_regime == 'RISK_ON' else 'HOLD'
        elif final_score < self.sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'