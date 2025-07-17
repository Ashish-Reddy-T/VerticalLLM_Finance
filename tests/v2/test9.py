from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_9_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 9 Verification ---")

    # Use a volatile stock like TSLA over a specific period known for swings
    symbols = ['TSLA']
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

    logger.info("--- Lesson 9 Verification Complete ---")
    logger.info("Check the trade log for trades closed by 'RISK_MANAGER'.")

if __name__ == "__main__":
    run_lesson_9_test()