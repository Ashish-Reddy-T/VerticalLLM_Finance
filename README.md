# Vertical LLM for Finance

Building a Vertical Large Language Model in the stock market sector:

- Using yahoo's financial data: `yfinance`. 
- Using local LLM: `Mistral 7b q4_K_M`.
- Be tuned as further developments are underway.

---

## Example Output

```
Agent: Loading configuration...
Agent: Initializing Mistral 7B model...

llama_init_from_model: n_ctx_per_seq (4096) < n_ctx_train (32768) -- the full capacity of the model will not be utilized
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

---
🤖 Financial Agent Initialized.
You can now ask questions about stock prices or general topics.
Type 'exit', 'quit', or 'q' to end the session.
---
You: Compare Apple and Tesla's performance over the last 3 months

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "compare_stocks",
            "action": "Compare Apple and Tesla's stock performance",
            "parameters": {
                "companies": ["Apple", "Tesla"],
                "period": "3mo"
            },
            "reasoning": "To understand the relative performance of both companies over the specified time period."
        }
    ]
}

Agent: Executing step 1: Compare Apple and Tesla's stock performance
Agent: Reason: To understand the relative performance of both companies over the specified time period.
Search Tool: Trying direct API fallback for 'Apple'...
Found symbol: AAPL
Fetch Tool: Fetching quote for 'AAPL' (period: 3mo)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'AAPL', 'current_price': np.float64(196.4499969482422), 'period_high': 225.32451569687797, 'period_low': 168.9884109270566, 'period_open': np.float64(210.97334672214788), 'latest_volume': np.float64(51362400.0), 'avg_volume': np.float64(61197071.875), 'period_change_pct': np.float64(-6.883973733911024), 'period': '3mo', 'data_points': 64}
Search Tool: Trying direct API fallback for 'Tesla'...
Found symbol: TSLA
Fetch Tool: Fetching quote for 'TSLA' (period: 3mo)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'TSLA', 'current_price': np.float64(325.30999755859375), 'period_high': 367.7099914550781, 'period_low': 214.25, 'period_open': np.float64(247.30999755859375), 'latest_volume': np.float64(128495300.0), 'avg_volume': np.float64(126490918.75), 'period_change_pct': np.float64(31.5393638631693), 'period': '3mo', 'data_points': 64}
Comparison Tool: Comparing 2 stocks over 3mo...

 ---------- COMPARISON ----------
{'period': '3mo', 'companies': {'Apple': {'symbol': 'AAPL', 'return_pct': np.float64(-6.883973733911024), 'current_price': np.float64(196.4499969482422), 'volatility': np.float64(6.883973733911024)}, 'Tesla': {'symbol': 'TSLA', 'return_pct': np.float64(31.5393638631693), 'current_price': np.float64(325.30999755859375), 'volatility': np.float64(31.5393638631693)}}, 'best_performer': 'Tesla', 'worst_performer': 'Apple', 'most_volatile': 'Tesla'}

--- Agent's Response ---
Over the past 3 months, I have analyzed the performance of both Apple (AAPL) and Tesla (TSLA). Here's the comparison:

1. Stock Performance:
   - Apple (AAPL) has seen a return of -6.88% during this period, with its current price at $196.45.
   - Tesla (TSLA), on the other hand, has performed significantly better, delivering a return of 31.54% and currently trading at $325.31.

2. Volatility:
   - Apple shows a lower volatility rate of 6.88%, indicating a relatively stable performance compared to its return.
   - Tesla demonstrates a much higher volatility rate of 31.54%, suggesting a more unpredictable stock price movement for Tesla compared to Apple.

In summary, Tesla has outperformed Apple over the last 3 months, delivering a much higher return. However, Tesla's performance is also more volatile compared to Apple's. It's essential to consider your investment goals and risk tolerance when deciding which stock to invest in.
------------------------

You: Show me Google's historical trends and current price

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "get_historical_data",
            "action": "Get Google's historical stock data",
            "parameters": {"ticker": "GOOGL", "period": "1y"},
            "reasoning": "To understand the long-term trends and performance of Google's stock"
        },
        {
            "tool": "get_stock_info",
            "action": "Get current price of Google's stock",
            "parameters": {"ticker": "GOOGL"},
            "reasoning": "To provide the user with the most recent price of Google's stock"
        }
    ]
}

Agent: Executing step 1: Get Google's historical stock data
Agent: Reason: To understand the long-term trends and performance of Google's stock
Search Tool: Trying direct API fallback for 'GOOGL'...
Found symbol: GOOGL
Analysis Tool: Analyzing historical data for 'GOOGL' (period: 1y)...

 ---------- HIST. ANALYSIS ----------
{'symbol': 'GOOGL', 'period': '1y', 'trend_direction': 'downward', 'volatility_pct': np.float64(7.715511068892697), 'ma_short': np.float64(176.48200073242188), 'ma_long': np.float64(172.6538101196289), 'highest_price': 205.89334106445312, 'lowest_price': 144.52503967285156, 'avg_daily_volume': np.float64(30410814.0), 'total_return_pct': np.float64(-0.7205564837898207)}

Agent: Executing step 2: Get current price of Google's stock
Agent: Reason: To provide the user with the most recent price of Google's stock
Search Tool: Trying direct API fallback for 'GOOGL'...
Found symbol: GOOGL
Fetch Tool: Fetching quote for 'GOOGL' (period: 1d)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'GOOGL', 'current_price': np.float64(174.6699981689453), 'period_high': 177.1300048828125, 'period_low': 172.38999938964844, 'period_open': np.float64(172.44000244140625), 'latest_volume': np.float64(27641100.0), 'avg_volume': np.float64(27641100.0), 'period_change_pct': np.float64(1.2932009371182869), 'period': '1d', 'data_points': 1}

--- Agent's Response ---
Based on the analysis, Google's (GOOGL) historical stock trends show a downward trend over the last year, with a total return of -0.72% during this period. The stock has experienced a volatility of 7.71% within this timeframe. The highest price recorded during this period was $205.89, while the lowest was $144.53. The average daily volume of Google's stock was approximately 30.41 million shares.

Currently, Google's stock is trading at $174.67, with a daily high of $177.13 and a daily low of $172.39. The latest volume is 27.64 million shares, which is also the average volume for the day. In the last 24 hours, the stock has experienced a change of 1.29%.

In summary, Google's stock has shown a downward trend over the last year, but has slightly increased in the last day. Keep in mind that this is a brief overview and it's essential to perform further analysis for a comprehensive understanding of Google's stock performance.
------------------------

You: Analyze Amazon's stock over the past 6 months and compare it with Microsoft

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "get_stock_info",
            "action": "Get Amazon's current stock data",
            "parameters": {"company": "Amazon", "period": "1d"},
            "reasoning": "To have the most recent data for further analysis"
        },
        {
            "tool": "get_historical_data",
            "action": "Get Amazon's stock data for the past 6 months",
            "parameters": {"company": "Amazon", "period": "6mo"},
            "reasoning": "To analyze Amazon's stock performance over the specified period"
        },
        {
            "tool": "get_stock_info",
            "action": "Get Microsoft's current stock data",
            "parameters": {"company": "Microsoft", "period": "1d"},
            "reasoning": "To have the most recent data for Microsoft"
        },
        {
            "tool": "get_historical_data",
            "action": "Get Microsoft's stock data for the past 6 months",
            "parameters": {"company": "Microsoft", "period": "6mo"},
            "reasoning": "To analyze Microsoft's stock performance over the specified period"
        },
        {
            "tool": "compare_stocks",
            "action": "Compare Amazon and Microsoft's stock performance",
            "parameters": {"companies": ["Amazon", "Microsoft"], "period": "6mo"},
            "reasoning": "To understand the relative performance of both companies' stocks over the specified period"
        }
    ]
}

Agent: Executing step 1: Get Amazon's current stock data
Agent: Reason: To have the most recent data for further analysis
Search Tool: Trying direct API fallback for 'Amazon'...
Found symbol: AMZN
Fetch Tool: Fetching quote for 'AMZN' (period: 1d)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'AMZN', 'current_price': np.float64(212.10000610351562), 'period_high': 214.0500030517578, 'period_low': 209.6199951171875, 'period_open': np.float64(209.9600067138672), 'latest_volume': np.float64(29300100.0), 'avg_volume': np.float64(29300100.0), 'period_change_pct': np.float64(1.0192414370441614), 'period': '1d', 'data_points': 1}

Agent: Executing step 2: Get Amazon's stock data for the past 6 months
Agent: Reason: To analyze Amazon's stock performance over the specified period
Search Tool: Trying direct API fallback for 'Amazon'...
Found symbol: AMZN
Analysis Tool: Analyzing historical data for 'AMZN' (period: 6mo)...

 ---------- HIST. ANALYSIS ----------
{'symbol': 'AMZN', 'period': '6mo', 'trend_direction': 'downward', 'volatility_pct': np.float64(8.919998351260817), 'ma_short': np.float64(214.6260009765625), 'ma_long': np.float64(211.4200012207031), 'highest_price': 242.05999755859375, 'lowest_price': 167.32000732421875, 'avg_daily_volume': np.float64(43799275.6097561), 'total_return_pct': np.float64(-8.942595297832339)}

Agent: Executing step 3: Get Microsoft's current stock data
Agent: Reason: To have the most recent data for Microsoft
Search Tool: Trying direct API fallback for 'Microsoft'...
Found symbol: MSFT
Fetch Tool: Fetching quote for 'MSFT' (period: 1d)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'MSFT', 'current_price': np.float64(474.9599914550781), 'period_high': 479.17999267578125, 'period_low': 472.760009765625, 'period_open': np.float64(476.4100036621094), 'latest_volume': np.float64(16806900.0), 'avg_volume': np.float64(16806900.0), 'period_change_pct': np.float64(-0.30436225013857215), 'period': '1d', 'data_points': 1}

Agent: Executing step 4: Get Microsoft's stock data for the past 6 months
Agent: Reason: To analyze Microsoft's stock performance over the specified period
Search Tool: Trying direct API fallback for 'Microsoft'...
Found symbol: MSFT
Analysis Tool: Analyzing historical data for 'MSFT' (period: 6mo)...

 ---------- HIST. ANALYSIS ----------
{'symbol': 'MSFT', 'period': '6mo', 'trend_direction': 'upward', 'volatility_pct': np.float64(7.467758016536679), 'ma_short': np.float64(474.0239990234375), 'ma_long': np.float64(469.6989990234375), 'highest_price': 478.8699951171875, 'lowest_price': 353.9102783203125, 'avg_daily_volume': np.float64(23005685.36585366), 'total_return_pct': np.float64(5.579414892830391)}

Agent: Executing step 5: Compare Amazon and Microsoft's stock performance
Agent: Reason: To understand the relative performance of both companies' stocks over the specified period
Search Tool: Trying direct API fallback for 'Amazon'...
Found symbol: AMZN
Fetch Tool: Fetching quote for 'AMZN' (period: 6mo)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'AMZN', 'current_price': np.float64(212.10000610351562), 'period_high': 242.52000427246094, 'period_low': 161.3800048828125, 'period_open': np.float64(230.22999572753906), 'latest_volume': np.float64(29300100.0), 'avg_volume': np.float64(43799275.6097561), 'period_change_pct': np.float64(-7.874729601037303), 'period': '6mo', 'data_points': 123}
Search Tool: Trying direct API fallback for 'Microsoft'...
Found symbol: MSFT
Fetch Tool: Fetching quote for 'MSFT' (period: 6mo)...

 ---------- CURR. ANALYSIS ----------
{'symbol': 'MSFT', 'current_price': np.float64(474.9599914550781), 'period_high': 480.4200134277344, 'period_low': 344.1581969485817, 'period_open': np.float64(445.55695084461104), 'latest_volume': np.float64(16806900.0), 'avg_volume': np.float64(23005685.36585366), 'period_change_pct': np.float64(6.599165506167013), 'period': '6mo', 'data_points': 123}
Comparison Tool: Comparing 2 stocks over 6mo...

 ---------- COMPARISON ----------
{'period': '6mo', 'companies': {'Amazon': {'symbol': 'AMZN', 'return_pct': np.float64(-7.874729601037303), 'current_price': np.float64(212.10000610351562), 'volatility': np.float64(7.874729601037303)}, 'Microsoft': {'symbol': 'MSFT', 'return_pct': np.float64(6.599165506167013), 'current_price': np.float64(474.9599914550781), 'volatility': np.float64(6.599165506167013)}}, 'best_performer': 'Microsoft', 'worst_performer': 'Amazon', 'most_volatile': 'Amazon'}

--- Agent's Response ---
Over the past 6 months, Amazon's stock performance has shown a downward trend with a total return of -7.87%. The stock's volatility percentage is 8.91%, and the average daily volume is approximately 43.79 million shares. The lowest price recorded during this period was $167.32, and the highest price was $242.06. On the other hand, Microsoft's stock has performed better, with a total return of 6.59%. The stock's volatility percentage is 7.46%, and the average daily volume is approximately 23 million shares. The lowest price recorded during this period was $353.91, and the highest price was $478.87.

Comparing the two companies, Microsoft has outperformed Amazon over the past 6 months with a higher total return. However, Amazon's stock has been more volatile during this period. In terms of the most recent data, as of today, Amazon's stock price is $212.10, while Microsoft's stock price is $474.96.
------------------------

You: exit
🤖 Agent: Goodbye!
```

---