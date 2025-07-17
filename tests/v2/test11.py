from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_11_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 11 Verification ---")

    symbols = ['NVDA']
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

    logger.info("--- Lesson 11 Verification Complete ---")
    logger.info("Check the log for 'Position Size Calculation' messages.")
    logger.info("The 'BOUGHT' quantity should no longer be a fixed 10 shares.")

if __name__ == "__main__":
    run_lesson_11_test()