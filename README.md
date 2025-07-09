# Vertical LLM for Finance

A Python-based assistant for analyzing equities using local large language models and traditional market data sources.

## Repository Structure

- `agent.py` – orchestrates the language model and analysis tools
- `financial_tools.py` – helpers for retrieving market data
- `fundamental_analysis.py` – fundamental metrics and scoring
- `technical_analysis.py` – technical indicator calculations
- `sentiment_analysis.py` – sentiment scoring
- `self_rag.py` / `rag_core.py` – retrieval augmented generation components
- `main.py` – simple chat interface

## Usage

Start an interactive session:
```bash
python main.py
```
Follow the prompts to ask questions about a stock.

## Disclaimer

All outputs from this project are provided for informational purposes only and do not constitute financial advice. Always conduct your own research before making investment decisions.

## Example Output


```
You: Analyze Apple's fundamentals

--- Agent's Response ---
Investment Recommendation: Neutral (0.0686 confidence level)

Apple Inc. (AAPL) currently stands at a Neutral investment recommendation, based on a comprehensive fundamental analysis of 18 key metrics across six categories. The confidence level for this recommendation is 0.0686.

Valuation Metrics:
Apple's valuation metrics show mixed results. The Price-to-Earnings (PE) ratio of 32.62, Price-to-Book (PB) ratio of 46.91, and Price-to-Sales (PS) ratio of 7.82 are all significantly higher than the industry average, suggesting an overvalued position. However, the company has a high cash-to-market-cap ratio of 1.54, indicating a strong financial position and a potential undervaluation.

Profitability Metrics:
Apple demonstrates strong profitability, with a Return on Equity (ROE) of 138.01, Return on Assets (ROA) of 23.81, Gross Margin of 46.63%, and Operating Margin of 31.03%. These figures exceed the industry averages, indicating Apple's ability to generate substantial profits from its assets and operations.

Growth Metrics:
Growth metrics for Apple are relatively neutral, with quarterly revenue growth at -23.28% and annual revenue growth at 5.1%. While these figures show a slight decline in the short term, they are still indicative of a consistently growing company. Earnings growth stands at 7.8%, which is in line with the industry average.

Financial Health Metrics:
Apple's financial health metrics are mostly positive. The company has a debt-to-equity ratio of 1.47, which is higher than the ideal but still manageable. The Current Ratio of 0.82 and Quick Ratio of 0.68 suggest that Apple has sufficient liquidity to cover its short-term obligations. However, the Dividend Yield and Payout Ratio are both at 51.0% and 15.58%, respectively, which may indicate that the company is returning too much capital to shareholders, potentially limiting reinvestment opportunities.

Dividend and Market Metrics:
Apple offers a dividend yield of 51.0%, which is high compared to the industry average. However, the company's market capitalization of $3.13 trillion places it among the largest companies in the world, making it difficult to achieve significant returns through price appreciation alone.

Long-Term Investment Perspective:
Apple's strong profitability, consistent growth, and substantial financial resources position it well for long-term growth. However, the high valuation metrics warrant caution, as they may limit the potential for significant price appreciation in the short term. Investors should consider Apple as part of a diversified portfolio, focusing on its long-term potential and the company's ability to maintain its competitive advantage in the consumer electronics market.

In conclusion, while Apple's fundamentals show a mixed picture, the company's strong profitability, consistent growth, and substantial financial resources position it well for long-term growth. The high valuation metrics warrant caution, but with a focus on the long term, Apple remains an attractive investment opportunity.
------------------------

You: What's the sentiment on Tesla?

🤖 Agent: Generating ...

--- Agent's Response ---
Based on our comprehensive sentiment analysis, the current sentiment for Tesla (TSLA) is POSITIVE, with a score of 0.2072. This positive sentiment is derived from six different sources, each with varying levels of reliability and volume.

1. News Sentiment: News articles analyzed show a slightly negative sentiment towards Tesla, with a score of -0.186. This negative sentiment is based on a volume of 46 articles from 13 unique sources, over the period of July 3 to July 10, 2025.

2. Analyst Ratings: Analysts have a slightly positive view of Tesla, with a score of 0.159. This is based on one recommendation, with a current price of $296.72.

3. Social Media: Social media sentiment shows a negative sentiment towards Tesla, with a score of -0.179. This sentiment is based on a volume of 61,778 posts, with a 0.33 confidence level.

4. Insider Trading: Insiders have been buying shares of Tesla, with a total volume of 20 transactions and a value of $305,304,377, contributing a positive score of 1.0 to the overall sentiment.

5. Options Flow: The options flow analysis indicates a slightly negative sentiment, with a score of -0.097. This sentiment is based on a volume of 790,465 options, with a 0.8 confidence level.

6. Institutional Activity: Institutional activity shows no significant sentiment, with a score of 0.0. This is based on a volume of 10 institutions and a total institutional shares ownership of 84,834,958.

It's important to note that while insider trading and institutional activity indicate a positive sentiment, they are slightly contradicted by the news sentiment and options flow analysis, which show a slightly negative sentiment. However, the overall sentiment remains positive due to the majority of sources leaning towards a positive outlook.

In terms of the short-term market perspective, the positive sentiment suggests that investors are optimistic about Tesla's future performance. However, the conflicting signals from news sentiment and options flow analysis indicate that there may be some underlying concerns or uncertainties that investors should be aware of. As always, it's important to conduct further research and consider professional advice before making investment decisions.
------------------------

You: should I buy microsoft's stocks right now?

--- Agent's Response ---
Based on the comprehensive technical analysis, it is recommended to buy Microsoft (MSFT) stocks with a confidence level of 66.91%. The analysis indicates a strong bullish trend across multiple timeframes, supported by several technical indicators.

Key Technical Indicators:
- The Average Directional Index (ADX) signals a strong uptrend across 15-minute, 1-hour, 4-hour, and 1-day timeframes, with strengths ranging from 0.56 to 0.92.
- The Relative Strength Index (RSI) shows overbought conditions on the 1-day timeframe, but the Williams %R indicator also indicates overbought conditions on the 15-minute and 1-day timeframes.
- A hanging man candlestick pattern is observed on the 1-hour timeframe, which could be a bearish signal, but its impact is somewhat offset by the overall bullish trend.

Multi-timeframe Confluence and Signal Strength:
The confluence analysis results in a score of 4.54, which is above the recommended threshold of 0.6, indicating a strong bullish signal. This score is derived from the bullish ADX signals across different timeframes.

Entry/Exit Levels and Risk-Reward Ratio:
- Entry Price: Current price is $502.61
- Target Price: $506.78
- Stop Loss: $466.96
- Potential Profit: $4.17
- Potential Loss: $35.65
- Risk-Reward Ratio: 0.117

Risk Management Considerations:
Given the high potential loss and moderate risk-reward ratio, it's essential to manage the risk by setting a stop loss at $466.96 to limit potential losses.

Strongest Signals and Conflicting Indicators:
The strongest signals are the bullish ADX signals across different timeframes, while the conflicting indicators are the overbought conditions indicated by the RSI on the 1-day timeframe and the hanging man candlestick pattern on the 1-hour timeframe.

In conclusion, while the overall trend is bullish, there are some conflicting indicators that suggest caution. It is recommended to buy Microsoft stocks with a stop loss at $466.96, but it would be prudent to monitor the situation closely and consider the potential risks involved.
------------------------
```

---