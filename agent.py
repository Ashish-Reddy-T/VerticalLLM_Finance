import yaml
from pathlib import Path
from llama_cpp import Llama
from financial_tools import find_ticker_symbol, get_stock_quote

def _load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Initialize LLM
print("Agent: Loading configuration...")
config_file = _load_config()
model_path = config_file.get('model', {}).get('path') # Modify this if deploying!

print("Agent: Initializing Mistral 7B model...\n")
llm = Llama(
    model_path=model_path,
    n_gpu_layers=-1,                # Offload all layers to the GPU (my mac has 14 GPU cores)
    n_ctx=2048,                     # Set context window size
    chat_format="mistral-instruct", # Use the correct chat template for this model
    verbose=False                   # Keep the output clean
)
print("\nAgent: Model loaded successfully.")

# Define the Tools the Agent could Use
tools = {
    "get_stock_info": {
        "description": "Use this tool to get the latest stock price, volume, and other daily trading data for a given company name or ticker symbol.",
        "function": get_stock_quote
    }
}

# Core Agent Logic
def handle_query(query: str) -> str:
    """
    Handles a user query by following the ReAct (Reason+Act) framework.
    """
    
    # Step 1: RE - The LLM decides which tool to use
    tool_descriptions = "\n".join([f"- {key}: {value['description']}" for key, value in tools.items()])
    # - get_stock_info: Use this tool to get the latest stock price, volume, and other daily trading data for a given company name or ticker symbol.
    
    
    selection_prompt = f"""
[INST] You are an expert financial assistant. Your task is to analyze the user's query and determine if a specialized tool is needed to answer it.

Here are the available tools:
{tool_descriptions}

Based on the user's query below, which tool should you use?
If no tool is suitable, you MUST respond with the word "none". Otherwise, respond with the exact name of the tool.

User Query: "{query}"
Selected Tool: [/INST]"""

    # Ask the LLM to make a decision
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": selection_prompt}],
        max_tokens=15,  # Small token limit as we only expect a tool name or "none"
        temperature=0.0 # Low temperature for deterministic tool selection
    )
    chosen_tool = response['choices'][0]['message']['content'].strip().lower() # 'none' or 'get_stock_info` oe other tools if included
    
    # Step 2: ACT - Execute the chosen tool
    if "get_stock_info" in chosen_tool:
        print(f"Agent: Decision made to use tool 'get_stock_info'.")
        
        # First, we need the entity (the company name) from the query.
        # For simplicity, we'll extract it by asking the LLM.
        entity_prompt = f"""[INST] From the following user query, please extract the company name or stock symbol. Respond with ONLY the name or symbol.

User Query: "{query}"
Company/Symbol: [/INST]"""
        
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": entity_prompt}],
            max_tokens=10,  # Just the company name/symbol
            temperature=0.0 # Deterministic choices required
        )
        company_name = response['choices'][0]['message']['content'].strip()
        
        if not company_name:
            return "I couldn't identify a company name in your query. Please be more specific."
            
        # Use our financial tools to get the data
        symbol = find_ticker_symbol(company_name)
        if not symbol:
            return f"I'm sorry, I couldn't find a stock symbol for '{company_name}'."
            
        stock_data = get_stock_quote(symbol)
        if "ERROR" in stock_data:
            return f"I encountered an error trying to fetch data for {symbol}: {stock_data['ERROR']}"

        # Step 3: SYNTHESIZE - Generate the final response using the tool's data
        response_prompt = f"""[INST] You are a helpful financial assistant. Use the following real-time stock data to answer the user's query. Provide a clear, concise, and natural language response.

Context:
- Company Name: {company_name}
- Ticker Symbol: {stock_data['symbol']}
- Current Price: ${stock_data['price']:.2f}
- Today's High: ${stock_data['high']:.2f}
- Today's Low: ${stock_data['low']:.2f}
- Trading Volume: {stock_data['volume']:,}

User Query: "{query}"

Answer: [/INST]"""
        
        final_response = llm.create_chat_completion(
            messages=[{"role": "user", "content": response_prompt}],
            max_tokens=256, # More tokens for a conversational answer
            temperature=0.7
        )
        return final_response['choices'][0]['message']['content']

    else:
        # Fallback: No tool was chosen - chosen_tool returned 'none'
        print("Agent: No specific tool needed. Answering directly.")
        fallback_prompt = f"[INST] {query} [/INST]"
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": fallback_prompt}],
            max_tokens=256
        )
        return response['choices'][0]['message']['content']