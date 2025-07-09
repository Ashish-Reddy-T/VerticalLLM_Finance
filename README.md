# Vertical LLM for Finance

A Python-based assistant for analyzing equities using local large language models and traditional market data sources.

## Repository Structure

- `agent.py` – orchestrates the language model and analysis tools
- `financial_tools.py` – helpers for retrieving market data
- `fundamental_analysis.py` – fundamental metrics and scoring
- `technical_analysis.py` – technical indicator calculations
- `sentiment_analysis.py` – sentiment scoring
- `self_rag.py` / `rag_core.py` – retrieval augmented generation components
- `data/` – FAISS index for RAG
- `documents/` – example PDF documents for ingestion
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
Agent: Loading configuration...
Agent: Initializing Mistral 7B model...

llama_init_from_model: n_ctx_per_seq (8192) < n_ctx_train (32768) -- the full capacity of the model will not be utilized
ggml_metal_init: skipping kernel_get_rows_bf16                     (not supported)
ggml_metal_init: skipping kernel_mul_mv_bf16_f32                   (not supported)
ggml_metal_init: skipping kernel_mul_mv_bf16_f32_1row              (not supported)
ggml_metal_init: skipping kernel_mul_mv_bf16_f32_l4                (not supported)
ggml_metal_init: skipping kernel_mul_mv_bf16_bf16                  (not supported)
ggml_metal_init: skipping kernel_mul_mv_id_bf16_f32                (not supported)
ggml_metal_init: skipping kernel_mul_mm_bf16_f32                   (not supported)
ggml_metal_init: skipping kernel_mul_mm_id_bf16_f32                (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_bf16_h64           (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_bf16_h80           (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_bf16_h96           (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_bf16_h112          (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_bf16_h128          (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_bf16_h256          (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_vec_bf16_h128      (not supported)
ggml_metal_init: skipping kernel_flash_attn_ext_vec_bf16_h256      (not supported)
ggml_metal_init: skipping kernel_cpy_f32_bf16                      (not supported)
ggml_metal_init: skipping kernel_cpy_bf16_f32                      (not supported)
ggml_metal_init: skipping kernel_cpy_bf16_bf16                     (not supported)

Agent: Model loaded successfully.
Agent: Initializing Technical Analysis system...
Agent: Initializing Fundamental Analysis system...
Agent: Initializing Sentiment Analysis system...
Agent: FinBERT model loaded successfully
Agent: Initializing Self-RAG system...

---
🤖 Financial Agent Initialized.
You can now ask questions about stock prices or general topics.
Type 'exit', 'quit', or 'q' to end the session.
---
You: Analyze Apple's fundamentals

🤖 Agent is thinking...

 ---------- EXECUTION PLAN ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "comprehensive_fundamental_analysis",
            "action": "Perform a complete fundamental analysis of Apple",
            "parameters": {"company_name": "Apple"}
        }
    ]
}

Agent: Executing step 1: Perform a complete fundamental analysis of Apple
Agent: Found symbol: AAPL
Agent: Executing comprehensive fundamental analysis for AAPL
Agent: Executing comprehensive fundamental analysis for AAPL

--- Agent's Response ---
Investment Recommendation: Neutral (0.0686 confidence level)

Apple Inc. (AAPL) currently stands at a Neutral investment recommendation, based on a comprehensive fundamental analysis of 18 key metrics across six categories. The confidence level for this recommendation is 0.0686.

Valuation Metrics:
Apple's PE (Price-to-Earnings) ratio is significantly higher than the industry average, indicating the stock may be overvalued at 32.62. Meanwhile, the PB (Price-to-Book) ratio also sits above average, suggesting a relatively expensive valuation (46.92). However, the PS (Price-to-Sales) ratio is within expected ranges, providing some balance to the valuation outlook.

Profitability Metrics:
Apple's profitability is robust, with a Return on Equity (ROE) of 138.01 and Return on Assets (ROA) of 23.81. Both metrics outperform industry averages, demonstrating the company's ability to generate strong profits from its assets. The gross and operating margins also support this finding.

Growth Metrics:
Growth metrics for Apple show mixed results. While the company's revenue and earnings have grown at a moderate pace, the quarterly revenue growth rate has experienced a decline. This suggests that while Apple has maintained growth, it may be slowing down compared to historical trends.

Financial Health Metrics:
Apple's financial health metrics present some concerns. The debt-to-equity and current ratios are higher than the industry average, suggesting a higher level of debt relative to equity and a slightly weaker short-term liquidity position. However, the quick ratio remains within acceptable ranges.

Dividend Metrics:
Apple offers a dividend yield of 51.0%, which is well above the industry average. The company's payout ratio is also high, indicating a substantial portion of earnings are being paid out as dividends.

Market Metrics:
Apple's market capitalization is massive, currently standing at over $3 trillion. The beta value of 1.21 indicates the stock's volatility is slightly higher than the overall market.

Long-Term Investment Perspective:
Apple's strong profitability and financial health, combined with its leadership position in the technology sector, make it an attractive long-term investment opportunity. However, the high valuation metrics and concerns regarding growth and financial health should be carefully considered before making investment decisions.

In conclusion, while Apple's fundamentals show several positive aspects, potential investors should be aware of the high valuation, slowing growth, and financial health concerns. A Neutral investment recommendation is given, with a confidence level of 0.0686. It is recommended to consult with a financial advisor before making investment decisions.
------------------------

You: What's the sentiment on Tesla?

🤖 Agent is thinking...

 ---------- EXECUTION PLAN ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "comprehensive_sentiment_analysis",
            "action": "Analyze the sentiment on Tesla",
            "parameters": {"stock_symbol": "TSLA"}
        }
    ]
}

Agent: Executing step 1: Analyze the sentiment on Tesla
Agent: Found symbol: TSLA
Agent: Executing comprehensive sentiment analysis for TSLA
Agent: Executing comprehensive sentiment analysis for TSLA

--- Agent's Response ---
Based on our comprehensive sentiment analysis, the current sentiment for Tesla (TSLA) is NEUTRAL, with a sentiment score of -0.07948572665053506. This score was derived from four distinct sentiment sources: news sentiment, social media, options flow, and institutional activity.

1. News Sentiment: We analyzed 47 articles from 10 unique sources in the timeframe of July 1, 2025 to July 8, 2025. The sentiment score for news sources was -0.009201577086921058, with a confidence level of 93.9%.

2. Social Media: Our analysis of social media data revealed a sentiment score of -0.2327951463159627, based on a volume of 107,426 posts. The confidence level for this source was 52.9%.

3. Options Flow: The options flow analysis showed a sentiment score of -0.2170535821157143, with a high volume of 1,237,587 contracts. The reliability of this data was 60%.

4. Institutional Activity: Our institutional activity analysis showed no clear sentiment, with a confidence level of 50%. We observed that institutional ownership stands at 26.34%, with a total of 10 institutions holding 84,834,958 shares.

It's important to note that while most sentiment sources indicate a neutral sentiment, there is some discrepancy between the news sentiment and social media sentiment. The news sentiment is slightly positive, while social media sentiment is slightly negative.

In terms of short-term market perspective, the neutral sentiment suggests a balanced outlook for Tesla. However, the discrepancy between news and social media sentiment could indicate potential market volatility in the near future. Traders and investors should closely monitor these trends and adjust their strategies accordingly.

As always, this sentiment analysis should be used as a tool for making informed investment decisions, but it should not be the sole basis for those decisions. It's recommended to conduct additional research and consider multiple factors before making investment decisions.
------------------------

You: should I buy microsoft's stocks or no?

🤖 Agent is thinking...

 ---------- EXECUTION PLAN ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "comprehensive_analysis",
            "action": "Perform a complete analysis of Microsoft's stocks",
            "parameters": {"stock_symbol": "MSFT"}
        }
    ]
}

