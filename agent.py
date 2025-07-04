from llama_cpp import Llama

from utils import get_config
from financial_tools import (
    search_yahoo_api, 
    get_stock_quote, get_historical_analysis, compare_stock_data, get_news_sentiment,
    get_multi_timeframe_data, analyze_pattern_confluence
)
from self_rag import SelfRAG

# Initialize LLM
print("Agent: Loading configuration...")
config_file = get_config()
model_path = config_file.get('model', {}).get('path') # Modify this if deploying! (to include models dir)

print("Agent: Initializing Mistral 7B model...\n")
llm = Llama(
    model_path=model_path,
    n_gpu_layers=-1,                # Offload all layers to the GPU (my mac has 14 GPU cores)
    n_ctx=8192,                     # Set context window size
    chat_format="mistral-instruct", # Use the correct chat template for this model
    verbose=False                   # Keep the output clean
)
print("\nAgent: Model loaded successfully.")

print("Agent: Initializing Self-RAG system...")
self_rag = SelfRAG(llm)

# Define the Tools the Agent could Use
tools = {
    "get_stock_info": {
        "description": "Get current or recent stock price, volume, and trading data for a company. Can specify period like '1d', '5d', '1mo'.",
        "function": "get_stock_quote"
    },
    "get_historical_data": {
        "description": "Get historical stock data and trends for analysis over periods like '1mo', '3mo', '6mo', '1y'.",
        "function": "get_historical_analysis"
    },
    "compare_stocks": {
        "description": "Compare multiple companies' stock performance over a specified time period.",
        "function": "compare_stock_data"
    },
    "analyze_candlestick_patterns": {
        "description": "Analyze candlestick patterns across multiple timeframes(15m, 1h, 4h, 1d) to generate buy/sell signals.",
        "function": "execute_candlestick_analysis"
    },
    "comprehensive_analysis": {
        "description": "Complete analysis combining fundamentals, technicals, and candlestick patterns for trading decisions.",
        "function": "execute_comprehensive_analysis"
    }
}   

# Core Agent Logic (Follow ReAct format)
def handle_query(query: str) -> str:
    """
    Handles a user query by following an enhanced ReAct framework with planning.
    """
    
    # Step 1: PLAN - Create execution plan
    execution_plan = create_execution_plan(query) 
    
    if not execution_plan['needs_tools'] or not execution_plan['steps']:
        print("\nAgent: No specific tools needed. Using Self-RAG analysis.")
        return self_rag.generate_with_rag(query)    
      
    # Step 2: EXECUTE - Run the planned steps
    results = {}
    for i, step in enumerate(execution_plan['steps']):
        print(f"\nAgent: Executing step {i+1}: {step['action']}")

        step_result = execute_tool_step(step, results) 
        results[f"step_{i+1}"] = step_result
        
        if "ERROR" in str(step_result):
            return f"I encountered an error during step {i+1}: {step_result}"
    
    # Step 3: SYNTHESIZE - Generate final response
    return synthesize_response(query, execution_plan, results)

def create_execution_plan(query: str) -> dict:
    """
    Creates a multi-step execution plan for complex queries.
    """
    tool_descriptions = "\n".join([f"- {key}: {value['description']}" for key, value in tools.items()])
    
    planning_prompt = f"""
[INST] You are an expert financial assistant planner. Analyze the user's query and create a step-by-step execution plan.

Available tools:
{tool_descriptions}

QUERY ANALYSIS GUIDELINES:
- If query mentions "patterns", "candlestick", "technical", "buy", "sell", "signal" → use analyze_candlestick_patterns
- If query asks for "complete analysis", "recommendation", "should I buy/sell" → use comprehensive_analysis  
- If query compares multiple stocks → use compare_stocks
- If query asks for basic info only → use get_stock_info or get_historical_data
- If query is general knowledge → set needs_tools: false

For each step, specify:
1. The tool to use
2. The description of the query
3. The specific parameters needed  

Respond in this exact JSON format:
{{
    "needs_tools": true/false,
    "steps": [
        {{
            "tool": "tool_name",
            "action": "brief description",
            "parameters": {{"param1": "value1"}},
        }}
    ]
}}

If no tools are needed and the query is general knowledge → SET "needs_tools": false

User Query: "{query}"
Plan: [/INST]"""

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": planning_prompt}],
        max_tokens=512,
        temperature=0.0
    )

    try:
        import json
        plan_text = response['choices'][0]['message']['content'].strip()
        start_idx = plan_text.find('{')
        end_idx = plan_text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_text = plan_text[start_idx:end_idx]
            # Debugging
            print("\n", "-"*10, "INFO", "-"*10)
            print(json_text)
            plan = json.loads(json_text) # Get dict from json
        else:
            plan = {"needs_tools": False, "steps": []}
    except Exception as e:
        print(f'ERROR: {e}')
        plan = {"needs_tools": False, "steps": []}
    
    return plan


