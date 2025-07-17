import logging
import yfinance as yf

class FundamentalAnalyzer:
    """
    Analyzes a company's fundamental data to generate a normalized score.
    This analyzer is designed to be called infrequently (e.g., quarterly).
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Define weights for different fundamental categories
        self.category_weights = {
            'valuation': 0.4,
            'profitability': 0.3,
            'health': 0.3
        }

    def _normalize(self, value, low, high, invert=False):
        """Normalizes a value to a -1.0 to 1.0 scale."""
        if value is None:
            return 0.0
        # Clamp the value to be within the low/high bounds
        value = max(low, min(value, high))
        
        # Normalize to 0-1 range
        normalized = (value - low) / (high - low)
        
        # Scale to -1 to 1 range
        scaled = (normalized * 2) - 1
        
        return -scaled if invert else scaled

    def analyze(self, symbol: str, current_date):
        """
        Fetches and analyzes fundamental data for a given symbol.

        Returns:
            float: A normalized fundamental score from -1.0 to 1.0.
        """
        self.logger.info(f"[{symbol}] Performing fundamental analysis for date: {current_date.strftime('%Y-%m-%d')}")
        try:
            ticker = yf.Ticker(symbol)
            # .info is a snapshot, which is appropriate for fundamental data
            info = ticker.info
        except Exception as e:
            self.logger.error(f"[{symbol}] Could not fetch yfinance info: {e}")
            return 0.0 # Return neutral score on error

        # --- 1. Valuation Score ---
        # For P/E, lower is better (so we invert the normalization)
        pe_ratio = info.get('trailingPE')
        valuation_score = self._normalize(pe_ratio, low=10, high=40, invert=True)

        # --- 2. Profitability Score ---
        # For ROE, higher is better
        roe = info.get('returnOnEquity')
        if roe: roe *= 100 # Convert to percentage
        profitability_score = self._normalize(roe, low=0, high=25)

        # --- 3. Financial Health Score ---
        # For Debt/Equity, lower is better (invert)
        debt_to_equity = info.get('debtToEquity')
        health_score = self._normalize(debt_to_equity, low=0, high=100, invert=True)

        # --- 4. Combine Scores with Weights ---
        final_score = (
            (valuation_score * self.category_weights['valuation']) +
            (profitability_score * self.category_weights['profitability']) +
            (health_score * self.category_weights['health'])
        )

        self.logger.info(f"[{symbol}] Fundamental Score: {final_score:.2f} "
                       f"(Valuation: {valuation_score:.2f}, Profitability: {profitability_score:.2f}, Health: {health_score:.2f})")

        return final_score