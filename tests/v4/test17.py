from ...backtest import BacktestEngine
from ...utils import setup_logger

def run_lesson_17_test():
    """
    Verifies that portfolio-level constraints (max exposure, max concentration)
    correctly block trades that would violate them.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 17 Verification ---")

    # We use aggressive risk to force the constraints to trigger
    # A 10% risk per trade will quickly try to use up our capital
    symbols = ['NVDA', 'AMD'] # Use two correlated stocks
    start_date = '2023-01-01'
    end_date = '2023-06-30'
    initial_capital = 100000.0

    engine = BacktestEngine(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )

    # We will override the engine's portfolio manager with a more aggressive one
    engine.portfolio_manager = engine.portfolio_manager.__class__(
        initial_capital,
        stop_loss_pct=0.10,
        portfolio_risk_pct=0.10, # Aggressive 10% risk per trade
        max_portfolio_exposure=0.60, # Low 60% exposure limit
        max_position_concentration=0.35 # Low 35% concentration limit
    )
    # Re-link the context to the new manager
    engine.market_context.portfolio_manager = engine.portfolio_manager


    engine.run()

    logger.info("--- Lesson 17 Verification Complete ---")
    logger.info("Check the log for 'BUY BLOCKED' messages due to exposure or concentration limits.")

if __name__ == "__main__":
    run_lesson_17_test()