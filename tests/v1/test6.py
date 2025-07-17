from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_6_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 6 Verification ---")

    symbols = ['AAPL', 'MSFT', 'GOOG']
    start_date = '2023-01-01'
    end_date = '2023-03-31'
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 6 Verification Complete ---")
    logger.info("Check the log for the final 'Backtest Performance Summary'.")

if __name__ == "__main__":
    run_lesson_6_test()