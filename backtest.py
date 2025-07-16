import backtrader as bt
import pandas as pd
import numpy as np
import pickle
import hashlib
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import lru_cache
import multiprocessing as mp

# Import your existing modules
from financial_tools import search_yahoo_api, get_stock_quote
from technical_analysis import TechnicalAnalyzer
from fundamental_analysis import FundamentalAnalyzer
from sentiment_analysis import SentimentAnalyzer

class SignalType(Enum):
    BUY = 1
    SELL = -1
    HOLD = 0

@dataclass
class TradingSignal:
    """Standardized trading signal structure"""
    symbol: str
    timestamp: datetime
    signal: SignalType
    confidence: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: float = 1.0
    metadata: Dict = None

class CacheManager:
    """High-performance caching system for expensive calculations"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.max_memory_items = 1000
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(f"{cache_dir}/technical", exist_ok=True)
        os.makedirs(f"{cache_dir}/finbert", exist_ok=True)
        os.makedirs(f"{cache_dir}/fundamental", exist_ok=True)
    
    def _get_cache_key(self, symbol: str, timeframe: str, start_date: str, end_date: str, calc_type: str) -> str:
        """Generate unique cache key"""
        key_string = f"{symbol}_{timeframe}_{start_date}_{end_date}_{calc_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_technical_indicators(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> Optional[Dict]:
        """Get cached technical indicators or None if not found"""
        cache_key = self._get_cache_key(symbol, timeframe, start_date, end_date, "technical")
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = f"{self.cache_dir}/technical/{cache_key}.pkl"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    # Add to memory cache (with LRU eviction)
                    self._add_to_memory_cache(cache_key, data)
                    return data
            except Exception as e:
                print(f"Cache read error: {e}")
        
        return None
    
    def cache_technical_indicators(self, symbol: str, timeframe: str, start_date: str, end_date: str, data: Dict):
        """Cache technical indicators"""
        cache_key = self._get_cache_key(symbol, timeframe, start_date, end_date, "technical")
        
        # Save to disk
        cache_file = f"{self.cache_dir}/technical/{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Cache write error: {e}")
        
        # Add to memory cache
        self._add_to_memory_cache(cache_key, data)
    
    def get_finbert_sentiment(self, text_hash: str) -> Optional[Dict]:
        """Get cached FinBERT sentiment"""
        cache_file = f"{self.cache_dir}/finbert/{text_hash}.pkl"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"FinBERT cache read error: {e}")
        return None
    
    def cache_finbert_sentiment(self, text_hash: str, sentiment_data: Dict):
        """Cache FinBERT sentiment"""
        cache_file = f"{self.cache_dir}/finbert/{text_hash}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(sentiment_data, f)
        except Exception as e:
            print(f"FinBERT cache write error: {e}")
    
    def _add_to_memory_cache(self, key: str, data: Dict):
        """Add to memory cache with LRU eviction"""
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest item (simple FIFO for now)
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = data
    
    def clear_cache(self):
        """Clear all caches"""
        self.memory_cache.clear()
        # Could also clear disk cache if needed


class SignalGenerator:
    """Extract agent logic and convert to discrete trading signals"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Simplified weights for backtesting (no LLM planning)
        self.weights = {
            'technical': 0.70,      # Increased - most reliable for backtesting
            'fundamental': 0.20,    # Reduced - changes slowly
            'sentiment': 0.10       # Reduced - too slow/expensive for frequent calculation
        }
        
        # Even more sensitive thresholds
        self.buy_threshold = 0.1   # 2% threshold - very sensitive
        self.sell_threshold = -0.1
        
        # Pre-calculated analysis cache
        self.analysis_cache = {}
    
    def pre_calculate_analysis(self, symbol: str, start_date: str, end_date: str):
        """Pre-calculate all analysis for the entire period to avoid redundant calculations"""
        print(f"Pre-calculating analysis for {symbol} from {start_date} to {end_date}")
        
        cache_key = f"{symbol}_{start_date}_{end_date}"
        if cache_key in self.analysis_cache:
            print(f"Using cached pre-analysis for {symbol}")
            return
        
        try:
            # Calculate technical analysis once for the entire period
            print(f"Calculating technical analysis for {symbol}...")
            technical_analysis = self.technical_analyzer.analyze_comprehensive_technicals(symbol, ['1d', '4h', '1h', '15m'])
            technical_score = self._extract_technical_score(technical_analysis, symbol)
            
            # Calculate fundamental analysis once (doesn't change daily)
            print(f"Calculating fundamental analysis for {symbol}...")
            fundamental_analysis = self.fundamental_analyzer.analyze_comprehensive_fundamentals(symbol)
            fundamental_score = self._extract_fundamental_score(fundamental_analysis)
            
            # Calculate sentiment analysis
            print(f"Calculating sentiment analysis for {symbol}...")
            sentiment_analysis = self.sentiment_analyzer.analyze_comprehensive_sentiment(symbol, symbol, 7)
            sentiment_score = self._extract_sentiment_score(sentiment_analysis)
            
            # Store in cache
            self.analysis_cache[cache_key] = {
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'sentiment_score': sentiment_score,
                'calculated_date': datetime.now()
            }
            
            print(f"Pre-analysis complete for {symbol}: T={technical_score:.3f}, F={fundamental_score:.3f}, S={sentiment_score:.3f}")
            print(f"Expected combined score: {(technical_score * 0.70 + fundamental_score * 0.20 + sentiment_score * 0.10):.3f}")
            
            # Debug: Print raw analysis structure to understand why technical is 0
            if technical_score == 0.0 and symbol in technical_analysis:
                raw_confluence = technical_analysis[symbol].get('confluence_analysis', {})
                print(f"DEBUG - Raw confluence data: {raw_confluence}")
            
            if fundamental_score == 0.0 and 'fundamental_analysis' in fundamental_analysis:
                raw_fundamental = fundamental_analysis.get('fundamental_analysis', {})
                print(f"DEBUG - Raw fundamental data keys: {list(raw_fundamental.keys())}")
                print(f"DEBUG - Recommendation: {raw_fundamental.get('recommendation')}, Score: {raw_fundamental.get('total_score')}")
            
        except Exception as e:
            print(f'Pre-analysis error for {symbol}: {e}')
            self.analysis_cache[cache_key] = {
                'technical_score': 0.0,
                'fundamental_score': 0.0,
                'sentiment_score': 0.0,
                'error': str(e)
            }
    
    def generate_signal(self, symbol: str, current_date: datetime, lookback_days: int = 30) -> TradingSignal:
        """Generate trading signal using dynamic analysis"""
        
        try:
            # Check if we need to recalculate analysis (weekly)
            week_key = f"{symbol}_{current_date.strftime('%Y-%W')}"
            
            # Use cached analysis if available for this week
            analysis_data = self.analysis_cache.get(week_key)
            
            if not analysis_data:
                # Recalculate analysis for this week
                print(f"Recalculating analysis for {symbol} week of {current_date.strftime('%Y-%m-%d')}")
                
                # Calculate technical analysis for current date
                technical_analysis = self.technical_analyzer.analyze_comprehensive_technicals(symbol, ['1d', '4h', '1h', '15m'])
                technical_score = self._extract_technical_score(technical_analysis, symbol)
                
                # Fundamental analysis changes slowly, so we can keep it for longer periods
                fundamental_analysis = self.fundamental_analyzer.analyze_comprehensive_fundamentals(symbol)
                fundamental_score = self._extract_fundamental_score(fundamental_analysis)
                
                # Sentiment analysis for current period
                sentiment_analysis = self.sentiment_analyzer.analyze_comprehensive_sentiment(symbol, symbol, 7)
                sentiment_score = self._extract_sentiment_score(sentiment_analysis)
                
                # Cache for this week
                analysis_data = {
                    'technical_score': technical_score,
                    'fundamental_score': fundamental_score,
                    'sentiment_score': sentiment_score,
                    'calculated_date': current_date
                }
                self.analysis_cache[week_key] = analysis_data
            
            # Get scores
            technical_score = analysis_data.get('technical_score', 0.0)
            fundamental_score = analysis_data.get('fundamental_score', 0.0)
            sentiment_score = analysis_data.get('sentiment_score', 0.0)
            
            # Calculate weighted score
            combined_score = (
                technical_score * self.weights['technical'] +
                fundamental_score * self.weights['fundamental'] +
                sentiment_score * self.weights['sentiment']
            )
            
            # Debug output with more detail
            if current_date.day % 7 == 0:  # Print weekly
                signal_strength = "WEAK" if abs(combined_score) < 0.05 else "MODERATE" if abs(combined_score) < 0.15 else "STRONG"
                print(f"{current_date.date()}: {symbol} - T:{technical_score:.3f}, F:{fundamental_score:.3f}, Combined:{combined_score:.3f} ({signal_strength})")
            
            # Generate signal with more aggressive approach
            if combined_score > self.buy_threshold:
                signal_type = SignalType.BUY
            elif combined_score < self.sell_threshold:
                signal_type = SignalType.SELL
            elif fundamental_score > 0.05:  # Any positive fundamental score
                signal_type = SignalType.BUY
                combined_score = fundamental_score * 0.5  # Boost for logging
            elif current_date.day % 15 == 0 and fundamental_score > 0:
                # Force trade every 15 days if fundamentals are positive
                signal_type = SignalType.BUY
                combined_score = 0.03  # Minimal but above threshold
                print(f"FORCED BUY: {symbol} on {current_date.date()} due to positive fundamentals")
            else:
                signal_type = SignalType.HOLD
            
            # Get current price for entry
            entry_price = self._get_current_price(symbol, current_date)
            confidence = min(abs(combined_score), 1.0)
            
            return TradingSignal(
                symbol=symbol,
                timestamp=current_date,
                signal=signal_type,
                confidence=confidence,
                entry_price=entry_price,
                metadata={
                    'combined_score': combined_score,
                    'technical_score': technical_score,
                    'fundamental_score': fundamental_score,
                    'sentiment_score': sentiment_score
                }
            )
            
        except Exception as e:
            print(f"Signal generation error for {symbol}: {e}")
            return TradingSignal(
                symbol=symbol,
                timestamp=current_date,
                signal=SignalType.HOLD,
                confidence=0.0,
                entry_price=0.0
            )
    
    def _extract_technical_score(self, analysis: Dict, symbol: str) -> float:
        """Extract technical score from pre-calculated analysis with more lenient thresholds"""
        try:
            if isinstance(analysis, dict):
                # The technical analysis result has the confluence_analysis directly in the root
                confluence = analysis.get('confluence_analysis', {})
                recommendation = confluence.get('recommendation', 'HOLD')
                confidence = confluence.get('confidence', 0.0)
                confluence_score = confluence.get('confluence_score', 0.0)
                detected_signals = confluence.get('detected_signals', [])
                
                print(f"Technical Analysis for {symbol}: {recommendation}, confidence: {confidence:.3f}, confluence: {confluence_score:.3f}, signals: {len(detected_signals)}")
                
                # More balanced scoring - reduce the maximum strength
                if recommendation == 'BUY':
                    return min(confidence * 0.8, 0.6)  # Cap at 0.6 instead of 1.0
                elif recommendation == 'SELL':
                    return max(-confidence * 0.8, -0.6)  # Cap at -0.6 instead of -1.0
                elif recommendation == 'HOLD':
                    # Use any confluence score, no matter how small
                    if confluence_score > 0:
                        return min(confluence_score * 0.5, 0.3)  # Cap confluence-based signals
                    elif len(detected_signals) > 0:
                        return 0.05  # Give small positive score for any detected signals
                    else:
                        return 0.0
                else:
                    return 0.0
        except Exception as e:
            print(f"Technical score extraction error: {e}")
        return 0.0
    
    def _extract_fundamental_score(self, analysis: Dict) -> float:
        """Extract fundamental score from pre-calculated analysis"""
        try:
            if isinstance(analysis, dict) and 'fundamental_analysis' in analysis:
                fund_data = analysis['fundamental_analysis']
                recommendation = fund_data.get('recommendation', 'NEUTRAL')
                confidence = fund_data.get('confidence', 0.0)
                total_score = fund_data.get('total_score', 0.0)
                
                print(f"Fundamental Analysis: {recommendation}, confidence: {confidence:.3f}, score: {total_score:.3f}")
                
                # Map recommendation to score with more aggressive scaling
                score_map = {
                    'BUY': 1.0, 'WEAK_BUY': 0.5, 'NEUTRAL': 0.0,
                    'WEAK_SELL': -0.5, 'SELL': -1.0
                }
                
                base_score = score_map.get(recommendation, 0.0)
                final_score = base_score * confidence
                
                # Also consider raw score for additional signal
                if abs(total_score) > 0.1:
                    final_score += total_score * 0.5
                
                return np.clip(final_score, -1.0, 1.0)
        except Exception as e:
            print(f"Fundamental score extraction error: {e}")
        return 0.0
    
    def _extract_sentiment_score(self, analysis: Dict) -> float:
        """Extract sentiment score from pre-calculated analysis"""
        try:
            if isinstance(analysis, dict) and 'overall_sentiment' in analysis:
                sentiment_data = analysis['overall_sentiment']
                weighted_score = sentiment_data.get('weighted_score', 0.0)
                confidence = sentiment_data.get('confidence', 0.0)
                recommendation = sentiment_data.get('recommendation', 'NEUTRAL')
                
                print(f"Sentiment Analysis: {recommendation}, confidence: {confidence:.3f}, score: {weighted_score:.3f}")
                
                # Map sentiment recommendation to score
                score_map = {
                    'VERY_POSITIVE': 1.0, 'POSITIVE': 0.5, 'NEUTRAL': 0.0,
                    'NEGATIVE': -0.5, 'VERY_NEGATIVE': -1.0
                }
                
                base_score = score_map.get(recommendation, 0.0)
                final_score = base_score * confidence
                
                # Also consider raw weighted score for additional signal
                if abs(weighted_score) > 0.1:
                    final_score += weighted_score * 0.3
                
                return np.clip(final_score, -1.0, 1.0)
        except Exception as e:
            print(f"Sentiment score extraction error: {e}")
        return 0.0
    
    def _get_current_price(self, symbol: str, current_date: datetime) -> float:
        """Get current price for the given date"""
        try:
            # In backtesting, we need historical price for that specific date
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            
            # Get data for that specific date
            start_date = current_date.strftime('%Y-%m-%d')
            end_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
            data = ticker.history(start=start_date, end=end_date)
            if not data.empty:
                return float(data['Close'].iloc[-1])
            
        except Exception as e:
            print(f"Price fetch error: {e}")
        
        return 0.0

