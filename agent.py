from llama_cpp import Llama

from utils import get_keys
from financial_tools import search_yahoo_api, get_stock_quote
from technical_analysis import TechnicalAnalyzer
from fundamental_analysis import FundamentalAnalyzer
from sentiment_analysis import SentimentAnalyzer
from self_rag import SelfRAG

# Initialize LLM
print("Agent: Loading configuration...")
print("Agent: Initializing Mistral 7B model...\n")

model_path = get_keys("PATH")
llm = Llama(
    model_path=model_path,
    n_gpu_layers=-1,
    n_ctx=8192,
    chat_format="mistral-instruct",
    verbose=False
)
print("\nAgent: Model loaded successfully.")

print("Agent: Initializing Technical Analysis system...")
technical_analyzer = TechnicalAnalyzer()

print("Agent: Initializing Fundamental Analysis system...")
fundamental_analyzer = FundamentalAnalyzer()

print("Agent: Initializing Sentiment Analysis system...")
sentiment_analyzer = SentimentAnalyzer()

print("Agent: Initializing Self-RAG system...")
self_rag = SelfRAG(llm)

# Enhanced Tools with comprehensive analysis systems
tools = {
    "get_stock_info": {
        "description": "Get current or recent stock price, volume, and trading data for a company. Can specify period like '1d', '5d', '1mo'.",
        "function": "get_stock_quote"
    },
    "comprehensive_technical_analysis": {
        "description": "Complete technical analysis with trend, momentum, volume, volatility indicators and candlestick patterns across multiple timeframes.",
        "function": "execute_comprehensive_technical_analysis"
    },
    "comprehensive_fundamental_analysis": {
        "description": "Complete fundamental analysis including valuation ratios, profitability metrics, growth analysis, financial health, and dividend analysis.",
        "function": "execute_comprehensive_fundamental_analysis"
    },
    "comprehensive_sentiment_analysis": {
        "description": "Multi-source sentiment analysis including news, analyst ratings, social media, insider trading, and options flow.",
        "function": "execute_comprehensive_sentiment_analysis"
    },
    "comprehensive_analysis": {
        "description": "Complete analysis combining enhanced technical (50%), fundamental (30%), and sentiment (20%) analysis for investment decisions.",
        "function": "execute_comprehensive_analysis"
    }
}

# Core Agent Logic (Enhanced ReAct framework)
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
- If query mentions "technical analysis", "indicators", "MACD", "RSI", "patterns", "signals" → use comprehensive_technical_analysis
- If query mentions "fundamentals", "P/E ratio", "earnings", "financial health", "valuation" → use comprehensive_fundamental_analysis
- If query mentions "sentiment", "news", "analyst ratings", "social media", "insider trading" → use comprehensive_sentiment_analysis
- If query asks for "complete analysis", "recommendation", "should I buy/sell" → use comprehensive_analysis  
- If query asks for basic info only → use get_stock_info
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

