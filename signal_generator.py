import logging

class SignalGenerator:
    """
    Generates a final trading signal by blending technical, fundamental,
    and sentiment scores into a single, weighted score.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SignalGenerator initialized with a multi-factor model.")
        # Define the weights for each component of our model
        self.weights = {
            'technical': 0.6,
            'fundamental': 0.2,
            'sentiment': 0.2
        }
        # Define the threshold for the final blended score to trigger a trade
        self.buy_threshold = 0.3
        self.sell_threshold = -0.3

    def _get_technical_score(self, market_context, symbol) -> float:
        """Calculates a technical score from -1.0 to 1.0."""
        required_indicators = ['SMA_20', 'RSI']
        if not all(market_context.indicators[symbol].get(ind) for ind in required_indicators):
            return 0.0

        current_price = market_context.history[symbol][-1]['Close']
        sma_20 = market_context.indicators[symbol]['SMA_20']
        rsi_value = market_context.indicators[symbol]['RSI']['value']

        # Trend component (-0.5 to 0.5)
        trend_score = 0.5 if current_price > sma_20 else -0.5
        # Momentum component (-0.5 to 0.5, inverted)
        # We penalize extreme RSI values (overbought/oversold)
        momentum_score = -((rsi_value - 50) / 50) # Scales RSI from 0-100 to 1 to -1

        # Combine technical factors (can be more complex in the future)
        # We give more weight to the trend
        technical_score = (trend_score * 0.7) + (momentum_score * 0.3)
        return technical_score


    def generate_signal(self, market_context, symbol: str) -> str:
        """The main method to generate a blended signal."""
        # 1. Calculate the Technical Score
        tech_score = self._get_technical_score(market_context, symbol)

        # 2. Get the latest Fundamental Score from the context
        # If no score is available yet, default to a neutral 0.0
        fundamental_score = market_context.fundamentals[symbol].get('score', 0.0)

        # 3. Get the latest Sentiment Score from the context
        sentiment_score = market_context.sentiment[symbol].get('score', 0.0)

        # 4. Calculate the Final Blended Score
        final_score = (
            (tech_score * self.weights['technical']) +
            (fundamental_score * self.weights['fundamental']) +
            (sentiment_score * self.weights['sentiment'])
        )

        self.logger.debug(f"[{symbol}] Blended Score: {final_score:.2f} "
                        f"(T: {tech_score:.2f}, F: {fundamental_score:.2f}, S: {sentiment_score:.2f})")

        # 5. Generate final signal based on thresholds
        if final_score > self.buy_threshold:
            return 'BUY'
        elif final_score < self.sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'