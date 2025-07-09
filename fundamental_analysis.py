import yfinance as yf
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

from utils import get_config

class FundamentalSignal(Enum):
    STRONG_BUY = 2
    BUY = 1
    NEUTRAL = 0
    SELL = -1
    STRONG_SELL = -2

@dataclass
class FundamentalMetric:
    """Standardized fundamental metric structure"""
    metric_name: str
    value: float
    signal: FundamentalSignal
    strength: float  # 0.0 to 1.0
    reliability: float  # 0.0 to 1.0
    details: dict = None

class FundamentalAnalyzer:
    """Comprehensive fundamental analysis system"""
    
    def __init__(self):
        self.config = get_config()
        self.api_keys = self.config.get('api_keys', {})
        
        # Weights for different fundamental categories
        self.category_weights = {
            'valuation_metrics': 0.25,      # P/E, P/B, P/S ratios
            'profitability_metrics': 0.25,  # ROE, ROA, margins
            'growth_metrics': 0.20,         # Revenue, earnings growth
            'financial_health': 0.15,       # Debt ratios, current ratio
            'dividend_metrics': 0.10,       # Yield, payout ratio, growth
            'market_metrics': 0.05          # Market cap, float, etc.
        }
        
        # Industry benchmark ranges (will be enhanced with API data)
        self.benchmark_ranges = {
            'pe_ratio': {'undervalued': 15, 'fair': 25, 'overvalued': 35},
            'pb_ratio': {'undervalued': 1.5, 'fair': 3.0, 'overvalued': 5.0},
            'roe': {'poor': 10, 'good': 15, 'excellent': 20},
            'debt_to_equity': {'excellent': 0.3, 'good': 0.6, 'poor': 1.0}
        }

    def analyze_comprehensive_fundamentals(self, symbol: str) -> Dict:
        """
        Main entry point for comprehensive fundamental analysis
        """
        print(f"Agent: Executing comprehensive fundamental analysis for {symbol}")
        
        try:
            # Get company info and financial data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return {"ERROR": f"No fundamental data available for {symbol}"}
            
            # Analyze each category
            all_metrics = []
            
            # 1. Valuation Metrics
            valuation_metrics = self._analyze_valuation_metrics(ticker, info)
            print("INFO: Successfully retrieved Valuation Metrics.")
            all_metrics.extend(valuation_metrics)
            
            # 2. Profitability Metrics
            profitability_metrics = self._analyze_profitability_metrics(ticker, info)
            print("INFO: Successfully retrieved Profitability Metrics.")
            all_metrics.extend(profitability_metrics)
            
            # 3. Growth Metrics
            growth_metrics = self._analyze_growth_metrics(ticker, info)
            print("INFO: Successfully retrieved Growth Metrics.")
            all_metrics.extend(growth_metrics)
            
            # 4. Financial Health
            health_metrics = self._analyze_financial_health(ticker, info)
            print("INFO: Successfully retrieved Health Metrics.")
            all_metrics.extend(health_metrics)
            
            # 5. Dividend Analysis
            dividend_metrics = self._analyze_dividend_metrics(ticker, info)
            print("INFO: Successfully retrieved Dividend Metrics.")
            all_metrics.extend(dividend_metrics)
            
            # 6. Market Metrics
            market_metrics = self._analyze_market_metrics(ticker, info)
            print("INFO: Successfully retrieved Market Metrics.")
            all_metrics.extend(market_metrics)
            
            # Calculate overall fundamental score
            fundamental_analysis = self._calculate_fundamental_score(all_metrics)

            res = {
                "symbol": symbol,
                "company_name": info.get('longName', symbol),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "fundamental_metrics": all_metrics,
                "category_breakdown": self._categorize_metrics(all_metrics),
                "fundamental_analysis": fundamental_analysis,
                "recommendation": fundamental_analysis['recommendation'],
                "confidence": fundamental_analysis['confidence'],
                "score": fundamental_analysis['total_score']
            }

            return res
            
        except Exception as e:
            return {"ERROR": f"Fundamental analysis failed: {e}"}

    def _analyze_valuation_metrics(self, ticker, info: Dict) -> List[FundamentalMetric]:
        """Analyze valuation ratios"""
        metrics = []
        
        # P/E Ratio Analysis
        pe_ratio = info.get('trailingPE') or info.get('forwardPE')
        if pe_ratio and pe_ratio > 0:
            signal, strength = self._evaluate_pe_ratio(pe_ratio)
            metrics.append(FundamentalMetric(
                metric_name="pe_ratio",
                value=pe_ratio,
                signal=signal,
                strength=strength,
                reliability=0.8,
                details={'industry_avg': self._get_industry_pe_avg(info.get('industry', ''))}
            ))
            
        # P/B Ratio Analysis
        pb_ratio = info.get('priceToBook')
        if pb_ratio and pb_ratio > 0:
            signal, strength = self._evaluate_pb_ratio(pb_ratio)
            metrics.append(FundamentalMetric(
                metric_name="pb_ratio",
                value=pb_ratio,
                signal=signal,
                strength=strength,
                reliability=0.7
            ))
        
        # P/S Ratio Analysis
        ps_ratio = info.get('priceToSalesTrailing12Months')
        if ps_ratio and ps_ratio > 0:
            signal, strength = self._evaluate_ps_ratio(ps_ratio)
            metrics.append(FundamentalMetric(
                metric_name="ps_ratio",
                value=ps_ratio,
                signal=signal,
                strength=strength,
                reliability=0.6
            ))
        
        # PEG Ratio Analysis
        peg_ratio = info.get('pegRatio')
        if peg_ratio and peg_ratio > 0:
            signal, strength = self._evaluate_peg_ratio(peg_ratio)
            metrics.append(FundamentalMetric(
                metric_name="peg_ratio",
                value=peg_ratio,
                signal=signal,
                strength=strength,
                reliability=0.75
            ))
        
        return metrics

    def _analyze_profitability_metrics(self, ticker, info: Dict) -> List[FundamentalMetric]:
        """Analyze profitability ratios"""
        metrics = []
        
        # ROE Analysis
        roe = info.get('returnOnEquity')
        if roe:
            roe_pct = roe * 100  # Convert to percentage
            signal, strength = self._evaluate_roe(roe_pct)
            metrics.append(FundamentalMetric(
                metric_name="return_on_equity",
                value=roe_pct,
                signal=signal,
                strength=strength,
                reliability=0.85
            ))
        
        # ROA Analysis
        roa = info.get('returnOnAssets')
        if roa:
            roa_pct = roa * 100
            signal, strength = self._evaluate_roa(roa_pct)
            metrics.append(FundamentalMetric(
                metric_name="return_on_assets",
                value=roa_pct,
                signal=signal,
                strength=strength,
                reliability=0.75
            ))
        
        # Profit Margins
        gross_margin = info.get('grossMargins')
        if gross_margin:
            gross_margin_pct = gross_margin * 100
            signal, strength = self._evaluate_gross_margin(gross_margin_pct)
            metrics.append(FundamentalMetric(
                metric_name="gross_margin",
                value=gross_margin_pct,
                signal=signal,
                strength=strength,
                reliability=0.7
            ))
        
        operating_margin = info.get('operatingMargins')
        if operating_margin:
            op_margin_pct = operating_margin * 100
            signal, strength = self._evaluate_operating_margin(op_margin_pct)
            metrics.append(FundamentalMetric(
                metric_name="operating_margin",
                value=op_margin_pct,
                signal=signal,
                strength=strength,
                reliability=0.8
            ))
        
        return metrics

    def _analyze_growth_metrics(self, ticker, info: Dict) -> List[FundamentalMetric]:
        """Analyze growth metrics"""
        metrics = []
        
        # Revenue Growth
        revenue_growth = info.get('revenueGrowth')
        if revenue_growth:
            rev_growth_pct = revenue_growth * 100
            signal, strength = self._evaluate_revenue_growth(rev_growth_pct)
            metrics.append(FundamentalMetric(
                metric_name="revenue_growth",
                value=rev_growth_pct,
                signal=signal,
                strength=strength,
                reliability=0.8
            ))
        
        # Earnings Growth
        earnings_growth = info.get('earningsGrowth')
        if earnings_growth:
            earn_growth_pct = earnings_growth * 100
            signal, strength = self._evaluate_earnings_growth(earn_growth_pct)
            metrics.append(FundamentalMetric(
                metric_name="earnings_growth",
                value=earn_growth_pct,
                signal=signal,
                strength=strength,
                reliability=0.85
            ))
        
        # Quarterly Revenue Growth
        try:
            financials = ticker.quarterly_financials
            if not financials.empty and len(financials.columns) >= 2:
                recent_revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
                prev_revenue = financials.loc['Total Revenue'].iloc[1] if 'Total Revenue' in financials.index else None
                
                if recent_revenue and prev_revenue and prev_revenue != 0:
                    quarterly_growth = ((recent_revenue - prev_revenue) / prev_revenue) * 100
                    signal, strength = self._evaluate_quarterly_growth(quarterly_growth)
                    metrics.append(FundamentalMetric(
                        metric_name="quarterly_revenue_growth",
                        value=quarterly_growth,
                        signal=signal,
                        strength=strength,
                        reliability=0.7
                    ))
        except Exception as e:
            print(f"ERROR: Couldn't find data for quarterly financials: {e}. Skipping ...")
        
        return metrics

    def _analyze_financial_health(self, ticker, info: Dict) -> List[FundamentalMetric]:
        """Analyze financial health metrics"""
        metrics = []
        
        # Debt-to-Equity Ratio
        debt_to_equity = info.get('debtToEquity')
        if debt_to_equity:
            debt_to_equity_ratio = debt_to_equity / 100  # Convert from percentage
            signal, strength = self._evaluate_debt_to_equity(debt_to_equity_ratio)
            metrics.append(FundamentalMetric(
                metric_name="debt_to_equity",
                value=debt_to_equity_ratio,
                signal=signal,
                strength=strength,
                reliability=0.8
            ))
        
        # Current Ratio
        current_ratio = info.get('currentRatio')
        if current_ratio:
            signal, strength = self._evaluate_current_ratio(current_ratio)
            metrics.append(FundamentalMetric(
                metric_name="current_ratio",
                value=current_ratio,
                signal=signal,
                strength=strength,
                reliability=0.75
            ))
        
        # Quick Ratio
        quick_ratio = info.get('quickRatio')
        if quick_ratio:
            signal, strength = self._evaluate_quick_ratio(quick_ratio)
            metrics.append(FundamentalMetric(
                metric_name="quick_ratio",
                value=quick_ratio,
                signal=signal,
                strength=strength,
                reliability=0.7
            ))
        
        # Cash Position
        total_cash = info.get('totalCash')
        market_cap = info.get('marketCap')
        if total_cash and market_cap:
            cash_to_market_cap = (total_cash / market_cap) * 100
            signal, strength = self._evaluate_cash_position(cash_to_market_cap)
            metrics.append(FundamentalMetric(
                metric_name="cash_to_market_cap",
                value=cash_to_market_cap,
                signal=signal,
                strength=strength,
                reliability=0.6
            ))
        
        return metrics

    def _analyze_dividend_metrics(self, ticker, info: Dict) -> List[FundamentalMetric]:
        """Analyze dividend-related metrics"""
        metrics = []
        
        # Dividend Yield
        dividend_yield = info.get('dividendYield')
        if dividend_yield:
            div_yield_pct = dividend_yield * 100
            signal, strength = self._evaluate_dividend_yield(div_yield_pct)
            metrics.append(FundamentalMetric(
                metric_name="dividend_yield",
                value=div_yield_pct,
                signal=signal,
                strength=strength,
                reliability=0.7
            ))
        
        # Payout Ratio
        payout_ratio = info.get('payoutRatio')
        if payout_ratio:
            payout_pct = payout_ratio * 100
            signal, strength = self._evaluate_payout_ratio(payout_pct)
            metrics.append(FundamentalMetric(
                metric_name="payout_ratio",
                value=payout_pct,
                signal=signal,
                strength=strength,
                reliability=0.75
            ))
        
        return metrics

    def _analyze_market_metrics(self, ticker, info: Dict) -> List[FundamentalMetric]:
        """Analyze market-related metrics"""
        metrics = []
        
        # Market Cap Analysis
        market_cap = info.get('marketCap')
        if market_cap:
            signal, strength = self._evaluate_market_cap(market_cap)
            metrics.append(FundamentalMetric(
                metric_name="market_cap",
                value=market_cap,
                signal=signal,
                strength=strength,
                reliability=0.5
            ))
        
        # Beta Analysis
        beta = info.get('beta')
        if beta:
            signal, strength = self._evaluate_beta(beta)
            metrics.append(FundamentalMetric(
                metric_name="beta",
                value=beta,
                signal=signal,
                strength=strength,
                reliability=0.6
            ))
        
        return metrics

    # -------------------------

    # 1. Valuation Metrics
    def _evaluate_pe_ratio(self, pe_ratio: float) -> tuple:
        """Evaluate P/E ratio"""
        if pe_ratio < 15:
            return FundamentalSignal.BUY, 0.8
        elif pe_ratio < 25:
            return FundamentalSignal.NEUTRAL, 0.3
        elif pe_ratio < 35:
            return FundamentalSignal.SELL, 0.6
        else:
            return FundamentalSignal.STRONG_SELL, 0.9

    def _evaluate_pb_ratio(self, pb_ratio: float) -> tuple:
        """Evaluate P/B ratio"""
        if pb_ratio < 1.0:
            return FundamentalSignal.STRONG_BUY, 0.9
        elif pb_ratio < 1.5:
            return FundamentalSignal.BUY, 0.7
        elif pb_ratio < 3.0:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.7

    def _evaluate_ps_ratio(self, ps_ratio: float) -> tuple:
        """Evaluate P/S ratio"""
        if ps_ratio < 1.0:
            return FundamentalSignal.BUY, 0.7
        elif ps_ratio < 3.0:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.6

    def _evaluate_peg_ratio(self, peg_ratio: float) -> tuple:
        """Evaluate PEG ratio"""
        if peg_ratio < 0.5:
            return FundamentalSignal.STRONG_BUY, 0.9
        elif peg_ratio < 1.0:
            return FundamentalSignal.BUY, 0.8
        elif peg_ratio < 1.5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.7

    # 2. Profitability Metrics
    def _evaluate_roe(self, roe_pct: float) -> tuple:
        """Evaluate Return on Equity"""
        if roe_pct > 20:
            return FundamentalSignal.STRONG_BUY, 0.9
        elif roe_pct > 15:
            return FundamentalSignal.BUY, 0.7
        elif roe_pct > 10:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.6

    def _evaluate_roa(self, roa_pct: float) -> tuple:
        """Evaluate Return on Assets"""
        if roa_pct > 10:
            return FundamentalSignal.BUY, 0.8
        elif roa_pct > 5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.5
    
    def _evaluate_gross_margin(self, margin_pct: float) -> tuple:
        """Evaluate gross margin"""
        if margin_pct > 40:
            return FundamentalSignal.BUY, 0.7
        elif margin_pct > 20:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.5
    
    def _evaluate_operating_margin(self, margin_pct: float) -> tuple:
        """Evaluate operating margin"""
        if margin_pct > 15:
            return FundamentalSignal.BUY, 0.8
        elif margin_pct > 5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.6

    # 3. Growth Metrics
    def _evaluate_revenue_growth(self, growth_pct: float) -> tuple:
        """Evaluate revenue growth"""
        if growth_pct > 20:
            return FundamentalSignal.STRONG_BUY, 0.9
        elif growth_pct > 10:
            return FundamentalSignal.BUY, 0.7
        elif growth_pct > 0:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.8

    def _evaluate_earnings_growth(self, growth_pct: float) -> tuple:
        """Evaluate earnings growth"""
        if growth_pct > 25:
            return FundamentalSignal.STRONG_BUY, 0.9
        elif growth_pct > 15:
            return FundamentalSignal.BUY, 0.8
        elif growth_pct > 5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.7
        
    def _evaluate_quarterly_growth(self, growth_pct: float) -> tuple:
        """Evaluate quarterly growth"""
        if growth_pct > 10:
            return FundamentalSignal.BUY, 0.7
        elif growth_pct > 0:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.6

    # 4. Financial Health Metrics
    def _evaluate_debt_to_equity(self, ratio: float) -> tuple:
        """Evaluate debt-to-equity ratio"""
        if ratio < 0.3:
            return FundamentalSignal.BUY, 0.8
        elif ratio < 0.6:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.6

    def _evaluate_current_ratio(self, ratio: float) -> tuple:
        """Evaluate current ratio"""
        if ratio > 2.0:
            return FundamentalSignal.BUY, 0.7
        elif ratio > 1.5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.6

    def _evaluate_quick_ratio(self, ratio: float) -> tuple:
        """Evaluate quick ratio"""
        if ratio > 1.0:
            return FundamentalSignal.BUY, 0.6
        else:
            return FundamentalSignal.NEUTRAL, 0.3

    def _evaluate_cash_position(self, cash_pct: float) -> tuple:
        """Evaluate cash position"""
        if cash_pct > 15:
            return FundamentalSignal.BUY, 0.6
        elif cash_pct > 5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.4
        
    # 5. Dividend Metrics
    def _evaluate_dividend_yield(self, yield_pct: float) -> tuple:
        """Evaluate dividend yield"""
        if 2 <= yield_pct <= 6:
            return FundamentalSignal.BUY, 0.6
        elif yield_pct > 0:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.NEUTRAL, 0.1

    def _evaluate_payout_ratio(self, payout_pct: float) -> tuple:
        """Evaluate payout ratio"""
        if 30 <= payout_pct <= 60:
            return FundamentalSignal.BUY, 0.6
        elif payout_pct < 80:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.SELL, 0.7

    # 6. Market Metrics
    def _evaluate_market_cap(self, market_cap: float) -> tuple:
        """Evaluate Market Cap"""
        # Neutral signal - market cap doesn't inherently indicate buy/sell
        return FundamentalSignal.NEUTRAL, 0.2

    def _evaluate_beta(self, beta: float) -> tuple:
        """Evaluate Beta"""
        if 0.5 <= beta <= 1.5:
            return FundamentalSignal.NEUTRAL, 0.3
        else:
            return FundamentalSignal.NEUTRAL, 0.1  # High volatility stocks
    
    def _get_industry_pe_avg(self, industry: str) -> float:
        """Get industry average P/E (placeholder - would use real data)"""
        industry_averages = {
            'Technology': 25,
            'Healthcare': 20,
            'Financial Services': 12,
            'Consumer Goods': 18,
            'Energy': 15
        }
        return industry_averages.get(industry, 20)
        
    # -------------------------

    def _calculate_fundamental_score(self, metrics: List[FundamentalMetric]) -> Dict:
        """Calculate overall fundamental score"""
        if not metrics:
            return {
                'total_score': 0,
                'recommendation': 'NEUTRAL',
                'confidence': 0,
                'reasoning': "No fundamental metrics available"
            }
        
        total_weighted_score = 0
        total_weight = 0
        
        category_scores = {}
        
        for metric in metrics:
            # Determine category weight
            category = self._get_metric_category(metric.metric_name)
            weight = self.category_weights.get(category, 0.1)
            
            # Convert signal to numeric score
            signal_score = metric.signal.value
            weighted_score = signal_score * metric.strength * metric.reliability * weight
            
            total_weighted_score += weighted_score
            total_weight += weight
            
            if category not in category_scores:
                category_scores[category] = {'score': 0, 'count': 0}
            category_scores[category]['score'] += signal_score * metric.strength
            category_scores[category]['count'] += 1
        
        # Calculate final score
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine recommendation
        if final_score > 0.5:
            recommendation = 'BUY'
        elif final_score > 0.1:
            recommendation = 'WEAK_BUY'
        elif final_score > -0.1:
            recommendation = 'NEUTRAL'
        elif final_score > -0.5:
            recommendation = 'WEAK_SELL'
        else:
            recommendation = 'SELL'
        
        confidence = min(abs(final_score), 1.0)
        
        res = {
            'total_score': final_score,
            'recommendation': recommendation,
            'confidence': confidence,
            'category_scores': category_scores,
            'metrics_analyzed': len(metrics),
            'reasoning': f"Fundamental score: {final_score:.3f} based on {len(metrics)} metrics across {len(category_scores)} categories"
        }

        return res

    def _get_metric_category(self, metric_name: str) -> str:
        """Categorize metrics"""
        valuation_metrics = ['pe_ratio', 'pb_ratio', 'ps_ratio', 'peg_ratio']
        profitability_metrics = ['return_on_equity', 'return_on_assets', 'gross_margin', 'operating_margin']
        growth_metrics = ['revenue_growth', 'earnings_growth', 'quarterly_revenue_growth']
        health_metrics = ['debt_to_equity', 'current_ratio', 'quick_ratio', 'cash_to_market_cap']
        dividend_metrics = ['dividend_yield', 'payout_ratio']
        market_metrics = ['market_cap', 'beta']
        
        if metric_name in valuation_metrics:
            return 'valuation_metrics'
        elif metric_name in profitability_metrics:
            return 'profitability_metrics'
        elif metric_name in growth_metrics:
            return 'growth_metrics'
        elif metric_name in health_metrics:
            return 'financial_health'
        elif metric_name in dividend_metrics:
            return 'dividend_metrics'
        elif metric_name in market_metrics:
            return 'market_metrics'
        else:
            return 'other'

    def _categorize_metrics(self, metrics: List[FundamentalMetric]) -> Dict:
        """Categorize metrics for analysis"""
        categories = {
            'valuation_metrics': [],
            'profitability_metrics': [],
            'growth_metrics': [],
            'financial_health': [],
            'dividend_metrics': [],
            'market_metrics': []
        }
        
        for metric in metrics:
            category = self._get_metric_category(metric.metric_name)
            if category in categories:
                categories[category].append(metric.metric_name)
        
        return {k: len(v) for k, v in categories.items()}
    
if __name__ == "__main__":
    fundamental = FundamentalAnalyzer()
    print(fundamental.analyze_comprehensive_fundamentals('TSLA'))