User Query: "{query}"
Plan: [/INST]"""

    print("\n🤖 Agent: Generating ...")
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
            print("\n", "-"*10, "EXECUTION PLAN", "-"*10)
            print(json_text)
            plan = json.loads(json_text)
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
    tool_name = step.get('tool')
    parameters = step.get('parameters', {})
    
    if tool_name not in tools:
        return {"ERROR": f"Unknown tool: {tool_name}"}
    
    # Handle different tools
    if tool_name == "get_stock_info":
        company_name = next(iter(parameters.values()))
        period = parameters.get('period', '1d')
        return execute_stock_info_tool(company_name, period)
    
    elif tool_name == "comprehensive_technical_analysis":
        company_name = next(iter(parameters.values()))
        timeframes = parameters.get('timeframes', ['15m', '1h', '4h', '1d'])
        return execute_comprehensive_technical_analysis(company_name, timeframes)
    
    elif tool_name == "comprehensive_fundamental_analysis":
        company_name = next(iter(parameters.values()))
        return execute_comprehensive_fundamental_analysis(company_name)
    
    elif tool_name == "comprehensive_sentiment_analysis":
        company_name = next(iter(parameters.values()))
        days_back = parameters.get('days_back', 7)
        return execute_comprehensive_sentiment_analysis(company_name, days_back)
    
    elif tool_name == "comprehensive_analysis":
        company_name = next(iter(parameters.values()))
        return execute_comprehensive_analysis(company_name, previous_results)

    return {"ERROR": f"Tool execution not implemented for: {tool_name}"}

def execute_stock_info_tool(company: str, period: str = '1d') -> dict:
    """Get current basic stock info for a company/companies"""
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

def execute_comprehensive_fundamental_analysis(company: str) -> dict:
    """Execute comprehensive fundamental analysis using the new FundamentalAnalyzer"""
    if not company:
        return {"ERROR": "No company specified"}

    companies = [company] if not isinstance(company, list) else company
    results = {}

    for company in companies:
        symbol = search_yahoo_api(company)
        if not symbol:
            return {"ERROR": f"Could not find ticker for: {company}"}
        
        try:            
            # Use FundamentalAnalyzer
            analysis_result = fundamental_analyzer.analyze_comprehensive_fundamentals(symbol)
            
            if "ERROR" in str(analysis_result):
                return analysis_result
            
            results[company] = {
                **analysis_result,
                "company": company,
                "analysis_type": "comprehensive_fundamental"
            }

        except Exception as e:
            return {"ERROR": f"Comprehensive fundamental analysis failed: {e}"}
    
    return results

def execute_comprehensive_sentiment_analysis(company: str, days_back: int = 7) -> dict:
    """Execute comprehensive sentiment analysis using the new SentimentAnalyzer"""
    if not company:
        return {"ERROR": "No company specified"}

    companies = [company] if not isinstance(company, list) else company
    results = {}

    for company in companies:
        symbol = search_yahoo_api(company)
        if not symbol:
            return {"ERROR": f"Could not find ticker for: {company}"}
        
        try:
            # Use SentimentAnalyzer
            analysis_result = sentiment_analyzer.analyze_comprehensive_sentiment(symbol, company, days_back)
            
            if "ERROR" in str(analysis_result):
                return analysis_result
            
            results[company] = {
                **analysis_result,
                "company": company,
                "analysis_type": "comprehensive_sentiment"
            }

        except Exception as e:
            return {"ERROR": f"Comprehensive sentiment analysis failed: {e}"}
    
    return results

def execute_comprehensive_technical_analysis(company: str, timeframes: list = ['15m', '1h', '4h', '1d']) -> dict:
    """Execute comprehensive technical analysis using the new TechnicalAnalyzer"""
    if not company:
        return {"ERROR": "No company specified"}

    companies = [company] if not isinstance(company, list) else company
    results = {}

    for company in companies:
        symbol = search_yahoo_api(company)
        if not symbol:
            return {"ERROR": f"Could not find ticker for: {company}"}
        
        try:            
            # Use TechnicalAnalyzer
            analysis_result = technical_analyzer.analyze_comprehensive_technicals(symbol, timeframes)
            
            if "ERROR" in str(analysis_result):
                return analysis_result
            
            results[company] = {
                **analysis_result,
                "company": company,
                "analysis_type": "comprehensive_technical"
            }

        except Exception as e:
            return {"ERROR": f"Comprehensive technical analysis failed: {e}"}
    
    return results

def execute_comprehensive_analysis(company: str, previous_results: dict) -> dict:
    """
    Execute comprehensive analysis combining all factors:
    - Enhanced Technical Analysis (50%): All indicators + candlestick patterns
    - Enhanced Fundamental Analysis (30%): Valuation, profitability, growth, health metrics
    - Enhanced Sentiment Analysis (20%): Multi-source sentiment including news, analysts, social media
    """
    if not company:
        return {"ERROR": "No company specified"}
    
    try:
        print(f"Agent: Executing comprehensive enhanced analysis for {company}...")

        # Get enhanced technical analysis
        technical_data = execute_comprehensive_technical_analysis(company)
        
        # Get enhanced fundamental analysis
        fundamental_data = execute_comprehensive_fundamental_analysis(company)
        
        # Get enhanced sentiment analysis
        sentiment_data = execute_comprehensive_sentiment_analysis(company, 7)
        
        # Combine analyses with weighting
        analysis = {
            "company": company,
            "analysis_type": "comprehensive_enhanced_v2",
            "technical_analysis": technical_data,
            "fundamental_analysis": fundamental_data,
            "sentiment_analysis": sentiment_data,
            "combined_recommendation": None,
            "confidence_score": 0,
            "reasoning": [],
            "analysis_breakdown": {
                "technical_weight": 0.50,
                "fundamental_weight": 0.30,
                "sentiment_weight": 0.20
            }
        }
        
        # Enhanced weights
        technical_weight = 0.50
        fundamental_weight = 0.30
        sentiment_weight = 0.20
        
        combined_score = 0
        reasoning = []
        
        # Enhanced Technical analysis contribution (50%)
        tech_score = 0
        if (technical_data and company in technical_data and 
            "confluence_analysis" in technical_data[company]):
            
            tech_conf = technical_data[company]["confluence_analysis"]
            tech_recommendation = tech_conf["recommendation"]
            tech_confidence = tech_conf["confidence"]
            
            if tech_recommendation == "BUY":
                tech_score = technical_weight * tech_confidence
                combined_score += tech_score
                reasoning.append(f"Technical: BUY signal with {tech_confidence:.1%} confidence across {len(tech_conf.get('detected_signals', []))} indicators")
            elif tech_recommendation == "SELL":
                tech_score = -technical_weight * tech_confidence
                combined_score += tech_score
                reasoning.append(f"Technical: SELL signal with {tech_confidence:.1%} confidence across {len(tech_conf.get('detected_signals', []))} indicators")
            else:
                reasoning.append("Technical: HOLD - signals below confidence threshold")
        
        # Enhanced Fundamental analysis contribution (30%)
        fund_score = 0
        if (fundamental_data and company in fundamental_data and 
            "fundamental_analysis" in fundamental_data[company]):
            
            fund_analysis = fundamental_data[company]["fundamental_analysis"]
            fund_recommendation = fund_analysis["recommendation"]
            fund_confidence = fund_analysis["confidence"]
            
            # Convert fundamental recommendation to score
            fund_signal_map = {
                'BUY': 1.0, 'WEAK_BUY': 0.5, 'NEUTRAL': 0.0, 
                'WEAK_SELL': -0.5, 'SELL': -1.0
            }
            fund_signal = fund_signal_map.get(fund_recommendation, 0.0)
            fund_score = fundamental_weight * fund_signal * fund_confidence
            combined_score += fund_score
            
            reasoning.append(f"Fundamental: {fund_recommendation} with {fund_confidence:.1%} confidence across {fund_analysis.get('metrics_analyzed', 0)} metrics")

        # Enhanced Sentiment analysis contribution (20%)
        sent_score = 0
        if (sentiment_data and company in sentiment_data and 
            "overall_sentiment" in sentiment_data[company]):
            
            sent_analysis = sentiment_data[company]["overall_sentiment"]
            sent_score_raw = sent_analysis["weighted_score"]
            sent_confidence = sent_analysis["confidence"]
            
            sent_score = sentiment_weight * sent_score_raw * sent_confidence
            combined_score += sent_score
            
            reasoning.append(f"Sentiment: {sent_analysis['recommendation']} with {sent_confidence:.1%} confidence from {sent_analysis.get('sources_analyzed', 0)} sources")
        
        # Determine final recommendation with enhanced thresholds
        if combined_score > 0.20:
            analysis["combined_recommendation"] = "STRONG_BUY"
        elif combined_score > 0.10:
            analysis["combined_recommendation"] = "BUY"
        elif combined_score > 0.05:
            analysis["combined_recommendation"] = "WEAK_BUY"
        elif combined_score > -0.05:
            analysis["combined_recommendation"] = "HOLD"
        elif combined_score > -0.10:
            analysis["combined_recommendation"] = "WEAK_SELL"
        elif combined_score > -0.20:
            analysis["combined_recommendation"] = "SELL"
        else:
            analysis["combined_recommendation"] = "STRONG_SELL"
        
        analysis["confidence_score"] = abs(combined_score)
        analysis["reasoning"] = reasoning
        
        # Enhanced score breakdown
        analysis["score_breakdown"] = {
            "technical_contribution": tech_score,
            "fundamental_contribution": fund_score,
            "sentiment_contribution": sent_score,
            "total_score": combined_score,
            "score_components": {
                "technical_pct": (tech_score / combined_score * 100) if combined_score != 0 else 0,
                "fundamental_pct": (fund_score / combined_score * 100) if combined_score != 0 else 0,
                "sentiment_pct": (sent_score / combined_score * 100) if combined_score != 0 else 0
            }
        }

        print(f"\nEnhanced Analysis Summary for {company}:")
        print(f"Final Recommendation: {analysis['combined_recommendation']}")
        print(f"Overall Confidence: {analysis['confidence_score']:.3f}")
        print(f"Technical Contribution: {tech_score:.3f}")
        print(f"Fundamental Contribution: {fund_score:.3f}")
        print(f"Sentiment Contribution: {sent_score:.3f}")
        print(f"Total Score: {combined_score:.3f}")
        print()
        
        return analysis
        
    except Exception as e:
        return {"ERROR": f"Comprehensive enhanced analysis failed: {e}"}

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

            if "comprehensive_technical" in str(result):
                analysis_type = "comprehensive_technical"
            elif "confluence_analysis" in str(result):
                analysis_type = "technical"
            elif "combined_recommendation" in str(result):
                analysis_type = "comprehensive"

    context = "\n".join(context_parts)
    
    if analysis_type == "comprehensive_technical":
        synthesis_prompt = f"""[INST] You are a professional trading analyst. Provide a comprehensive technical analysis report based on the multi-indicator analysis.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Start with a clear BUY/SELL/HOLD recommendation and confidence level
