from transformers import pipeline
classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1"
)
LABELS = ["curfew", "protest", "riot", "war", "pandemic", "normal"] 
def analyze_news(text):
    result=classifier(text,LABELS)
    event=result["labels"][0]
    confidence=result["scores"][0]
    return event,confidence

def map_to_features(event):
    return {
        "curfew": 1 if event == "curfew" else 0,
        "lockdown_level": 2 if event == "pandemic" else 0,
        "emergency_level": 1 if event in ["riot", "war", "protest"] else 0
    }

    
