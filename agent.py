import yaml
from pathlib import Path
from llama_cpp import Llama
from financial_tools import search_yahoo_api, get_stock_quote, get_historical_analysis, compare_stock_data # find_ticker_symbol

def _load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Initialize LLM
print("Agent: Loading configuration...")
config_file = _load_config()
model_path = config_file.get('model', {}).get('path') # Modify this if deploying! (to include models dir)

print("Agent: Initializing Mistral 7B model...\n")
llm = Llama(
    model_path=model_path,
    n_gpu_layers=-1,                # Offload all layers to the GPU (my mac has 14 GPU cores)
    n_ctx=4096,                     # Set context window size
    chat_format="mistral-instruct", # Use the correct chat template for this model
    verbose=False                   # Keep the output clean
)
print("\nAgent: Model loaded successfully.")

# Define the Tools the Agent could Use
tools = {
    "get_stock_info": {
        "description": "Get current or recent stock price, volume, and trading data for a company. Can specify period like '1d', '5d', '1mo'.",
        "function": get_stock_quote
    },
    "get_historical_data": {
        "description": "Get historical stock data and trends for analysis over periods like '1mo', '3mo', '6mo', '1y'.",
        "function": get_historical_analysis
    },
    "compare_stocks": {
        "description": "Compare multiple companies' stock performance over a specified time period.",
        "function": compare_stock_data
    }
}   

# Core Agent Logic
def handle_query(query: str) -> str:
    """
    Handles a user query by following an enhanced ReAct framework with planning.
    """
    
    # Step 1: PLAN - Create execution plan
    execution_plan = create_execution_plan(query) 
    """
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
    """
    
    if not execution_plan['steps']:
        # No tools needed
        print("Agent: No specific tools needed. Answering directly.")
        return generate_direct_response(query)
      
    # Step 2: EXECUTE - Run the planned steps
    results = {}
    for i, step in enumerate(execution_plan['steps']):
        print(f"\nAgent: Executing step {i+1}: {step['action']}\nAgent: Reason: {step['reasoning']}")
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

For each step, specify:
1. The tool to use
2. The specific parameters needed
3. Why this step is necessary

Respond in this exact JSON format:
{{
    "needs_tools": true/false,
    "steps": [
        {{
            "tool": "tool_name",
            "action": "brief description",
            "parameters": {{"param1": "value1"}},
            "reasoning": "why this step is needed"
        }}
    ]
}}

If no tools are needed, set "needs_tools": false and "steps": []

User Query: "{query}"
Plan: [/INST]"""

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": planning_prompt}],
        max_tokens=400,
        temperature=0.0
    )

    # Debugging
    print("\n", "-"*10, "INFO", "-"*10)
    print(response['choices'][0]['message']['content'].strip())

    try:
        import json
        plan_text = response['choices'][0]['message']['content'].strip()
        # Extract JSON from response (in case there's extra text)
        start_idx = plan_text.find('{')
        end_idx = plan_text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_text = plan_text[start_idx:end_idx] # Gets brackets
            plan = json.loads(json_text) # Get dict from json
        else:
            plan = {"needs_tools": False, "steps": []}
    except:
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
        it = iter(parameters.values())
        company_name = next(it)
        # company_name = parameters.get('company', '')
        # period = next(it)
        period = parameters.get('period', '1d')
        return execute_stock_info_tool(company_name, period)
    
    elif tool_name == "get_historical_data":
        it = iter(parameters.values())
        company_name = next(it)
        # company_name = parameters.get('company', '')
        period = parameters.get('period', '1mo')
        return execute_historical_tool(company_name, period)
    
    elif tool_name == "compare_stocks":
        it = iter(parameters.values())
        companies = next(it)        
        # companies = parameters.get('companies', [])
        period = parameters.get('period', '1mo')
        return execute_comparison_tool(companies, period)
    
    return {"ERROR": f"Tool execution not implemented for: {tool_name}"}

def execute_stock_info_tool(company: str, period: str = '1d') -> dict:
    """Enhanced stock info with flexible periods."""
    if not company:
        return {"ERROR": "No company specified"}
    
    symbol = search_yahoo_api(company)
    if not symbol: # Both primary and secondary search fail and return None
        return {"ERROR": f"Could not find ticker for: {company}"}
    
    return get_stock_quote(symbol, period)

def execute_historical_tool(company: str, period: str = '1mo') -> dict:
    """Get historical analysis for a company."""
    if not company:
        return {"ERROR": "No company specified"}
    
    symbol = search_yahoo_api(company)
    if not symbol:
        return {"ERROR": f"Could not find ticker for: {company}"}
    
    return get_historical_analysis(symbol, period)

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

def synthesize_response(query: str, plan: dict, results: dict) -> str:
    """
    Synthesizes final response from multiple tool results.
    """
    # Prepare context from all results
    context_parts = []
    for step_key, result in results.items():
        if isinstance(result, dict) and "ERROR" not in str(result):
            context_parts.append(f"{step_key}: {result}")
    
    context = "\n".join(context_parts)
    
    synthesis_prompt = f"""[INST] You are a helpful financial assistant. Use the following data from multiple analysis steps to provide a comprehensive answer to the user's query.

Execution Plan:
{plan}

Analysis Results:
{context}

User Query: "{query}"

Provide a clear, comprehensive response that synthesizes insights from all the analysis steps: [/INST]"""
    
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": synthesis_prompt}],
        max_tokens=400,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

def generate_direct_response(query: str) -> str:
    """Generate response for queries that don't need tools."""
    fallback_prompt = f"[INST] {query} [/INST]"
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": fallback_prompt}],
        max_tokens=256
    )
    return response['choices'][0]['message']['content']