import logging
import numpy as np

class SentimentAnalyzer:
    """
    Analyzes market sentiment for a given symbol.
    In this version, it uses recent price momentum as a simple proxy for sentiment.
    It's designed to be called infrequently (e.g., weekly).
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze(self, symbol: str, market_context) -> float:
        """
        Generates a normalized sentiment score based on recent price action.

        Returns:
            float: A normalized sentiment score from -1.0 to 1.0.
        """
        self.logger.info(f"[{symbol}] Performing weekly sentiment analysis...")
        
        # We need at least 5 days of data to measure weekly momentum
        history = market_context.history[symbol]
        if len(history) < 5:
            self.logger.debug(f"[{symbol}] Not enough data for sentiment analysis (need 5 days).")
            return 0.0 # Return neutral score

        try:
            # Get the last 5 closing prices from the history deque
            recent_closes = [bar['Close'] for bar in list(history)[-5:]]
            
            # Simple proxy: 5-day price change percentage
            price_change_pct = (recent_closes[-1] - recent_closes[0]) / recent_closes[0]
            
            # Normalize and scale the score. We'll cap the effect at a 10% move.
            # A 10% or higher 5-day gain = +1.0 score. A 10% or higher loss = -1.0 score.
            sentiment_score = np.clip(price_change_pct / 0.10, -1.0, 1.0)

            self.logger.info(f"[{symbol}] Sentiment Score: {sentiment_score:.2f} (based on 5-day price change of {price_change_pct:.2%})")
            return sentiment_score

        except Exception as e:
            self.logger.error(f"[{symbol}] Error during sentiment analysis: {e}")
            return 0.0