- Explain the key technical indicators across different categories (trend, momentum, volume, volatility)
- Discuss the multi-timeframe confluence and signal strength
- Include specific entry/exit levels and risk-reward ratio if available
- Mention any risk management considerations
- Highlight the strongest signals and any conflicting indicators
- Keep the tone professional but accessible

USER QUERY: "{query}"

COMPREHENSIVE TECHNICAL ANALYSIS REPORT: [/INST]"""

    elif analysis_type == "technical":
        synthesis_prompt = f"""[INST] You are a professional trading analyst. Provide a comprehensive technical analysis report.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Start with a clear BUY/SELL/HOLD recommendation and confidence level
- Explain the key technical patterns and indicators detected
- Discuss the multi-timeframe confluence
- Include specific entry/exit levels and risk-reward ratio
- Mention any risk management considerations
- Keep the tone professional but accessible

USER QUERY: "{query}"

TECHNICAL ANALYSIS REPORT: [/INST]"""

    elif "fundamental" in str(results).lower():
        synthesis_prompt = f"""[INST] You are a fundamental analyst. Provide a comprehensive fundamental analysis report.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Start with a clear investment recommendation and confidence level
- Explain the key fundamental metrics across valuation, profitability, growth, and financial health
- Discuss strengths and weaknesses in the company's fundamentals
- Compare metrics to industry standards where relevant
- Provide long-term investment perspective
- Keep tone professional and informative