def execute_tool_step(step: dict, previous_results: dict) -> dict:
    """
    Executes a single tool step with access to previous results.
    """
    tool_name = step.get('tool') # ex: get_historical_data
    parameters = step.get('parameters', {}) # ex: {"ticker": "GOOGL", "period": "1y"}
    
    if tool_name not in tools:
        return {"ERROR": f"Unknown tool: {tool_name}"}
    
    # Handle different tools
    if tool_name == "get_stock_info":
        company_name = next(iter(parameters.values()))
        period = parameters.get('period', '1d')
        return execute_stock_info_tool(company_name, period)
    
    elif tool_name == "get_historical_data":
        company_name = next(iter(parameters.values()))
        period = parameters.get('period', '1mo')
        return execute_historical_tool(company_name, period)

    elif tool_name == "compare_stocks":
        companies = next(iter(parameters.values()))
        period = parameters.get('period', '1mo')
        return execute_comparison_tool(companies, period)
    
    elif tool_name == "analyze_candlestick_patterns":
        company_name = next(iter(parameters.values()))
        timeframes = parameters.get('timeframes', ['15m', '1h', '4h', '1d'])
        period = parameters.get('period', '5d')
        return execute_candlestick_analysis(company_name, timeframes, period)
    
    elif tool_name == "comprehensive_analysis":
        company_name = next(iter(parameters.values()))
        return execute_comprehensive_analysis(company_name, previous_results)

    return {"ERROR": f"Tool execution not implemented for: {tool_name}"}

def execute_stock_info_tool(company: str, period: str = '1d') -> dict:
    "Get current basic stock info for a company/comapnies"
    if not company:
        return {"ERROR": "No company specified"}
    
    companies = [company] if not isinstance(company, list) else company

    results = {}
    for company in companies:
        symbol = search_yahoo_api(company)
        if symbol:
            data = get_stock_quote(symbol, period)
            if "ERROR" not in str(data):
                results[company] = data

    return results

def execute_historical_tool(company: str, period: str = '1mo') -> dict:
    """Get historical analysis for a company."""
    if not company:
        return {"ERROR": "No company specified"}
    
    companies = [company] if not isinstance(company, list) else company

    results = {}
    for company in companies:
        symbol = search_yahoo_api(company)
        if not symbol:
            return {"ERROR": f"Could not find ticker for: {company}"}
        results[company] = get_historical_analysis(symbol, period)
    
    return results
    
def execute_comparison_tool(companies: list, period: str = '1mo') -> dict:
    """Compare multiple companies."""
    if not companies:
        return {"ERROR": "No companies specified"}
    
    results = {}
    for company in companies:
        symbol = search_yahoo_api(company)
        if symbol:
            data = get_stock_quote(symbol, period)
            if "ERROR" not in str(data):
                results[company] = data
    
    return compare_stock_data(results, period)

def execute_candlestick_analysis(company: str, timeframes: list = ['15m', '1h', '4h', '1d'], period: str = '5d') -> dict:
    """Execute comprehensive candlestick pattern analysis"""
    if not company:
        return {"ERROR": "No company specified"}

    companies = [company] if not isinstance(company, list) else company
    results = {}

    for company in companies:
        symbol = search_yahoo_api(company)
        if not symbol:
            return {"ERROR": f"Could not find ticker for: {company}"}
        try:
            print(f"Agent: Analyzing candlestick patterns for {symbol}")

            multi_data = get_multi_timeframe_data(symbol=symbol, timeframes=timeframes)
            if not multi_data:
                return {"ERROR": f"No candlestick data available for {symbol}"}
            confluence = analyze_pattern_confluence(multi_data)
            # print(f"\nINFO: Risk Reward: {confluence}")
            risk_reward = calculate_risk_reward_ratio(multi_data, confluence)
            # print(f"INFO: Risk Reward: {risk_reward}\n")

            results[company] = {
                "symbol": symbol,
                "company": company,
                "timeframes_analyzed": list(multi_data.keys()),
                "patterns_detected": len(confluence['detected_patterns']),
                "confluence_analysis": confluence,
                "risk_reward": risk_reward,
                "recommendation": confluence['recommendation'],
                "confidence": confluence['confidence'],
                "signal_strength": confluence['confluence_score']
            }

        except Exception as e:
            return {"ERROR": f"Candlestick analysis failed: {e}"}
    
    return results

