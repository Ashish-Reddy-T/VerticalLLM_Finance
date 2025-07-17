from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_5_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 5 Verification ---")

    symbols = ['AAPL']
    start_date = '2023-01-01'
    end_date = '2023-03-31' # Extend to see more potential trades
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 5 Verification Complete ---")
    logger.info("Check the log file for BOUGHT/SOLD records and the final Trade Log summary.")

if __name__ == "__main__":
    run_lesson_5_test()