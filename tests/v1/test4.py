from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_4_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 4 Verification ---")

    symbols = ['AAPL'] # Test with one symbol for clarity
    start_date = '2023-01-01'
    end_date = '2023-02-28' # Keep the test period short
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 4 Verification Complete ---")
    logger.info("Check the log file for 'Signal: BUY' or 'Signal: SELL' messages.")

if __name__ == "__main__":
    run_lesson_4_test()