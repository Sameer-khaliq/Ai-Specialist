import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from tools import get_weather, get_news, search_web
from tool_definitions import TOOL_DEFINITIONS

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ─────────────────────────────────────────────
# TOOL REGISTRY — name se function map karo
# ─────────────────────────────────────────────
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_news": get_news,
    "search_web": search_web
}

# ─────────────────────────────────────────────
# Gemini tools format mein convert karo
# ─────────────────────────────────────────────
def build_gemini_tools():
    function_declarations = []
    for tool in TOOL_DEFINITIONS:
        function_declarations.append(
            genai.protos.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=genai.protos.Type.STRING
                            if v["type"] == "string"
                            else genai.protos.Type.INTEGER,
                            description=v.get("description", "")
                        )
                        for k, v in tool["parameters"]["properties"].items()
                    },
                    required=tool["parameters"].get("required", [])
                )
            )
        )
    return [genai.protos.Tool(function_declarations=function_declarations)]

# ─────────────────────────────────────────────
# AGENT LOOP
# ─────────────────────────────────────────────
def run_agent(user_input: str) -> str:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=build_gemini_tools()
    )

    print(f"\n👤 User: {user_input}")
    
    # Step 1: Send to Gemini — it decides which tool to call
    response = model.generate_content(user_input)
    
    # Step 2: Check if Gemini wants to call a tool
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'function_call') and part.function_call:
            tool_name = part.function_call.name
            tool_args = dict(part.function_call.args)
            
            print(f"🔧 Tool selected: {tool_name}")
            print(f"📥 Arguments: {tool_args}")
            
            # Step 3: Execute the actual tool (real API call)
            if tool_name in TOOL_REGISTRY:
                tool_result = TOOL_REGISTRY[tool_name](**tool_args)
                print(f"📤 Tool result: {json.dumps(tool_result, indent=2)}")
                
                # Step 4: Send result back to Gemini for final response
                final_response = model.generate_content([
                    user_input,
                    {"role": "model", "parts": [part]},
                    {
                        "role": "user",
                        "parts": [{
                            "function_response": {
                                "name": tool_name,
                                "response": tool_result
                            }
                        }]
                    }
                ])
                
                return final_response.text
    
    # No tool called — direct response
    return response.text


# ─────────────────────────────────────────────
# TEST — no hardcoded routing, LLM decides
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "What's the weather like in Karachi right now?",
        "What's the latest news about artificial intelligence?",
        "Who is the founder of LangChain?",
        "Is it going to be hot in Dubai today?",   # weather again
        "Tell me recent updates about Pakistan cricket",  # news again
    ]

    for query in test_queries:
        print("\n" + "="*60)
        result = run_agent(query)
        print(f" Agent: {result}")