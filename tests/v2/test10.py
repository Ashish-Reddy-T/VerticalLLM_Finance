from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_10_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 10 Verification ---")

    # NVDA had a massive run-up in H1 2023, perfect for testing trailing stops.
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

    logger.info("--- Lesson 10 Verification Complete ---")
    logger.info("Check the DEBUG logs for 'Trailing stop adjusted up' messages.")
    logger.info("And check the final trade log for a sale triggered by 'TRAIL_STOP'.")

if __name__ == "__main__":
    run_lesson_10_test()