from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_7_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 7 Verification ---")

    symbols = ['AAPL', 'MSFT']
    # Use a longer date range to see the quarterly/weekly triggers.
    start_date = '2023-01-01'
    end_date = '2023-04-30' 
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 7 Verification Complete ---")
    logger.info("Check the log for 'Indicators not ready' debug messages during the first ~20 days.")
    logger.info("Also check for 'Quarterly trigger' and 'Weekly trigger' info messages.")

if __name__ == "__main__":
    run_lesson_7_test()