class BacktestStrategy(bt.Strategy):
    """Backtrader strategy that uses our SignalGenerator"""
    
    params = (
        ('signal_generator', None),
        ('lookback_days', 30),
        ('position_size', 0.95),  # Use 95% of available cash
    )
    
    def __init__(self):
        self.signal_generator = self.params.signal_generator
        self.last_signal_date = None
        self.signal_count = 0
        
    def next(self):
        """Called for each bar in the backtest"""
        current_date = self.datas[0].datetime.datetime(0)
        
        # Skip if we already generated signal for this date
        if self.last_signal_date == current_date.date():
            return
        
        self.last_signal_date = current_date.date()
        self.signal_count += 1
        
        # Get trading signal
        symbol = self.datas[0]._name
        signal = self.signal_generator.generate_signal(symbol, current_date, self.params.lookback_days)
        
        # Execute trades based on signal
        if signal.signal == SignalType.BUY and not self.position:
            available_cash = self.broker.getcash()
            size = (available_cash * self.params.position_size) / self.data.close[0]
            if size > 0:
                self.buy(size=size)
                print(f"{current_date.date()}: BUY {symbol} at ${self.data.close[0]:.2f} (confidence: {signal.confidence:.3f}, size: {size:.0f})")
            
        # Add sell logic for profit-taking or stop-loss
        elif signal.signal == SignalType.SELL and self.position:
            self.close()
            print(f"{current_date.date()}: SELL {symbol} at ${self.data.close[0]:.2f} (confidence: {signal.confidence:.3f})")
        
        # Add profit-taking logic - sell if up 15% or more
        elif self.position and not signal.signal == SignalType.SELL:
            entry_price = self.position.price
            current_price = self.data.close[0]
            profit_pct = (current_price - entry_price) / entry_price * 100
            
            if profit_pct > 15:  # Take profits at 15%
                self.close()
                print(f"{current_date.date()}: PROFIT-TAKING {symbol} at ${current_price:.2f} (+{profit_pct:.1f}%)")
            elif profit_pct < -10:  # Stop loss at -10%
                self.close()
                print(f"{current_date.date()}: STOP-LOSS {symbol} at ${current_price:.2f} ({profit_pct:.1f}%)")
            
        # Print summary every 10 signals
        if self.signal_count % 10 == 0:
            print(f"Processed {self.signal_count} signals, Position: {self.position.size if self.position else 0}")

