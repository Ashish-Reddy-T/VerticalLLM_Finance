import yfinance as yf, talib
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BULLISH = 1
    BEARISH = -1
    NEUTRAL = 0

@dataclass
class TechnicalSignal:
    """Standardized technical signal structure"""
    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reliability: float  # Historical accuracy 0.0 to 1.0
    timeframe: str
    indicator: str
    details: dict = None

class TechnicalAnalyzer:
    """Comprehensive technical analysis with multi-timeframe confluence"""
    
    def __init__(self):
        self.timeframe_weights = {
            '1d': 0.40,
            '4h': 0.30, 
            '1h': 0.20,
            '15m': 0.10
        }
        
        self.indicator_weights = {
            'trend_indicators': 0.30,
            'momentum_oscillators': 0.25,
            'volume_indicators': 0.20,
            'volatility_indicators': 0.15,
            'candlestick_patterns': 0.10
        }
        
        # Minimum confluence score for actionable signals
        self.min_confluence_threshold = 0.15

    def analyze_comprehensive_technicals(self, symbol: str, timeframes: List[str] = ['15m', '1h', '4h', '1d']) -> Dict:
        """
        Main entry point for comprehensive technical analysis
        """
        print(f"Agent: Executing comprehensive technical analysis for {symbol}")
        
        # Get multi-timeframe data
        multi_data = self.get_multi_timeframe_data(symbol, timeframes)
        if not multi_data:
            return {"ERROR": f"No data available for {symbol}"}
        
        # Analyze each category of indicators
        all_signals = []
        
        # 1. Trend Indicators
        trend_signals = self._analyze_trend_indicators(multi_data)
        all_signals.extend(trend_signals)
        
        # 2. Momentum Oscillators  
        momentum_signals = self._analyze_momentum_indicators(multi_data)
        all_signals.extend(momentum_signals)
        
        # 3. Volume Indicators
        volume_signals = self._analyze_volume_indicators(multi_data)
        all_signals.extend(volume_signals)
        
        # 4. Volatility Indicators
        volatility_signals = self._analyze_volatility_indicators(multi_data)
        all_signals.extend(volatility_signals)
        
        # 5. Candlestick Patterns
        candlestick_signals = self._analyze_candlestick_patterns(multi_data)
        all_signals.extend(candlestick_signals)
        
        # Calculate confluence
        confluence_analysis = self._calculate_technical_confluence(all_signals)
        
        # Risk-reward analysis
        risk_reward = self._calculate_risk_reward_ratio(multi_data, confluence_analysis)
        
        return {
            "symbol": symbol,
            "timeframes_analyzed": list(multi_data.keys()),
            "total_signals": len(all_signals),
            "signal_breakdown": self._categorize_signals(all_signals),
            "confluence_analysis": confluence_analysis,
            "risk_reward": risk_reward,
            "recommendation": confluence_analysis['recommendation'],
            "confidence": confluence_analysis['confidence'],
            "signal_strength": confluence_analysis['confluence_score']
        }

    def get_multi_timeframe_data(self, symbol: str, timeframes: List[str]) -> Dict:
        """Enhanced multi-timeframe data fetching with technical indicators pre-calculated"""
        multi_data = {}
        
        period_map = {
            '15m': '60d',
            '1h': '730d', 
            '4h': '730d',
            '1d': '2y'
        }
        
        for tf in timeframes:
            try:
                fetch_period = period_map.get(tf, '2y')
                data = yf.Ticker(symbol).history(period=fetch_period, interval=tf)
                
                if data.empty:
                    print(f"WARNING: No data for {symbol} at {tf} timeframe")
                    continue
                
                # Pre-calculate common indicators
                enhanced_data = self._add_base_indicators(data)
                
                multi_data[tf] = {
                    'ohlc': enhanced_data,
                    'timeframe': tf
                }
                
            except Exception as e:
                print(f"Error fetching {tf} data for {symbol}: {e}")
                continue
        
        return multi_data

    def _add_base_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add commonly used indicators to OHLC data"""
        df = data.copy()
        
        # Moving Averages
        df['SMA_10'] = talib.SMA(df['Close'], timeperiod=10)
        df['SMA_20'] = talib.SMA(df['Close'], timeperiod=20)
        df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
        df['EMA_12'] = talib.EMA(df['Close'], timeperiod=12)
        df['EMA_26'] = talib.EMA(df['Close'], timeperiod=26)
        
        # MACD
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['Close'])
        
        # RSI
        df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
        
        # Bollinger Bands
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = talib.BBANDS(df['Close'])
        
        # ATR
        df['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'])
        
        # Stochastic
        df['STOCH_K'], df['STOCH_D'] = talib.STOCH(df['High'], df['Low'], df['Close'])
        
        return df

    def _analyze_trend_indicators(self, multi_data: Dict) -> List[TechnicalSignal]:
        """Analyze trend-following indicators"""
        signals = []
        
        for tf, data in multi_data.items():
            df = data['ohlc']
            if len(df) < 50:  # Need sufficient data
                continue
            
            # 1. MACD Analysis
            macd_signal = self._analyze_macd(df, tf)
            if macd_signal:
                signals.append(macd_signal)
            
            # 2. Moving Average Crossover
            ma_signal = self._analyze_moving_averages(df, tf)
            if ma_signal:
                signals.append(ma_signal)
            
            # 3. ADX (if we have enough data)
            adx_signal = self._analyze_adx(df, tf)
            if adx_signal:
                signals.append(adx_signal)
        
        return signals

    def _analyze_momentum_indicators(self, multi_data: Dict) -> List[TechnicalSignal]:
        """Analyze momentum oscillators"""
        signals = []
        
        for tf, data in multi_data.items():
            df = data['ohlc']
            if len(df) < 20:
                continue
            
            # 1. RSI Analysis
            rsi_signal = self._analyze_rsi(df, tf)
            if rsi_signal:
                signals.append(rsi_signal)
            
            # 2. Stochastic Oscillator
            stoch_signal = self._analyze_stochastic(df, tf)
            if stoch_signal:
                signals.append(stoch_signal)
            
            # 3. Williams %R
            williams_signal = self._analyze_williams_r(df, tf)
            if williams_signal:
                signals.append(williams_signal)
        
        return signals

    def _analyze_volume_indicators(self, multi_data: Dict) -> List[TechnicalSignal]:
        """Analyze volume-based indicators"""
        signals = []
        
        for tf, data in multi_data.items():
            df = data['ohlc']
            if len(df) < 20:
                continue
            
            # 1. On-Balance Volume
            obv_signal = self._analyze_obv(df, tf)
            if obv_signal:
                signals.append(obv_signal)
            
            # 2. Volume-Price Trend
            vpt_signal = self._analyze_volume_price_trend(df, tf)
            if vpt_signal:
                signals.append(vpt_signal)
        
        return signals

    def _analyze_volatility_indicators(self, multi_data: Dict) -> List[TechnicalSignal]:
        """Analyze volatility indicators"""
        signals = []
        
        for tf, data in multi_data.items():
            df = data['ohlc']
            if len(df) < 20:
                continue
            
            # 1. Bollinger Bands
            bb_signal = self._analyze_bollinger_bands(df, tf)
            if bb_signal:
                signals.append(bb_signal)
            
            # 2. ATR-based signals
            atr_signal = self._analyze_atr(df, tf)
            if atr_signal:
                signals.append(atr_signal)
        
        return signals

    def _analyze_candlestick_patterns(self, multi_data: Dict) -> List[TechnicalSignal]:
        """Analyze candlestick patterns (moved from original code)"""
        signals = []
        
        for tf, data in multi_data.items():
            df = data['ohlc']
            if len(df) < 10:
                continue
            
            patterns = self._detect_candlestick_patterns(df)
            
            for pattern_name, pattern_data in patterns.items():
                latest_signal = pattern_data['signal'][-1] if len(pattern_data['signal']) > 0 else 0
                
                if latest_signal != 0:
                    signal_type = SignalType.BULLISH if latest_signal > 0 else SignalType.BEARISH
                    
                    signals.append(TechnicalSignal(
                        signal_type=signal_type,
                        strength=abs(latest_signal) / 100,
                        confidence=pattern_data['reliability'],
                        reliability=pattern_data['reliability'],
                        timeframe=tf,
                        indicator=f"candlestick_{pattern_name}",
                        details={'pattern': pattern_name, 'signal_value': latest_signal}
                    ))
        
        return signals

    # Individual Indicator Analysis Methods
    def _analyze_macd(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze MACD signals"""
        if len(df) < 26 or df['MACD'].isna().iloc[-1]:
            return None
        
        macd = df['MACD'].iloc[-1]
        signal_line = df['MACD_signal'].iloc[-1]
        histogram = df['MACD_hist'].iloc[-1]
        
        # MACD crossover signal
        if macd > signal_line and df['MACD'].iloc[-2] <= df['MACD_signal'].iloc[-2]:
            # Bullish crossover
            strength = min(abs(histogram) / abs(macd) * 2, 1.0) if macd != 0 else 0.5
            return TechnicalSignal(
                signal_type=SignalType.BULLISH,
                strength=strength,
                confidence=0.7,
                reliability=0.65,
                timeframe=tf,
                indicator="macd_crossover"
            )
        elif macd < signal_line and df['MACD'].iloc[-2] >= df['MACD_signal'].iloc[-2]:
            # Bearish crossover
            strength = min(abs(histogram) / abs(macd) * 2, 1.0) if macd != 0 else 0.5
            return TechnicalSignal(
                signal_type=SignalType.BEARISH,
                strength=strength,
                confidence=0.7,
                reliability=0.65,
                timeframe=tf,
                indicator="macd_crossover"
            )
        
        return None

    def _analyze_rsi(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze RSI signals"""
        if df['RSI'].isna().iloc[-1]:
            return None
        
        rsi = df['RSI'].iloc[-1]
        
        if rsi <= 30:  # Oversold
            strength = (30 - rsi) / 30  # Stronger signal the lower RSI goes
            return TechnicalSignal(
                signal_type=SignalType.BULLISH,
                strength=strength,
                confidence=0.6,
                reliability=0.58,
                timeframe=tf,
                indicator="rsi_oversold",
                details={'rsi_value': rsi}
            )
        elif rsi >= 70:  # Overbought
            strength = (rsi - 70) / 30  # Stronger signal the higher RSI goes
            return TechnicalSignal(
                signal_type=SignalType.BEARISH,
                strength=strength,
                confidence=0.6,
                reliability=0.58,
                timeframe=tf,
                indicator="rsi_overbought",
                details={'rsi_value': rsi}
            )
        
        return None

    def _analyze_moving_averages(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze moving average crossovers"""
        if df['SMA_20'].isna().iloc[-1] or df['SMA_50'].isna().iloc[-1]:
            return None
        
        sma_20_current = df['SMA_20'].iloc[-1]
        sma_50_current = df['SMA_50'].iloc[-1]
        sma_20_prev = df['SMA_20'].iloc[-2]
        sma_50_prev = df['SMA_50'].iloc[-2]
        
        # Golden Cross
        if sma_20_current > sma_50_current and sma_20_prev <= sma_50_prev:
            strength = min((sma_20_current - sma_50_current) / sma_50_current * 100, 1.0)
            return TechnicalSignal(
                signal_type=SignalType.BULLISH,
                strength=strength,
                confidence=0.75,
                reliability=0.68,
                timeframe=tf,
                indicator="ma_golden_cross"
            )
        # Death Cross
        elif sma_20_current < sma_50_current and sma_20_prev >= sma_50_prev:
            strength = min((sma_50_current - sma_20_current) / sma_50_current * 100, 1.0)
            return TechnicalSignal(
                signal_type=SignalType.BEARISH,
                strength=strength,
                confidence=0.75,
                reliability=0.68,
                timeframe=tf,
                indicator="ma_death_cross"
            )
        
        return None

    def _analyze_bollinger_bands(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze Bollinger Bands signals"""
        if df['BB_upper'].isna().iloc[-1]:
            return None
        
        close = df['Close'].iloc[-1]
        bb_upper = df['BB_upper'].iloc[-1]
        bb_lower = df['BB_lower'].iloc[-1]
        bb_middle = df['BB_middle'].iloc[-1]
        
        # Calculate position within bands
        bb_position = (close - bb_lower) / (bb_upper - bb_lower)
        
        if close <= bb_lower:  # Below lower band - oversold
            strength = min((bb_lower - close) / bb_lower * 10, 1.0)
            return TechnicalSignal(
                signal_type=SignalType.BULLISH,
                strength=strength,
                confidence=0.6,
                reliability=0.55,
                timeframe=tf,
                indicator="bb_oversold",
                details={'bb_position': bb_position}
            )
        elif close >= bb_upper:  # Above upper band - overbought
            strength = min((close - bb_upper) / bb_upper * 10, 1.0)
            return TechnicalSignal(
                signal_type=SignalType.BEARISH,
                strength=strength,
                confidence=0.6,
                reliability=0.55,
                timeframe=tf,
                indicator="bb_overbought",
                details={'bb_position': bb_position}
            )
        
        return None

    def _analyze_stochastic(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze Stochastic Oscillator"""
        if df['STOCH_K'].isna().iloc[-1]:
            return None
        
        k = df['STOCH_K'].iloc[-1]
        d = df['STOCH_D'].iloc[-1]
        k_prev = df['STOCH_K'].iloc[-2] if len(df) > 1 else k
        d_prev = df['STOCH_D'].iloc[-2] if len(df) > 1 else d
        
        # Oversold with bullish crossover
        if k <= 20 and d <= 20 and k > d and k_prev <= d_prev:
            strength = (20 - min(k, d)) / 20
            return TechnicalSignal(
                signal_type=SignalType.BULLISH,
                strength=strength,
                confidence=0.6,
                reliability=0.52,
                timeframe=tf,
                indicator="stoch_oversold_cross"
            )
        # Overbought with bearish crossover
        elif k >= 80 and d >= 80 and k < d and k_prev >= d_prev:
            strength = (max(k, d) - 80) / 20
            return TechnicalSignal(
                signal_type=SignalType.BEARISH,
                strength=strength,
                confidence=0.6,
                reliability=0.52,
                timeframe=tf,
                indicator="stoch_overbought_cross"
            )
        
        return None

    # Additional indicator methods (simplified for space)
    def _analyze_adx(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze ADX for trend strength"""
        try:
            adx = talib.ADX(df['High'], df['Low'], df['Close'])
            if adx.isna().iloc[-1]:
                return None
            
            adx_value = adx.iloc[-1]
            if adx_value > 25:  # Strong trend
                # Determine direction using DI+ and DI-
                di_plus = talib.PLUS_DI(df['High'], df['Low'], df['Close'])
                di_minus = talib.MINUS_DI(df['High'], df['Low'], df['Close'])
                
                if di_plus.iloc[-1] > di_minus.iloc[-1]:
                    return TechnicalSignal(
                        signal_type=SignalType.BULLISH,
                        strength=min(adx_value / 50, 1.0),
                        confidence=0.7,
                        reliability=0.62,
                        timeframe=tf,
                        indicator="adx_strong_uptrend"
                    )
                else:
                    return TechnicalSignal(
                        signal_type=SignalType.BEARISH,
                        strength=min(adx_value / 50, 1.0),
                        confidence=0.7,
                        reliability=0.62,
                        timeframe=tf,
                        indicator="adx_strong_downtrend"
                    )
        except:
            pass
        return None

    def _analyze_williams_r(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze Williams %R"""
        try:
            williams_r = talib.WILLR(df['High'], df['Low'], df['Close'])
            if williams_r.isna().iloc[-1]:
                return None
            
            wr = williams_r.iloc[-1]
            if wr <= -80:  # Oversold
                return TechnicalSignal(
                    signal_type=SignalType.BULLISH,
                    strength=(-80 - wr) / 20,
                    confidence=0.55,
                    reliability=0.48,
                    timeframe=tf,
                    indicator="williams_r_oversold"
                )
            elif wr >= -20:  # Overbought
                return TechnicalSignal(
                    signal_type=SignalType.BEARISH,
                    strength=(wr + 20) / 20,
                    confidence=0.55,
                    reliability=0.48,
                    timeframe=tf,
                    indicator="williams_r_overbought"
                )
        except:
            pass
        return None

    def _analyze_obv(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze On-Balance Volume"""
        try:
            obv = talib.OBV(df['Close'], df['Volume'])
            if len(obv) < 10:
                return None
            
            # OBV trend analysis
            obv_sma = talib.SMA(obv, timeperiod=10)
            if obv.iloc[-1] > obv_sma.iloc[-1] and obv.iloc[-2] <= obv_sma.iloc[-2]:
                return TechnicalSignal(
                    signal_type=SignalType.BULLISH,
                    strength=0.6,
                    confidence=0.5,
                    reliability=0.45,
                    timeframe=tf,
                    indicator="obv_bullish_trend"
                )
            elif obv.iloc[-1] < obv_sma.iloc[-1] and obv.iloc[-2] >= obv_sma.iloc[-2]:
                return TechnicalSignal(
                    signal_type=SignalType.BEARISH,
                    strength=0.6,
                    confidence=0.5,
                    reliability=0.45,
                    timeframe=tf,
                    indicator="obv_bearish_trend"
                )
        except:
            pass
        return None

    def _analyze_volume_price_trend(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze Volume-Price Trend"""
        try:
            # Simple VPT calculation
            vpt = ((df['Close'] - df['Close'].shift(1)) / df['Close'].shift(1) * df['Volume']).cumsum()
            vpt_sma = vpt.rolling(window=10).mean()
            
            if len(vpt) < 2:
                return None
            
            if vpt.iloc[-1] > vpt_sma.iloc[-1] and vpt.iloc[-2] <= vpt_sma.iloc[-2]:
                return TechnicalSignal(
                    signal_type=SignalType.BULLISH,
                    strength=0.5,
                    confidence=0.4,
                    reliability=0.42,
                    timeframe=tf,
                    indicator="vpt_bullish"
                )
            elif vpt.iloc[-1] < vpt_sma.iloc[-1] and vpt.iloc[-2] >= vpt_sma.iloc[-2]:
                return TechnicalSignal(
                    signal_type=SignalType.BEARISH,
                    strength=0.5,
                    confidence=0.4,
                    reliability=0.42,
                    timeframe=tf,
                    indicator="vpt_bearish"
                )
        except:
            pass
        return None

    def _analyze_atr(self, df: pd.DataFrame, tf: str) -> TechnicalSignal:
        """Analyze ATR for volatility signals"""
        try:
            if df['ATR'].isna().iloc[-1]:
                return None
            
            atr = df['ATR'].iloc[-1]
            atr_sma = df['ATR'].rolling(window=14).mean().iloc[-1]
            
            # High volatility often precedes trend changes
            if atr > atr_sma * 1.5:
                return TechnicalSignal(
                    signal_type=SignalType.NEUTRAL,  # High volatility, direction unclear
                    strength=min((atr / atr_sma - 1) * 2, 1.0),
                    confidence=0.3,
                    reliability=0.35,
                    timeframe=tf,
                    indicator="atr_high_volatility",
                    details={'atr_ratio': atr / atr_sma}
                )
        except:
            pass
        return None

    def _detect_candlestick_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect candlestick patterns (from original code)"""
        patterns = {}
        
        if len(data) < 5:
            return patterns
        
        open_prices = data['Open'].values
        high_prices = data['High'].values
        low_prices = data['Low'].values
        close_prices = data['Close'].values
        
        # Existing patterns from original code
        patterns['inverted_hammer'] = {
            'signal': talib.CDLINVERTEDHAMMER(open=open_prices, high=high_prices, low=low_prices, close=close_prices),
            'reliability': 0.65,
            'profit_potential': 1.12
        }
        patterns['bearish_marubozu'] = {
            'signal': talib.CDLMARUBOZU(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.54,
            'profit_potential': 0.80
        }
        patterns['gravestone_doji'] = {
            'signal': talib.CDLGRAVESTONEDOJI(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.51,
            'profit_potential': 0.65
        }
        
        engulfing_signal = talib.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)
        patterns['bearish_engulfing'] = {
            'signal': [s if s < 0 else 0 for s in engulfing_signal],
            'reliability': 0.79,
            'profit_potential': 0.61
        }
        patterns['bullish_engulfing'] = {
            'signal': [s if s > 0 else 0 for s in engulfing_signal],
            'reliability': 0.63,
            'profit_potential': 0.58
        }
        patterns['shooting_star'] = {
            'signal': talib.CDLSHOOTINGSTAR(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.60,
            'profit_potential': 0.56
        }
        patterns['hammer'] = {
            'signal': talib.CDLHAMMER(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.61,
            'profit_potential': 0.52
        }
        patterns['hanging_man'] = {
            'signal': talib.CDLHANGINGMAN(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.59,
            'profit_potential': 0.48
        }
        patterns['morning_star'] = {
            'signal': talib.CDLMORNINGSTAR(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.78,
            'profit_potential': 1.04
        }
        patterns['evening_star'] = {
            'signal': talib.CDLEVENINGSTAR(open_prices, high_prices, low_prices, close_prices),
            'reliability': 0.72,
            'profit_potential': 1.15
        }
        
        return patterns

    def _calculate_technical_confluence(self, signals: List[TechnicalSignal]) -> Dict:
        """Calculate confluence across all technical signals"""
        if not signals:
            return {
                'bullish_signals': 0,
                'bearish_signals': 0,
                'confluence_score': 0,
                'recommendation': 'NEUTRAL',
                'confidence': 0,
                'detected_signals': [],
                'reasoning': "No technical signals detected."
            }
        
        bullish_score = 0
        bearish_score = 0
        
        for signal in signals:
            # Weight by timeframe and indicator category
            tf_weight = self.timeframe_weights.get(signal.timeframe, 0.1)
            
            # Determine indicator category weight
            category_weight = 0.2  # Default
            if 'macd' in signal.indicator or 'ma_' in signal.indicator or 'adx' in signal.indicator:
                category_weight = self.indicator_weights['trend_indicators']
            elif 'rsi' in signal.indicator or 'stoch' in signal.indicator or 'williams' in signal.indicator:
                category_weight = self.indicator_weights['momentum_oscillators']
            elif 'obv' in signal.indicator or 'vpt' in signal.indicator:
                category_weight = self.indicator_weights['volume_indicators']
            elif 'bb_' in signal.indicator or 'atr' in signal.indicator:
                category_weight = self.indicator_weights['volatility_indicators']
            elif 'candlestick' in signal.indicator:
                category_weight = self.indicator_weights['candlestick_patterns']
            
            # Calculate weighted signal strength
            weighted_strength = signal.strength * signal.confidence * tf_weight * category_weight
            
            if signal.signal_type == SignalType.BULLISH:
                bullish_score += weighted_strength
            elif signal.signal_type == SignalType.BEARISH:
                bearish_score += weighted_strength
        
        total_score = bullish_score + bearish_score
        
        # Determine recommendation
        if total_score >= self.min_confluence_threshold:
            if bullish_score > bearish_score:
                recommendation = 'BUY'
                confidence = bullish_score / total_score
            else:
                recommendation = 'SELL'
                confidence = bearish_score / total_score
        else:
            recommendation = 'HOLD'
            confidence = 0
        
        return {
            'bullish_signals': bullish_score,
            'bearish_signals': bearish_score,
            'confluence_score': total_score,
            'recommendation': recommendation,
            'confidence': confidence,
            'detected_signals': [
                {
                    'indicator': s.indicator,
                    'timeframe': s.timeframe,
                    'signal_type': s.signal_type.name,
                    'strength': s.strength,
                    'confidence': s.confidence
                } for s in signals
            ],
            'reasoning': f"Technical confluence score: {total_score:.3f} ({'above' if total_score >= self.min_confluence_threshold else 'below'} threshold of {self.min_confluence_threshold})"
        }

    def _categorize_signals(self, signals: List[TechnicalSignal]) -> Dict:
        """Categorize signals by type for analysis"""
        categories = {
            'trend_indicators': [],
            'momentum_oscillators': [],
            'volume_indicators': [],
            'volatility_indicators': [],
            'candlestick_patterns': []
        }
        
        for signal in signals:
            if any(x in signal.indicator for x in ['macd', 'ma_', 'adx']):
                categories['trend_indicators'].append(signal.indicator)
            elif any(x in signal.indicator for x in ['rsi', 'stoch', 'williams']):
                categories['momentum_oscillators'].append(signal.indicator)
            elif any(x in signal.indicator for x in ['obv', 'vpt']):
                categories['volume_indicators'].append(signal.indicator)
            elif any(x in signal.indicator for x in ['bb_', 'atr']):
                categories['volatility_indicators'].append(signal.indicator)
            elif 'candlestick' in signal.indicator:
                categories['candlestick_patterns'].append(signal.indicator)
        
        return {k: len(v) for k, v in categories.items()}

    def _calculate_risk_reward_ratio(self, multi_data: Dict, confluence: Dict) -> Dict:
        """Calculate risk-reward ratio from technical levels"""
        daily_data = multi_data.get('1d', {}).get('ohlc')
        
        if daily_data is None or daily_data.empty:
            return {"error": "Insufficient data for risk-reward calculation"}
        
        current_price = daily_data['Close'].iloc[-1]
        
        # Enhanced support/resistance calculation
        resistance = daily_data['High'].rolling(window=min(20, len(daily_data))).max().iloc[-1]
        support = daily_data['Low'].rolling(window=min(20, len(daily_data))).min().iloc[-1]
        
        # Use Bollinger Bands for additional levels if available
        if 'BB_upper' in daily_data.columns and not daily_data['BB_upper'].isna().iloc[-1]:
            bb_resistance = daily_data['BB_upper'].iloc[-1]
            bb_support = daily_data['BB_lower'].iloc[-1]
            resistance = max(resistance, bb_resistance)
            support = min(support, bb_support)
        
        if confluence['recommendation'] == 'BUY':
            target = resistance
            stop_loss = support
            potential_profit = target - current_price
            potential_loss = current_price - stop_loss
        elif confluence['recommendation'] == 'SELL':
            target = support
            stop_loss = resistance
            potential_profit = current_price - target
            potential_loss = stop_loss - current_price
        else:
            return {"recommendation": "HOLD", "reason": "No clear directional bias"}
        
        risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
        
        return {
            "current_price": float(current_price),
            "target": float(target),
            "stop_loss": float(stop_loss),
            "potential_profit": float(potential_profit),
            "potential_loss": float(potential_loss),
            "risk_reward_ratio": float(risk_reward_ratio),
            "trade_recommendation": "EXECUTE" if risk_reward_ratio >= 1.5 else "WAIT",
            "risk_level": "LOW" if risk_reward_ratio >= 2.0 else "MEDIUM" if risk_reward_ratio >= 1.5 else "HIGH"
        }