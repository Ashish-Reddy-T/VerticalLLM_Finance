from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_14_test():
    """
    Verifies that the Sentiment Analyzer is triggered weekly and
    generates a score.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 14 Verification ---")

    symbols = ['TSLA'] # Use a stock known for sentiment-driven moves
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

    logger.info("--- Lesson 14 Verification Complete ---")
    logger.info("Check the log on Mondays for 'Performing weekly sentiment analysis' messages and the resulting score.")

if __name__ == "__main__":
    run_lesson_14_test()