def execute_comprehensive_analysis(company: str, previous_results: dict) -> dict:
    """
    Execute comprehensive analysis combining all factors -- 20% sentiment / 30% fundamentals / 50% technicals framework
    """
    if not company:
        return {"ERROR": "No company specified"}
    
    try:
        print(f"Agent: Executing comprehensive analysis for {company}...")

        fundamental_data = execute_historical_tool(company, '3mo')
        technical_data = execute_candlestick_analysis(company)
        sentiment_data = get_news_sentiment(company, days_back=7)
        
        # Combine analyses with weighting
        analysis = {
            "company": company,
            "analysis_type": "comprehensive",
            "fundamental_analysis": fundamental_data,
            "technical_analysis": technical_data,
            "sentiment_analysis": sentiment_data,
            "combined_recommendation": None,
            "confidence_score": 0,
            "reasoning": []
        }
        
        # Weights: 20% sentiment, 30% fundamental, 50% technical
        technical_weight = 0.50
        fundamental_weight = 0.30
        sentiment_weight = 0.20
        
        combined_score = 0
        reasoning = []
        
        # Technical analysis contribution (50%)
        if technical_data and "confluence_analysis" in technical_data:
            tech_conf = technical_data["confluence_analysis"]
            if tech_conf["recommendation"] == "BUY":
                combined_score += technical_weight * tech_conf["confidence"]
                reasoning.append(f"Technical analysis suggests BUY with {tech_conf['confidence']:.1%} confidence")
            elif tech_conf["recommendation"] == "SELL":
                combined_score -= technical_weight * tech_conf["confidence"]
                reasoning.append(f"Technical analysis suggests SELL with {tech_conf['confidence']:.1%} confidence")
        
        # Fundamental analysis contribution (30%)
        if fundamental_data and "trend_direction" in fundamental_data:
            if fundamental_data["trend_direction"] == "upward":
                combined_score += fundamental_weight * 0.6  # Moderate fundamental confidence
                reasoning.append("Fundamental trend is upward")
            else:
                combined_score -= fundamental_weight * 0.6
                reasoning.append("Fundamental trend is downward")

        # Sentiment analysis contribution (20%)
        if sentiment_data and "sentiment_score" in sentiment_data:
            sentiment_signal = sentiment_data["sentiment_score"] * sentiment_data["confidence"]
            combined_score += sentiment_weight * sentiment_signal
        
        # Determine final recommendation
        if combined_score > 0.1:
            analysis["combined_recommendation"] = "BUY"
        elif combined_score < -0.1:
            analysis["combined_recommendation"] = "SELL"
        else:
            analysis["combined_recommendation"] = "HOLD"
        
        analysis["confidence_score"] = abs(combined_score)
        analysis["reasoning"] = reasoning

        print()
        for key, value in analysis.items():
            print(f"{key}: {value}")
        print()
        
        return analysis
        
    except Exception as e:
        return {"ERROR": f"Comprehensive analysis failed: {e}"}

def calculate_risk_reward_ratio(multi_data: dict, confluence: dict) -> dict:
    """
    Calculate risk-reward based on pattern analysis and support/resistance
    """
    daily_data = multi_data.get('1d', {}).get('ohlc')
    
    if daily_data is None or daily_data.empty:
        return {"error": "Insufficient data for risk-reward calculation"}
    
    current_price = daily_data['Close'].iloc[-1]
    
    # Calculate support/resistance using recent highs/lows
    resistance = daily_data['High'].rolling(window=min(20, len(daily_data))).max().iloc[-1]
    support = daily_data['Low'].rolling(window=min(20, len(daily_data))).min().iloc[-1]
    
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

def synthesize_response(query: str, plan: dict, results: dict) -> str:
    """
    Synthesizes final response from multiple tool results.
    """
    # Prepare context from all results
    context_parts = []
    analysis_type = "basic"

    for step_key, result in results.items():
        if isinstance(result, dict) and "ERROR" not in str(result):
            context_parts.append(f"{step_key}: {result}")

            if "confluence_analysis" in str(result):
                analysis_type = "technical"
            elif "combined_recommendation" in str(result):
                analysis_type = "comprehensive"

    
    context = "\n".join(context_parts)

    # Debugging
    # print("\n", "-"*10, "CONTEXT...", "-"*10)
    # print(context, "\n")
    
    if analysis_type == "technical":
        synthesis_prompt = f"""[INST] You are a professional trading analyst. Provide a comprehensive technical analysis report based on the candlestick pattern analysis.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Start with a clear BUY/SELL/HOLD recommendation and confidence level
- Explain the key candlestick patterns detected and their significance
- Discuss the multi-timeframe confluence
- Include specific entry/exit levels and risk-reward ratio
- Mention any risk management considerations
- Keep the tone professional but accessible

USER QUERY: "{query}"

TECHNICAL ANALYSIS REPORT: [/INST]"""

    elif analysis_type == "comprehensive":
        synthesis_prompt = f"""[INST] You are a senior investment analyst. Provide a comprehensive investment recommendation combining fundamental and technical analysis.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Lead with clear investment recommendation and confidence score
- Explain both fundamental and technical factors
- Discuss how different timeframes and analysis methods agree or disagree
- Provide specific action items and risk management
- Include reasoning for the combined recommendation
- Keep tone professional and decisive

USER QUERY: "{query}"

INVESTMENT ANALYSIS REPORT: [/INST]"""

    else:
        # Standard synthesis for basic queries
        synthesis_prompt = f"""[INST] You are a helpful financial assistant. Provide a clear, comprehensive answer based on the analysis.

ANALYSIS RESULTS:
{context}

USER QUERY: "{query}"

Provide a clear, comprehensive response: [/INST]"""
    
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": synthesis_prompt}],
        max_tokens=600,  # Increased for more detailed responses
        temperature=0.7
    )
    
    return response['choices'][0]['message']['content']