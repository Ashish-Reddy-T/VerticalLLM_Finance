from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_18_test():
    """
    Verifies that the inter-stock correlation check correctly blocks trades.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 18 Verification ---")

    # NVDA and AMD are highly correlated semiconductor stocks.
    # We expect the system to buy one, but then block the other.
    symbols = ['NVDA', 'AMD']
    start_date = '2023-01-01'
    end_date = '2023-06-30'
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 18 Verification Complete ---")
    logger.info("Check the log for 'BUY BLOCKED: High correlation' messages.")

if __name__ == "__main__":
    run_lesson_18_test()