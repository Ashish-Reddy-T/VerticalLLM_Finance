from ...optimizer import Optimizer
from ...utils import setup_logger

def run_lesson_19_test():
    """
    Verifies that the Optimizer can run multiple backtests and find the best parameters.
    This version uses a more aggressive grid to test system sensitivity.
    """
    logger = setup_logger()
    logger.info("--- Starting Lesson 19 Verification (Sensitivity Analysis) ---")

    symbols = ['NVDA']
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    initial_capital = 100000.0

    optimizer = Optimizer(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )
    
    # --- The only change is in the parameter grid ---
    # We are adding much lower thresholds to force the system to trade.
    aggressive_param_grid = {
        'stop_loss_pct': [0.10, 0.15],
        'portfolio_risk_pct': [0.02],
        'buy_threshold': [0.1, 0.2, 0.3],     # Start with a very low 0.1 threshold
        'sell_threshold': [-0.1, -0.2, -0.3]  # Start with a very low -0.1 threshold
    }

    optimizer.run_optimization(param_grid=aggressive_param_grid) # Pass the new grid

    logger.info("--- Lesson 19 Verification Complete ---")
    logger.info("Check the console for the results. We now expect to see trades.")

if __name__ == "__main__":
    run_lesson_19_test()