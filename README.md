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
Search Tool: Trying direct API fallback for 'Tesla'...
Found symbol: TSLA
Fetch Tool: Fetching quote for 'TSLA' (period: 3mo)...
Comparison Tool: Comparing 2 stocks over 3mo...

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

Agent: Executing step 2: Get current price of Google's stock
Agent: Reason: To provide the user with the most recent price of Google's stock
Search Tool: Trying direct API fallback for 'GOOGL'...
Found symbol: GOOGL
Fetch Tool: Fetching quote for 'GOOGL' (period: 1d)...

--- Agent's Response ---
Based on the analysis, Google's (GOOGL) historical stock trends show a downward trend over the last year, with a total return of -0.72% during this period. The stock has experienced a volatility of 7.71% within this timeframe. The highest price recorded during this period was $205.89, while the lowest was $144.52. The average daily volume over this period was approximately 30.41 million shares.

Currently, as of the latest data point (today), Google's stock is trading at $174.67. The stock opened at $172.44 today, and has seen a daily change of +1.29%. The highest and lowest prices recorded today were $177.13 and $172.39 respectively. The latest volume traded was 27.64 million shares, with an average volume of the same amount.

In summary, Google's stock has shown a downward trend over the last year, but has seen a slight increase in price today. It is important to consider these trends and factors, along with other relevant information, before making any investment decisions.
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

Agent: Executing step 2: Get Amazon's stock data for the past 6 months
Agent: Reason: To analyze Amazon's stock performance over the specified period
Search Tool: Trying direct API fallback for 'Amazon'...
Found symbol: AMZN
Analysis Tool: Analyzing historical data for 'AMZN' (period: 6mo)...

Agent: Executing step 3: Get Microsoft's current stock data
Agent: Reason: To have the most recent data for Microsoft
Search Tool: Trying direct API fallback for 'Microsoft'...
Found symbol: MSFT
Fetch Tool: Fetching quote for 'MSFT' (period: 1d)...

Agent: Executing step 4: Get Microsoft's stock data for the past 6 months
Agent: Reason: To analyze Microsoft's stock performance over the specified period
Search Tool: Trying direct API fallback for 'Microsoft'...
Found symbol: MSFT
Analysis Tool: Analyzing historical data for 'MSFT' (period: 6mo)...

Agent: Executing step 5: Compare Amazon and Microsoft's stock performance
Agent: Reason: To understand the relative performance of both companies' stocks over the specified period
Search Tool: Trying direct API fallback for 'Amazon'...
Found symbol: AMZN
Fetch Tool: Fetching quote for 'AMZN' (period: 6mo)...
Search Tool: Trying direct API fallback for 'Microsoft'...
Found symbol: MSFT
Fetch Tool: Fetching quote for 'MSFT' (period: 6mo)...
Comparison Tool: Comparing 2 stocks over 6mo...

--- Agent's Response ---
Over the past 6 months, Amazon's stock performance has shown a downward trend with a total return of -8.94%. The stock's volatility, measured as a percentage, is 8.91%. The highest price recorded during this period was $242.06, while the lowest was $167.32. The average daily volume was approximately 43.79 million shares. As for the recent 1-day data, Amazon's stock closed at $212.10, marking a 1.02% increase from the previous day's close.

Comparing Amazon's performance with Microsoft over the same period, Microsoft has shown an upward trend with a total return of 5.58%. Microsoft's stock's volatility, measured as a percentage, is 7.47%. The highest price recorded during this period was $478.87, while the lowest was $353.91. The average daily volume was approximately 23 million shares. In the recent 1-day data, Microsoft's stock closed at $474.96, marking a -0.30% decrease from the previous day's close.

Based on the analysis, Microsoft has outperformed Amazon over the past 6 months. Additionally, Microsoft's stock has shown lower volatility compared to Amazon during the same period.
------------------------

You: exit
🤖 Agent: Goodbye!
```

---