class BacktestEngine:
    """Main backtesting engine with parallel processing support"""
    
    def __init__(self, cache_manager: CacheManager = None):
        self.cache_manager = cache_manager or CacheManager()
        # Use the updated simplified signal generator
        self.signal_generator = SignalGenerator(self.cache_manager)
    
    def run_single_backtest(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        initial_capital: float = 10000.0
    ) -> Dict:
        """Run backtest for a single asset with simplified signal generation"""
        
        print(f"Starting simplified backtest for {symbol} from {start_date} to {end_date}")
        
        # Analysis will be calculated dynamically during backtest
        print(f"Analysis will be calculated dynamically for {symbol}")
        
        # Create Cerebro engine
        cerebro = bt.Cerebro()
        
        # Add strategy
        cerebro.addstrategy(
            BacktestStrategy, 
            signal_generator=self.signal_generator,
            lookback_days=30
        )
        
        # Get data
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                return {"error": f"No data available for {symbol}"}
            
            print(f"Loaded {len(data)} bars for {symbol}")
            
            # Convert to Backtrader format
            bt_data = bt.feeds.PandasData(
                dataname=data,
                name=symbol,
                timeframe=bt.TimeFrame.Days
            )
            
            cerebro.adddata(bt_data)
            
        except Exception as e:
            return {"error": f"Data fetch failed: {e}"}
        
        # Set broker parameters
        cerebro.broker.setcash(initial_capital)
        cerebro.broker.setcommission(commission=0.001)  # 0.1% commission
        
        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # Run backtest
        start_time = time.time()
        print("Running simplified backtest...")
        results = cerebro.run()
        end_time = time.time()
        
        # Extract results
        strategy = results[0]
        
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        # Get analyzer results
        sharpe_ratio = strategy.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        max_drawdown = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)
        trade_analysis = strategy.analyzers.trades.get_analysis()
        
        return {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'sharpe_ratio': sharpe_ratio or 0,
            'max_drawdown_pct': max_drawdown,
            'total_trades': trade_analysis.get('total', {}).get('total', 0),
            'winning_trades': trade_analysis.get('won', {}).get('total', 0),
            'losing_trades': trade_analysis.get('lost', {}).get('total', 0),
            'execution_time_seconds': end_time - start_time,
            'signal_type': 'simplified'
        }
    
    def run_multi_asset_backtest(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        initial_capital: float = 10000.0,
        max_workers: int = None
    ) -> Dict:
        """Run sequential backtests for multiple assets (avoiding multiprocessing issues)"""
        
        print(f"Running sequential backtests for {len(symbols)} symbols")
        
        # Run backtests sequentially to avoid multiprocessing issues
        results = {}
        for symbol in symbols:
            print(f"\n--- Processing {symbol} ---")
            try:
                result = self.run_single_backtest(symbol, start_date, end_date, initial_capital)
                results[symbol] = result
                print(f"✓ {symbol} completed: {result.get('total_return_pct', 0):.2f}% return")
            except Exception as e:
                results[symbol] = {"error": f"Backtest failed: {e}"}
                print(f"✗ {symbol} failed: {e}")
        
        # Calculate portfolio-level metrics
        portfolio_metrics = self._calculate_portfolio_metrics(results, initial_capital)
        
        return {
            'individual_results': results,
            'portfolio_metrics': portfolio_metrics,
            'symbols_count': len(symbols),
            'successful_backtests': len([r for r in results.values() if 'error' not in r])
        }
    
    def _run_single_backtest_isolated(self, symbol: str, start_date: str, end_date: str, initial_capital: float) -> Dict:
        """Run single backtest in isolated process"""
        # Create new instances for process isolation
        cache_manager = CacheManager()
        signal_generator = SignalGenerator(cache_manager)
        
        engine = BacktestEngine(cache_manager)
        engine.signal_generator = signal_generator
        
        return engine.run_single_backtest(symbol, start_date, end_date, initial_capital)
    
    def _calculate_portfolio_metrics(self, results: Dict, initial_capital: float) -> Dict:
        """Calculate portfolio-level performance metrics"""
        successful_results = [r for r in results.values() if 'error' not in r]
        
        if not successful_results:
            return {"error": "No successful backtests"}
        
        # Simple equal-weight portfolio metrics
        total_initial = initial_capital * len(successful_results)
        total_final = sum(r['final_value'] for r in successful_results)
        portfolio_return = (total_final - total_initial) / total_initial * 100
        
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in successful_results])
        max_drawdown = max(r['max_drawdown_pct'] for r in successful_results)
        total_trades = sum(r['total_trades'] for r in successful_results)
        
        return {
            'portfolio_return_pct': portfolio_return,
            'avg_sharpe_ratio': avg_sharpe,
            'worst_drawdown_pct': max_drawdown,
            'total_trades': total_trades,
            'successful_symbols': len(successful_results),
            'avg_execution_time': np.mean([r['execution_time_seconds'] for r in successful_results])
        }

