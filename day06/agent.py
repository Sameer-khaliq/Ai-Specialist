import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import get_weather, get_news, search_web

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_agent(user_input: str) -> str:
    print(f"\nUser: {user_input}")
    
    my_tools = [get_weather, get_news, search_web]
    
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            tools=my_tools,
            temperature=0.5,
        )
    )
    
    response = chat.send_message(user_input)
    return response.text

if __name__ == "__main__":
    test_queries = [
        "What's the weather like in Karachi right now?",
        "What's the latest news about artificial intelligence?",
        "Who is the founder of LangChain?",
        "Is it going to be hot in Dubai today?",
        "Tell me recent updates about Pakistan cricket"
    ]

    for query in test_queries:
        print("\n" + "="*60)
        result = run_agent(query)
        print(f"Agent: {result}")