USER QUERY: "{query}"

FUNDAMENTAL ANALYSIS REPORT: [/INST]"""

    elif "sentiment" in str(results).lower():
        synthesis_prompt = f"""[INST] You are a market sentiment analyst. Provide a comprehensive sentiment analysis report.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Start with a clear sentiment recommendation (POSITIVE/NEGATIVE/NEUTRAL)
- Explain the different sentiment sources analyzed (news, analysts, social media, etc.)
- Discuss the reliability and volume of each source
- Highlight any conflicting sentiment signals
- Provide short-term market perspective based on sentiment
- Keep tone professional but accessible

USER QUERY: "{query}"

SENTIMENT ANALYSIS REPORT: [/INST]"""

    elif analysis_type == "comprehensive":
        synthesis_prompt = f"""[INST] You are a senior investment analyst. Provide a comprehensive investment recommendation combining enhanced technical, fundamental and sentiment analysis.

ANALYSIS RESULTS:
{context}

INSTRUCTIONS:
- Lead with clear investment recommendation (STRONG_BUY/BUY/WEAK_BUY/HOLD/WEAK_SELL/SELL/STRONG_SELL) and confidence score
- Explain how the enhanced technical analysis (50% weight) contributes with multiple indicator categories
- Discuss comprehensive fundamental factors (30% weight) including valuation, profitability, growth metrics
- Explain multi-source sentiment analysis (20% weight) from news, analysts, social media, insider trading
- Explain how different analysis methods agree or disagree
- Provide specific action items and risk management based on the combined analysis
- Include reasoning for the combined recommendation and score breakdown
- Highlight the contribution percentage of each analysis type
- Keep tone professional and decisive

USER QUERY: "{query}"

ENHANCED INVESTMENT ANALYSIS REPORT: [/INST]"""

    else:
        # Standard synthesis for basic queries
        synthesis_prompt = f"""[INST] You are a helpful financial assistant. Provide a clear, comprehensive answer based on the analysis.

ANALYSIS RESULTS:
{context}

USER QUERY: "{query}"

Provide a clear, comprehensive response: [/INST]"""
    
    print("\n🤖 Agent: Generating ...")
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": synthesis_prompt}],
        max_tokens=800,  # Increased for more detailed responses
        temperature=0.7
    )
    
    return response['choices'][0]['message']['content']