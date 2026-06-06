# cost_calculator.py

def calculate_cost(input_tokens, output_tokens, model="gemini-flash"):
    pricing = {
        "gemini-flash": {"input": 1.25, "output": 5.00},
        "gpt-4o":       {"input": 2.50,  "output": 10.00},
        "claude-sonnet":{"input": 3.00,  "output": 15.00}
    }
    
    rates = pricing[model]
    input_cost  = (input_tokens  / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    total = input_cost + output_cost
    
    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total, 6)
    }

# Real world example
# Client ka chatbot — 1000 conversations/day
# Each conversation: 500 input tokens, 200 output tokens

daily_conversations = 1000
input_t  = 500
output_t = 500

result = calculate_cost(
    input_tokens  = daily_conversations * input_t,
    output_tokens = daily_conversations * output_t,
    model="gemini-flash"
)

print(f"Model: {result['model']}")
print(f"Daily cost: ${result['total_cost_usd']}")
print(f"Monthly cost: ${round(result['total_cost_usd'] * 30, 4)}")

# Same calculation for GPT-4o
result_gpt = calculate_cost(
    input_tokens  = daily_conversations * input_t,
    output_tokens = daily_conversations * output_t,
    model="gpt-4o"
)
print(f"\nGPT-4o daily cost: ${result_gpt['total_cost_usd']}")
print(f"GPT-4o monthly cost: ${round(result_gpt['total_cost_usd'] * 30, 4)}")


result_claude = calculate_cost(
    input_tokens  = daily_conversations * input_t,
    output_tokens = daily_conversations * output_t,
    model="claude-sonnet"
)
print(f"\nClaude-Sonnet daily cost: ${result_claude['total_cost_usd']}")
print(f"Claude-Sonnet monthly cost: ${round(result_claude['total_cost_usd'] * 30, 4)}")