from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_3_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 3 Verification ---")

    symbols = ['AAPL'] # Test with one symbol for clarity
    start_date = '2023-01-01'
    end_date = '2023-03-31' # Use three months to ensure the SMA gets calculated
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 3 Verification Complete ---")
    logger.info("Check the log file for daily 'SMA_20' values after the 20th day.")

if __name__ == "__main__":
    run_lesson_3_test()