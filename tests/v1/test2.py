from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_2_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 2 Verification ---")

    symbols = ['AAPL', 'MSFT']
    start_date = '2023-01-01'
    end_date = '2023-01-31' # Test with one month of data
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 2 Verification Complete ---")
    logger.info("If you see daily log entries above, the event loop is working.")

if __name__ == "__main__":
    run_lesson_2_test()