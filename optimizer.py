import logging
import itertools
import pandas as pd
from .backtest import BacktestEngine

class Optimizer:
    def __init__(self, symbols, start_date, end_date, initial_capital):
        # ... (no changes to __init__) ...
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.results = []


    def run_optimization(self, param_grid=None): # Accept an optional grid
        self.logger.info("--- Starting Strategy Parameter Optimization ---")

        if param_grid is None:
            # Define the default Parameter Grid if none is provided
            param_grid = {
                'stop_loss_pct': [0.05, 0.10, 0.15],
                'portfolio_risk_pct': [0.01, 0.02],
                'buy_threshold': [0.2, 0.3, 0.4],
                'sell_threshold': [-0.2, -0.3, -0.4]
            }

        keys, values = zip(*param_grid.items())
        param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        self.logger.info(f"Optimizer will test {len(param_combinations)} unique parameter combinations.")

        for i, params in enumerate(param_combinations):
            self.logger.info(f"--- Running Optimization Pass {i+1}/{len(param_combinations)} ---")
            self.logger.info(f"Testing parameters: {params}")
            engine = BacktestEngine(
                self.symbols, self.start_date, self.end_date,
                self.initial_capital, strategy_params=params
            )
            summary = engine.run()
            result_row = params.copy()
            result_row['return_pct'] = summary['total_return_pct']
            result_row['trade_count'] = summary['total_trades']
            self.results.append(result_row)

        self.logger.info("--- Strategy Optimization Completed ---")
        self.print_results()

    def print_results(self):
        # ... (no changes) ...
        if not self.results: self.logger.info("No results to display."); return
        results_df = pd.DataFrame(self.results)
        sorted_results = results_df.sort_values(by='return_pct', ascending=False)
        self.logger.info("--- Top Optimization Results ---")
        pd.set_option('display.max_rows', 200); pd.set_option('display.width', 1000)
        print(sorted_results.head(20))