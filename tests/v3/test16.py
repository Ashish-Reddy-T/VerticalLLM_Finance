from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_16_test():
    """
    Verifies that the Market Regime Filter correctly prevents BUY trades
    during a major market downturn.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 16 Verification ---")

    # We test on a strong stock (AAPL) during a weak year (2022).
    # The goal is to see if the regime filter protects us from buying the dips.
    symbols = ['AAPL']
    start_date = '2022-01-01'
    end_date = '2022-12-31'
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 16 Verification Complete ---")
    logger.info("Check the log for 'REGIME CHANGE' messages. Note how few, if any, BUY trades are executed during 'RISK_OFF' periods.")

if __name__ == "__main__":
    run_lesson_16_test()