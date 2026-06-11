import requests
import os
from dotenv import load_dotenv

load_dotenv()

#TOOL 1: WEATHER

def get_weather(city: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": os.getenv("WEATHER_API_KEY"),
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        return {"error": f"Weather not found for {city}"}

    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "condition": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }


# TOOL 2: NEWS

def get_news(topic: str, count: int = 2) -> dict:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "apiKey": os.getenv("NEWS_API_KEY"),
        "pageSize": count,
        "sortBy": "publishedAt",
        "language": "en"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        return {"error": f"News not found for {topic}"}

    articles = []
    for a in data["articles"][:count]:
        articles.append({
            "title": a["title"],
            "source": a["source"]["name"],
            "published": a["publishedAt"][:10],
            "url": a["url"]
        })

    return {"topic": topic, "articles": articles}


# TOOL 3: SEARCH

def search_web(query: str) -> dict:
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": os.getenv("SERP_API_KEY"),
        "num": 3
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for r in data.get("organic_results", [])[:3]:
        results.append({
            "title": r.get("title"),
            "snippet": r.get("snippet"),
            "link": r.get("link")
        })

    return {"query": query, "results": results}


# Test each tool independently
if __name__ == "__main__":
    import json
    print(" Weather:", json.dumps(get_weather("Lahore"), indent=2))
    print(" News:", json.dumps(get_news("artificial intelligence"), indent=2))
    print(" Search:", json.dumps(search_web("LangChain tutorial 2024"), indent=2))