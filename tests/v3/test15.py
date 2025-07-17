from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_15_test():
    """
    Verifies the multi-factor model is blending scores and generating
    a single, unified trading signal.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 15 Verification ---")

    symbols = ['META']
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

    logger.info("--- Lesson 15 Verification Complete ---")
    logger.info("Check the DEBUG logs for the 'Blended Score' message to see how the factors are combined.")

if __name__ == "__main__":
    run_lesson_15_test()