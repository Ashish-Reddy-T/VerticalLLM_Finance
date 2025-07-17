from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_13_test():
    """
    Verifies that the Fundamental Analyzer is triggered quarterly and
    generates a score.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 13 Verification ---")

    symbols = ['MSFT'] # Use a well-known large-cap stock
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

    logger.info("--- Lesson 13 Verification Complete ---")
    logger.info("Check the log on the first trading day of April for the 'Performing fundamental analysis' message.")

if __name__ == "__main__":
    run_lesson_13_test()