Agent: Executing step 1: Perform a complete analysis of Microsoft's stocks
Agent: Executing comprehensive enhanced analysis for MSFT...
Agent: Found symbol: MSFT
Agent: Executing comprehensive technical analysis for MSFT
Agent: Executing comprehensive technical analysis for MSFT
Agent: Found symbol: MSFT
Agent: Executing comprehensive fundamental analysis for MSFT
Agent: Executing comprehensive fundamental analysis for MSFT
Agent: Found symbol: MSFT
Agent: Executing comprehensive sentiment analysis for MSFT
Agent: Executing comprehensive sentiment analysis for MSFT

Enhanced Analysis Summary for MSFT:
Final Recommendation: STRONG_BUY
Overall Confidence: 0.416
Technical Contribution: 0.362
Fundamental Contribution: 0.021
Sentiment Contribution: 0.033
Total Score: 0.416


--- Agent's Response ---
Based on the comprehensive technical analysis of Microsoft Corporation (MSFT), we recommend a STRONG BUY with a confidence level of 72.4%. Our recommendation is supported by a confluence of six technical indicators across different categories.

Key Technical Indicators:

1. Trend Indicators: ADX (Average Directional Movement Index) indicates a strong uptrend in the 4-hour and 1-day timeframes, signaling a persistent and strong directional movement in the price. However, a strong downtrend was detected in the 15-minute timeframe, which might be a temporary trend.

2. Momentum Oscillators: None of the momentum oscillators were utilized in this analysis.

3. Volume Indicators: The OBV (On-Balance Volume) suggests a bearish trend in the 1-day timeframe, meaning that there's been more selling volume than buying volume during this period.

4. Candlestick Patterns: A bullish engulfing pattern was detected in the 1-hour timeframe, which typically indicates a potential reversal from a downtrend to an uptrend.

5. Volatility Indicators: No volatility indicators were used in this analysis.

Multi-Timeframe Confluence and Signal Strength:
The confluence score is 0.185, which is above the threshold of 0.15, indicating a high probability of a successful trade. The strongest signals are the ADX strong uptrend in the 4-hour and 1-day timeframes, as well as the bullish engulfing pattern in the 1-hour timeframe.

Entry/Exit Levels and Risk-Reward Ratio:
If you decide to enter a long position, consider entering at around 496.60 (current price) and setting a stop loss at 466.96 (1-day low). The potential profit is around 4.72, while the potential loss is 29.64. This results in a risk-reward ratio of 0.159, indicating a relatively high risk.

Risk Management Considerations:
Given the high risk-reward ratio, it is crucial to employ proper risk management strategies, such as setting a stop loss and taking profits at specific levels.

Strongest Signals and Conflicting Indicators:
The strongest signals are the ADX strong uptrend in the 4-hour and 1-day timeframes, as well as the bullish engulfing pattern in the 1-hour timeframe. However, the conflicting indicator is the OBV bearish trend in the 1-day timeframe, which suggests that the price may continue to decline in the short term despite the bullish signals.

In conclusion, based on the technical analysis, we recommend a STRONG BUY of Microsoft Corporation (MSFT) with a confidence level of 72.4%. However, due to the high risk-reward ratio, proper risk management strategies should be employed. Additionally, it is essential to stay updated on the latest news and events that may impact the stock price.
------------------------

You: exit
🤖 Agent: Goodbye!

```

---