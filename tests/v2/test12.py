from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_12_test():
    logger = setup_logger()
    logger.info("--- Starting Lesson 12 Verification ---")

    # GLD (Gold ETF) was famously choppy/range-bound in late 2023.
    # An ideal candidate to test if our volatility filter works.
    symbols = ['GLD']
    start_date = '2023-06-01'
    end_date = '2023-12-31'
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    engine.run()

    logger.info("--- Lesson 12 Verification Complete ---")
    logger.info("Check the log for 'VOLATILITY FILTER ENGAGED' messages.")
    logger.info("The number of trades should be very low, even if signals were generated.")

if __name__ == "__main__":
    run_lesson_12_test()