# Example usage and testing
if __name__ == "__main__":
    # Set environment variable to avoid HuggingFace tokenizer warnings
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    # Initialize the backtesting system
    cache_manager = CacheManager()
    engine = BacktestEngine(cache_manager)
    
    # Example 1: Single asset backtest (shorter period for testing)
    print("=== Single Asset Backtest ===")
    result = engine.run_single_backtest(
        symbol="MSFT",  # Start with MSFT since it has positive fundamentals
        start_date="2023-01-01",  # Shorter period for quick testing
        end_date="2023-12-31",   # 2 month test period
        initial_capital=10000
    )
    print(f"MSFT Result: Return: {result.get('total_return_pct', 0):.2f}%, Trades: {result.get('total_trades', 0)}")
    
    # Example 2: Multi-asset backtest (sequential)
    print("\n=== Multi-Asset Sequential Backtest ===")
    symbols = ["MSFT", "GOOGL"]  # Test only stocks with positive fundamentals
    results = engine.run_multi_asset_backtest(
        symbols=symbols,
        start_date="2023-01-01",
        end_date="2023-12-31",
        initial_capital=10000
    )
    print(f"Portfolio Results: Return: {results['portfolio_metrics']['portfolio_return_pct']:.2f}%, Trades: {results['portfolio_metrics']['total_trades']}")
    
    # Show individual results
    print("\n=== Individual Stock Performance ===")
    for symbol, result in results['individual_results'].items():
        if 'error' not in result:
            print(f"{symbol}: {result['total_return_pct']:.2f}% return, {result['total_trades']} trades, {result['execution_time_seconds']:.1f}s")