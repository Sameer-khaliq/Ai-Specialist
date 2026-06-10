# Yeh JSON schema Gemini ko batata hai:
# 1. Kaunse tools available hain
# 2. Kab use karein (description)
# 3. Kya parameters chahiye

TOOL_DEFINITIONS = [
    {
        "name": "get_weather",
        "description": "Get current weather for any city. Use when user asks about weather, temperature, climate, rain, or conditions in a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name e.g. Lahore, Dubai, London"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_news",
        "description": "Get latest news articles about any topic. Use when user asks about news, recent events, updates, or what's happening with a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic to search news for e.g. AI, Pakistan, cricket"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of articles to return, default 3",
                    "default": 3
                }
            },
            "required": ["topic"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the web for any information, facts, or general queries. Use when user asks general questions not covered by weather or news.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string"
                }
            },
            "required": ["query"]
        }
    }
]