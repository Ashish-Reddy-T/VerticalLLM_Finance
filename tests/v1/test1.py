from ...utils import setup_logger
from ...backtest_core import PortfolioManager, MarketDataContext

def run_lesson_1_test():
    # 1. Setup the logger
    # This is the first thing we do, so all subsequent actions are logged.
    logger = setup_logger()

    logger.info("--- Starting Lesson 1 Verification ---")

    # 2. Instantiate PortfolioManager
    initial_capital = 100000.0
    portfolio = PortfolioManager(initial_capital=initial_capital)
    logger.info(f"Successfully created PortfolioManager instance.")
    assert portfolio.cash == initial_capital

    # 3. Instantiate MarketDataContext
    symbols_to_test = ['AAPL', 'MSFT', 'GOOGL']
    context = MarketDataContext(symbols=symbols_to_test)
    logger.info(f"Successfully created MarketDataContext instance.")

    assert 'AAPL' in context.history
    assert 'MSFT' in context.indicators
    assert context.history['GOOGL'].maxlen == 252
    
    logger.info("--- Lesson 1 Verification Successful ---")
    logger.info("All core data structures and logging are set up correctly.")

if __name__ == "__main__":
    run_lesson_1_test()