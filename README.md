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
Agent: Initializing Self-RAG system...

---
🤖 Financial Agent Initialized.
You can now ask questions about stock prices or general topics.
Type 'exit', 'quit', or 'q' to end the session.
---
You: hi there.

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": false,
    "steps": []
}

This initial response is to acknowledge the user's greeting and does not require any specific tool or action. It simply sets the stage for further interactions related to financial planning and analysis.

Agent: No specific tools needed. Using Self-RAG analysis for this.
INFO: RETRIEVE0 (yes/no): no

Agent: No Self-RAG required. Using LLM knowledge for to answer.

--- Agent's Response ---
Hello! How can I assist you today? 😊 If you have any questions or need help with something, feel free to ask. 😊

Here are a few things I can help you with:

1. Answering questions about various topics (e.g., science, math, history, literature, etc.)
2. Providing explanations for complex concepts
3. Helping you solve problems
4. Generating ideas for projects or assignments
5. Offering suggestions for books, movies, or TV shows based on your preferences
6. Providing fun facts, trivia, and jokes
7. And much more! Just let me know what you need. 😊

If you're not sure what you need help with, feel free to ask me anything that comes to mind, and I'll do my best to assist you. 😊

Enjoy your day! 😊
------------------------

You: what is x: x^2+3x+2=0

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": false,
    "steps": []
}

This query is not related to financial analysis, but rather a mathematical equation. To solve for x, you can use the quadratic formula: x = [-b ± sqrt(b^2 - 4ac)] / 2a. In this case, a = 1, b = 3, and c = 2. So, x = [-3 ± sqrt((3)^2 - 4*1*2)] / 2*1. The solution would be x1 = [-3 + sqrt(9 - 8)] / 2 and x2 = [-3 - sqrt(9 - 8)] / 2.

Agent: No specific tools needed. Using Self-RAG analysis for this.
INFO: RETRIEVE0 (yes/no): no

Agent: No Self-RAG required. Using LLM knowledge for to answer.

--- Agent's Response ---
To find the solutions for the quadratic equation x^2 + 3x + 2 = 0, we can use the quadratic formula:

x = (-b ± √(b² - 4ac)) / 2a

In this case, a = 1, b = 3, and c = 2.

Plugging these values into the formula, we get:

x = (-3 ± √(3² - 4*1*2)) / (2*1)
x = (-3 ± √(9 - 8)) / 2
x = (-3 ± √1) / 2

Since √1 = 1, we have two possible solutions:

x1 = (-3 + 1) / 2 = -1
x2 = (-3 - 1) / 2 = -2

So the solutions for the given quadratic equation are x1 = -1 and x2 = -2.
------------------------

You: what is eps?

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": false,
    "steps": []
}

Explanation:
The user is asking for the definition of EPS (Earnings Per Share). No tools are needed to provide this information. A simple explanation can be given as follows:

EPS is a financial metric that measures a company's profitability by revealing how much of its earnings can be attributed to each outstanding share of common stock. It is calculated by dividing a company's net income by the number of outstanding shares of common stock. EPS is a key indicator of a company's profitability and is often used to compare the performance of different companies.

Agent: No specific tools needed. Using Self-RAG analysis for this.
INFO: RETRIEVE0 (yes/no): yes
INFO: RETRIEVE1 (relevant/irrelevant/partial): irrelevant
INFO: RETRIEVE1 (relevant/irrelevant/partial): irrelevant
INFO: RETRIEVE1 (relevant/irrelevant/partial): irrelevant
INFO: RETRIEVE1 (relevant/irrelevant/partial): irrelevant
INFO: RETRIEVE1 (relevant/irrelevant/partial): irrelevant
INFO: RETRIEVE1 (relevant/irrelevant/partial): irrelevant

--- Agent's Response ---
The question is asking about EPS, which stands for "Earnings Per Share." This is a common financial metric that measures a company's profitability by dividing its total earnings by the number of outstanding shares of its common stock.

In the provided context, the calculation of EPS is explained with a formula:

- Operating profit plus depreciation plus amortization of goodwill minus Federal income tax (paid at the company’s average rate) minus cost of stock options minus “maintenance” (or essential) capital expenditures minus any income generated by unsustainable rates of return on pension funds (as of 2003, anything greater than 6.5%) and where Invested Capital is equal to: Total assets minus cash (as well as short-term investments and non-interest-bearing current liabilities) plus past accounting charges that reduced invested capital.

However, it is important to note that EPS has been distorted in recent years by factors like stock-option grants and accounting gains and charges. To see how much a company is truly earning on the capital it deploys in its businesses, it is recommended to look beyond EPS to ROIC (Return on Invested Capital). This formula shows, after all legitimate expenses, what the company earns from its operating businesses and how efficiently it has used the shareholders’ money to generate that return. An ROIC of at least 10% is attractive; even 6% or 7% can be tempting if the company has good brand names, focused management, or is under a temporary cloud.

In conclusion, while EPS is a useful metric for understanding a company's profitability, it is essential to consider other factors such as ROIC to gain a more comprehensive understanding of the company's financial health.
------------------------

You: compare apple's stock with google's stock over the last quarter (which is 3 months).

🤖 Agent is thinking...

 ---------- INFO ----------
{
    "needs_tools": true,
    "steps": [
        {
            "tool": "compare_stocks",
            "action": "Compare Apple's and Google's stock performance",
            "parameters": {
                "companies": ["Apple", "Google"],
                "period": "3mo"
            },
            "reasoning": "To understand the relative stock performance of Apple and Google over the last quarter."
        }
    ]
}

Agent: Executing step 1: Compare Apple's and Google's stock performance
Agent: Reason: To understand the relative stock performance of Apple and Google over the last quarter.
Search Tool: Trying direct API fallback for 'Apple'...
Found symbol: AAPL
Fetch Tool: Fetching quote for 'AAPL' (period: 3mo)...
Search Tool: Trying direct API fallback for 'Google'...
Found symbol: GOOG
Fetch Tool: Fetching quote for 'GOOG' (period: 3mo)...
Comparison Tool: Comparing 2 stocks over 3mo...

--- Agent's Response ---
Over the past three months, the performance of Apple's stock (AAPL) has been less favorable compared to Google's stock (GOOG). In particular, Google's stock has seen a return of approximately 6.52%, while Apple's stock has experienced a decline of around 6.88%.

It's worth noting that both stocks have shown similar levels of volatility during this period, with Apple's stock volatility being 6.88% and Google's being 6.52%.

As of the current date, the closing prices for Apple's stock and Google's stock were $196.45 and $175.88 respectively.

In summary, Google's stock has outperformed Apple's stock over the last quarter, with a higher return percentage. However, both stocks have exhibited similar levels of volatility.
------------------------

You: exit
🤖 Agent: Goodbye!
```

---