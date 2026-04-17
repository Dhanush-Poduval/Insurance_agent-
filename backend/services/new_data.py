from transformers import pipeline
from dotenv import load_dotenv
import requests
import os
load_dotenv()
NEWS_API_KEY=os.getenv("NEWS_API_KEY")
classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1"
)
LABELS = ["curfew", 
          "protest",
          "riot", 
          "war",
          "pandemic", 
          "normal",
          "curfew restriction",
          "public protest",
          "riot violence",
          "war conflict",
          "pandemic lockdown",
          "normal situation"] 
def fetch_news(city):
    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={city}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
        )
        res = requests.get(url).json()
        articles = res.get("articles", [])
        headlines = [article["title"] for article in articles if article.get("title")]
        return headlines
    except Exception as e:
        print("Error fetching news API",e)
        return []

def analyze_news(city):
    news_list=fetch_news(city)
    if not news_list:
        return "normal",0.0
    news=" ".join(news_list)
    result=classifier(news,LABELS)
    event=result["labels"][0]
    confidence=result["scores"][0]
    return event,confidence

def map_to_features(event):
    return {
        "curfew": 1 if event == "curfew" else 0,
        "lockdown_level": 2 if event == "pandemic" else 0,
        "emergency_level": 1 if event in ["riot", "war", "protest"] else 0
    }

    
