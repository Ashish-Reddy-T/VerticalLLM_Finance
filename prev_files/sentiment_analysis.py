import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from ..utils import get_keys

class SentimentSignal(Enum):
    VERY_POSITIVE = 2
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1
    VERY_NEGATIVE = -2

@dataclass
class SentimentSource:
    """Standardized sentiment source structure"""
    source_type: str
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    volume: int  # Number of data points
    reliability: float  # Historical accuracy 0.0 to 1.0
    details: dict = None

class SentimentAnalyzer:
    """Comprehensive multi-source sentiment analysis system"""
    
    def __init__(self):
        
        # Initialize FinBERT for financial sentiment analysis
        self._init_finbert()
        
        # Weights for different sentiment sources
        self.source_weights = {
            'news_sentiment': 0.25,
            'analyst_ratings': 0.20,
            'social_media': 0.20,
            'insider_trading': 0.15,
            'options_flow': 0.10,
            'institutional_activity': 0.10
        }
        
        # Reliability scores based on research
        self.source_reliability = {
            'news_sentiment': 0.7,
            'analyst_ratings': 0.75,
            'social_media': 0.5,
            'insider_trading': 0.85,
            'options_flow': 0.6,
            'institutional_activity': 0.8
        }

    def _init_finbert(self):
        """Initialize FinBERT model for financial sentiment analysis"""
        try:
            finbert_ckpt = "yiyanghkust/finbert-tone"
            self.tokenizer = AutoTokenizer.from_pretrained(finbert_ckpt)
            self.model = AutoModelForSequenceClassification.from_pretrained(finbert_ckpt)
            self.sentiment_labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
        except Exception as e:
            print(f"WARNING: Could not load FinBERT model: {e}")
            self.tokenizer = None
            self.model = None

    def analyze_comprehensive_sentiment(self, symbol: str, company_name: str, days_back: int = 7) -> Dict:
        """
        Main entry point for comprehensive sentiment analysis
        """
        print(f"Agent: Executing comprehensive sentiment analysis for {symbol}")
        
        sentiment_sources = []
        
        try:
            # 1. News Sentiment
            news_sentiment = self._analyze_news_sentiment(company_name, days_back)
            if news_sentiment:
                #print("INFO: Successfully retrieved News Sentiments.")
                sentiment_sources.append(news_sentiment)
            
            # 2. Analyst Ratings and Price Targets
            analyst_sentiment = self._analyze_analyst_sentiment(symbol)
            if analyst_sentiment:
                #print("INFO: Successfully retrieved Analyst Recommendations.")
                sentiment_sources.append(analyst_sentiment)
            
            # 3. Social Media Sentiment
            social_sentiment = self._analyze_social_media_sentiment(symbol, company_name)
            if social_sentiment:
                #print("INFO: Successfully retrieved Social Media Analyses.")
                sentiment_sources.append(social_sentiment)
            
            # 4. Insider Trading Activity
            insider_sentiment = self._analyze_insider_trading(symbol)
            if insider_sentiment:
                #print("INFO: Successfully retrieved Insider Sentiments.")
                sentiment_sources.append(insider_sentiment)
            
            # 5. Options Flow Analysis
            options_sentiment = self._analyze_options_flow(symbol)
            if options_sentiment:
                #print("INFO: Successfully retrieved Option Flow Sentiments.")
                sentiment_sources.append(options_sentiment)
            
            # 6. Institutional Activity
            institutional_sentiment = self._analyze_institutional_activity(symbol)
            if institutional_sentiment:
                #print("INFO: Successfully retrieved Instituitional Sentiments.")
                sentiment_sources.append(institutional_sentiment)
            
            # Calculate overall sentiment
            overall_sentiment = self._calculate_overall_sentiment(sentiment_sources)

            res = {
                "symbol": symbol,
                "company_name": company_name,
                "analysis_date": datetime.now().isoformat(),
                "days_analyzed": days_back,
                "sentiment_sources": sentiment_sources,
                "source_breakdown": self._categorize_sources(sentiment_sources),
                "overall_sentiment": overall_sentiment,
                "recommendation": overall_sentiment['recommendation'],
                "confidence": overall_sentiment['confidence'],
                "sentiment_score": overall_sentiment['weighted_score']
            }
            
            return res
            
        except Exception as e:
            return {"ERROR": f"Comprehensive sentiment analysis failed: {e}"}

    def _analyze_news_sentiment(self, company_name: str, days_back: int) -> Optional[SentimentSource]:
        """Enhanced news sentiment analysis with multiple sources"""
        try:
            news_api_key = get_keys('NEWSAPI')
            if not news_api_key:
                print("WARNING: News API key not found")
                return None
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Multiple news queries for better coverage
            queries = [
                f'"{company_name}"',
                f'"{company_name}" stock',
                f'"{company_name}" earnings',
                f'"{company_name}" revenue'
            ]
            
            all_articles = []
            
            for query in queries:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'sortBy': 'relevancy',
                    'language': 'en',
                    'pageSize': 20,
                    'apiKey': news_api_key
                }
                
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    news_data = response.json()
                    articles = news_data.get('articles', [])
                    all_articles.extend(articles)
                except:
                    continue
            
            if not all_articles:
                print(f"WARNING: No articles found for: {company_name}")
                return None
            
            # Remove duplicates based on title
            unique_articles = []
            seen_titles = set()
            for article in all_articles:
                title = article.get('title', '')
                if title and title not in seen_titles:
                    unique_articles.append(article)
                    seen_titles.add(title)
            
            # Analyze sentiment for each article
            sentiments = []
            
            for article in unique_articles[:50]:  # Limit to top 50
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                
                # Combine text fields
                text_parts = [title, description, content]
                full_text = '. '.join([part for part in text_parts if part and len(part.strip()) > 10])
                
                if full_text and len(full_text.strip()) > 20:
                    sentiment_result = self._get_finbert_sentiment(full_text[:512])  # Limit for FinBERT
                    if sentiment_result:
                        sentiments.append(sentiment_result)
            
            if not sentiments:
                print("WARNING: No sentiments discovered from FinBERT")
                return None
            
            # Calculate weighted average sentiment
            total_weight = sum(s['confidence'] for s in sentiments)
            if total_weight == 0:
                print("WARNING: Confidence score is 0 (implying no sentiments may have been discovered)")
                return None
            
            weighted_sentiment = sum(s['score'] * s['confidence'] for s in sentiments) / total_weight
            avg_confidence = np.mean([s['confidence'] for s in sentiments])

            res = SentimentSource(
                source_type="news_sentiment",
                sentiment_score=weighted_sentiment,
                confidence=avg_confidence,
                volume=len(sentiments),
                reliability=self.source_reliability['news_sentiment'],
                details={
                    'articles_analyzed': len(sentiments),
                    'unique_sources': len(set(a.get('source', {}).get('name', '') for a in unique_articles)),
                    'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                }
            )

            return res
            
        except Exception as e:
            print(f"ERROR: News sentiment analysis error: {e}")
            return None

    def _analyze_analyst_sentiment(self, symbol: str) -> Optional[SentimentSource]:
        """Analyze analyst ratings and price targets"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get analyst recommendations
            recommendations = None
            try:
                recommendations = ticker.recommendations
            except Exception as e:
                print(f"ERROR: Couldn't get recommendations: {e}")
                recommendations = None
            
            # Get analyst price targets
            analyst_price_targets = None
            try:
                analyst_price_targets = ticker.analyst_price_targets
            except Exception as e:
                print(f"ERROR: Couldn't get price targets: {e}")
                analyst_price_targets = None
            
            if recommendations is None and analyst_price_targets is None:
                print("ERROR: No analyst recommendations or price targets found")
                return None
            
            sentiment_scores = []
            current_price = None
            details = {
                'recommendations_count': 0,
                'price_target_analyzed': None,
                'current_price': None
            }
            
            try:
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
                details['current_price'] = current_price
            except Exception as e:
                print(f"Error getting current price: {e}")
            
            # Analyze recommendations
            if recommendations is not None and not recommendations.empty:
                rating_weights = {
                    'strongBuy': 1.0,
                    'buy': 0.5,
                    'hold': 0.0,
                    'sell': -0.5,
                    'strongSell': -1.0
                }
                
                # Get the most recent period (0m)
                latest = recommendations[recommendations['period'] == '0m'].iloc[0]

                total_ratings = 0
                weighted_sum = 0.0
                
                for rating_type, weight in rating_weights.items():
                    if rating_type in latest:
                        count = latest[rating_type]
                        weighted_sum += count * weight
                        total_ratings += count
                
                if total_ratings > 0:
                    avg_sentiment = weighted_sum / total_ratings
                    sentiment_scores.append(avg_sentiment)
                    details['recommendations_count'] = total_ratings
            
            # Analyze price targets
            if analyst_price_targets is not None and current_price:
                target_mean = analyst_price_targets.get('targetMeanPrice')
                target_high = analyst_price_targets.get('targetHighPrice')
                target_low = analyst_price_targets.get('targetLowPrice')
                
                if target_mean and target_mean > 0:
                    price_sentiment = (target_mean - current_price) / current_price
                    price_sentiment = np.clip(price_sentiment * 2, -1, 1)
                    sentiment_scores.append(price_sentiment)
                    details['price_target_analyzed'] = target_mean
            
            if not sentiment_scores:
                print("ERROR: No sentiment scores could be calculated")
                return None
            
            avg_sentiment = np.mean(sentiment_scores)
            confidence = min(len(sentiment_scores) / 10, 1.0)  # Higher confidence with more data points

            res = SentimentSource(
                source_type="analyst_ratings",
                sentiment_score=avg_sentiment,
                confidence=confidence,
                volume=len(sentiment_scores),
                reliability=self.source_reliability['analyst_ratings'],
                details=details
            )
            
            return res
            
        except Exception as e:
            print(f"ERROR: Analyst sentiment analysis failed: {e}")
            return None


    def _analyze_social_media_sentiment(self, symbol: str, company_name: str) -> Optional[SentimentSource]:
        """Analyze social media sentiment (simplified - would need real API keys)"""
        try:
            # This is a placeholder for social media sentiment analysis
            # In reality, you would use APIs like:
            # - Twitter API v2 for tweets about the company/stock
            # - Reddit API for posts in r/stocks, r/investing, company-specific subreddits
            # - StockTwits API for financial social sentiment
            
            # For demonstration, using a simulated sentiment based on recent price action
            ticker = yf.Ticker(symbol)
            recent_data = ticker.history(period="5d")
            
            if recent_data.empty:
                return None
            
            # Simple proxy: recent price momentum as social sentiment indicator
            price_change = (recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[0]) / recent_data['Close'].iloc[0]
            volume_avg = recent_data['Volume'].mean()
            volume_recent = recent_data['Volume'].iloc[-1]
            
            # Simulate social sentiment based on price momentum and volume
            sentiment_score = np.clip(price_change * 3, -1, 1)  # Amplify price changes
            
            # Higher volume suggests more social media activity
            volume_factor = min(volume_recent / volume_avg, 2.0) if volume_avg > 0 else 1.0
            confidence = min(volume_factor / 2, 0.8)  # Max confidence of 0.8 for simulated data
            
            return SentimentSource(
                source_type="social_media",
                sentiment_score=sentiment_score,
                confidence=confidence,
                volume=int(volume_recent / 1000),  # Simulated social mentions
                reliability=self.source_reliability['social_media'],
                details={
                    'note': 'Simulated based on price momentum and volume',
                    'price_change_5d': price_change,
                    'volume_ratio': volume_factor
                }
            )
            
        except Exception as e:
            print(f"ERROR: Social media sentiment analysis error: {e}")
            return None

    def _analyze_insider_trading(self, symbol: str) -> Optional[SentimentSource]:
        """Analyze insider trading activity"""
        try:
            # Use yfinance to get insider transactions
            ticker = yf.Ticker(symbol)
            
            try:
                insider_transactions = ticker.insider_transactions
            except Exception as e:
                print(f"ERROR: Failed to access _insider transactions_ for {symbol}. Returning ...")
                return None
            
            if insider_transactions is None or insider_transactions.empty:
                print("ERROR: Access to _insider transactions_ yielded nothing")
                return None
            
            # Analyze recent transactions (last 90 days)
            cutoff_date = datetime.now() - timedelta(days=90)
            insider_transactions['Start Date'] = pd.to_datetime(insider_transactions['Start Date'], errors='coerce')
            recent_transactions = insider_transactions[
                insider_transactions['Start Date'] > cutoff_date
            ]
            
            if recent_transactions.empty:
                print("ERROR: Recent transactions are empty. Returning ...")
                return None
            
            # Calculate sentiment based on buy vs sell transactions
            buy_value = 0
            sell_value = 0
            transaction_count = 0
            
            for _, transaction in recent_transactions.iterrows():
                shares = transaction.get('Shares', 0)
                value = transaction.get('Value', 0)
                
                if shares > 0 and value > 0:  # Buy transaction
                    buy_value += value
                    transaction_count += 1
                elif shares < 0 and value > 0:  # Sell transaction
                    sell_value += value
                    transaction_count += 1
            
            if transaction_count == 0:
                print("WARNING: Found no transactions. Returning ...")
                return None
            
            total_value = buy_value + sell_value
            if total_value == 0:
                print("WARNING: No values have been determined for transactions. Returning ...")
                return None
            
            # Calculate sentiment: +1 for all buys, -1 for all sells
            net_sentiment = (buy_value - sell_value) / total_value
            confidence = min(transaction_count / 5, 1.0)  # Higher confidence with more transactions
            
            res = SentimentSource(
                source_type="insider_trading",
                sentiment_score=net_sentiment,
                confidence=confidence,
                volume=transaction_count,
                reliability=self.source_reliability['insider_trading'],
                details={
                    'buy_value': buy_value,
                    'sell_value': sell_value,
                    'transaction_count': transaction_count,
                    'period_days': 90
                }
            )

            return res
            
        except Exception as e:
            print(f"ERROR: Insider trading analysis error: {e}")
            return None

    def _analyze_options_flow(self, symbol: str) -> Optional[SentimentSource]:
        """Analyze options flow (simplified)"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get options data
            try:
                options_dates = ticker.options
                if not options_dates:
                    print("WARNING: Found no _options dates_. Returning ...")
                    return None
                
                # Get near-term options (first available expiration)
                options_chain = ticker.option_chain(options_dates[0])
                calls = options_chain.calls
                puts = options_chain.puts
                
            except Exception as e:
                return f"ERROR: Failed to get options data: {e}"
            
            if calls.empty and puts.empty:
                print("WARNING: Calls and/or Puts are empty. Returning ...")
                return None
            
            # Analyze call vs put volume and open interest
            call_volume = calls['volume'].sum()
            put_volume = puts['volume'].sum()
            
            call_oi = calls['openInterest'].sum()
            put_oi = puts['openInterest'].sum()
            
            total_volume = call_volume + put_volume
            total_oi = call_oi + put_oi
            
            if total_volume == 0 and total_oi == 0:
                print("WARNING: Total Volume and Open Interest don't have values. Returning ...")
                return None
            
            # Calculate put/call ratios
            pc_ratio_volume = put_volume / call_volume if call_volume > 0 else float('inf')
            pc_ratio_oi = put_oi / call_oi if call_oi > 0 else float('inf')
            
            # Lower P/C ratio = more bullish sentiment
            # Normalize to -1 (very bearish) to +1 (very bullish)
            if pc_ratio_volume == float('inf'):
                sentiment_volume = -1
            else:
                sentiment_volume = (1 - pc_ratio_volume) / (1 + pc_ratio_volume)
            
            if pc_ratio_oi == float('inf'):
                sentiment_oi = -1
            else:
                sentiment_oi = (1 - pc_ratio_oi) / (1 + pc_ratio_oi)
            
            # Average the two sentiments
            avg_sentiment = (sentiment_volume + sentiment_oi) / 2
            
            # Confidence based on total activity
            confidence = min(np.log(total_volume + 1) / 10, 0.8)
            
            res = SentimentSource(
                source_type="options_flow",
                sentiment_score=avg_sentiment,
                confidence=confidence,
                volume=int(total_volume),
                reliability=self.source_reliability['options_flow'],
                details={
                    'call_volume': call_volume,
                    'put_volume': put_volume,
                    'pc_ratio_volume': pc_ratio_volume,
                    'pc_ratio_oi': pc_ratio_oi,
                    'expiration_date': options_dates[0]
                }
            )

            return res
            
        except Exception as e:
            print(f"ERROR: Options flow analysis error: {e}")
            return None

    def _analyze_institutional_activity(self, symbol: str) -> Optional[SentimentSource]:
        """Analyze institutional holding changes"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get institutional holders
            try:
                institutional_holders = ticker.institutional_holders
            except Exception as e:
                print(f"ERROR: Failed to fetch instituitional holders: {e}")
                return None
            
            if institutional_holders is None or institutional_holders.empty:
                print("WARNING: Failed to retrieve data for instituitional holders. Returning ...")
                return None
            
            # This is simplified - in reality you'd track changes over time
            # For now, we'll use the concentration of institutional ownership as a proxy
            
            total_shares = ticker.info.get('sharesOutstanding', 0)
            
            # Calculate total institutional ownership
            total_institutional_shares = institutional_holders['Shares'].sum()
            institutional_percentage = (total_institutional_shares / total_shares) * 100
            
            # Higher institutional ownership generally indicates confidence
            # Normalize to sentiment score
            if institutional_percentage > 80:
                sentiment_score = 0.8
            elif institutional_percentage > 60:
                sentiment_score = 0.5
            elif institutional_percentage > 40:
                sentiment_score = 0.2
            elif institutional_percentage > 20:
                sentiment_score = 0.0
            else:
                sentiment_score = -0.3
            
            confidence = min(len(institutional_holders) / 20, 0.7)

            res = SentimentSource(
                source_type="institutional_activity",
                sentiment_score=sentiment_score,
                confidence=confidence,
                volume=len(institutional_holders),
                reliability=self.source_reliability['institutional_activity'],
                details={
                    'institutional_ownership_pct': institutional_percentage,
                    'num_institutions': len(institutional_holders),
                    'total_institutional_shares': total_institutional_shares
                }
            )
            
            return res
            
        except Exception as e:
            print(f"ERROR: Institutional activity analysis error: {e}")
            return None

    def _get_finbert_sentiment(self, text: str) -> Optional[Dict]:
        """Get sentiment using FinBERT model"""
        if not self.tokenizer or not self.model:
            print(f"WARNING: No tokenizer or model found for FinBERT")
            return None
        
        try:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            with torch.no_grad():
                logits = self.model(**inputs).logits
            
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]
            pred = torch.argmax(probs).item()
            
            return {
                "label": self.sentiment_labels[pred],
                "confidence": round(probs[pred].item(), 3),
                "score": round(probs[1].item() - probs[2].item(), 3)  # positive - negative
            }
        except Exception as e:
            print(f"ERROR: FinBERT sentiment error: {e}")
            return None

    def _calculate_overall_sentiment(self, sources: List[SentimentSource]) -> Dict:
        """Calculate overall sentiment from all sources"""
        if not sources:
            return {
                'weighted_score': 0.0,
                'recommendation': 'NEUTRAL',
                'confidence': 0.0,
                'reasoning': "No sentiment sources available"
            }
        
        total_weighted_score = 0
        total_weight = 0
        
        source_contributions = {}
        
        for source in sources:
            weight = self.source_weights.get(source.source_type)
            effective_weight = weight * source.confidence * source.reliability
            
            contribution = source.sentiment_score * effective_weight
            total_weighted_score += contribution
            total_weight += effective_weight
            
            source_contributions[source.source_type] = {
                'score': source.sentiment_score,
                'contribution': contribution,
                'weight': effective_weight,
                'volume': source.volume
            }
        
        # Calculate final sentiment score
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine recommendation
        if final_score > 0.3:
            recommendation = 'VERY_POSITIVE'
        elif final_score > 0.1:
            recommendation = 'POSITIVE'
        elif final_score > -0.1:
            recommendation = 'NEUTRAL'
        elif final_score > -0.3:
            recommendation = 'NEGATIVE'
        else:
            recommendation = 'VERY_NEGATIVE'
        
        confidence = min(abs(final_score) * 2, 1.0)
        
        res = {
            'weighted_score': final_score,
            'recommendation': recommendation,
            'confidence': confidence,
            'source_contributions': source_contributions,
            'sources_analyzed': len(sources),
            'reasoning': f"Sentiment score: {final_score:.3f} from {len(sources)} sources with {confidence:.1%} confidence"
        }

        return res

    def _categorize_sources(self, sources: List[SentimentSource]) -> Dict:
        """Categorize sentiment sources for analysis"""
        categories = {}
        for source in sources:
            categories[source.source_type] = {
                'sentiment_score': source.sentiment_score,
                'confidence': source.confidence,
                'volume': source.volume,
                'reliability': source.reliability
            }
        return categories
    
if __name__ == "__main__":
    alas = SentimentAnalyzer()
    s = alas.analyze_comprehensive_sentiment('AAPL', 'AAPL', 14)
    print(s)