import logging

class SignalGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SignalGenerator initialized.")
        self.weights = {
            'technical': 0.7,
            'fundamental': 0.2,
            'sentiment': 0.1
        }

    def _is_indicator_ready(self, market_context, symbol, indicators):
        for indicator in indicators:
            if market_context.indicators[symbol].get(indicator) is None:
                return False
        return True
    

    def generate_signal(self, market_context, symbol):
        # 1. Warm-up check

        indicators = ['SMA_20']
        if not self._is_indicator_ready(market_context, symbol, indicators):
            self.logger.debug(f"[{symbol}] Indicators not ready. Holding.")
            return 'HOLD'
        
        # 2. Gated Analysis (Fundamental & Sentiment)
        current_date = market_context.current_date
        
        # Fundamental
        if current_date.is_quarter_start:
            self.logger.info(f"[{symbol}] Quarterly trigger: Running fundamental analysis.")
            # In a real system:
            # fundamental_score = fundamental_analyzer.analyze(symbol, current_date)
            # market_context.fundamentals[symbol] = fundamental_score
        
        # Sentimental
        if current_date.weekday() == 0:
            self.logger.info(f"[{symbol}] Weekly trigger: Running sentiment analysis.")
            # In a real system:
            # sentiment_score = sentiment_analyzer.analyze(symbol, current_date)
            # market_context.sentiments[symbol] = sentiment_score
        
        # 3. Technical Logic
        sma_20 = market_context.indicators[symbol]['SMA_20']
        current_price = market_context.history[symbol][-1]['Close']

        if current_price > sma_20:
            technical_signal = 'BUY'
        elif current_price < sma_20:
            technical_signal = 'SELL'
        else:
            technical_signal = 'HOLD'
        
        # For now, just technical_signal (we'll combine fundamental and sentimental later)
        final_signal = technical_signal
        return final_signal