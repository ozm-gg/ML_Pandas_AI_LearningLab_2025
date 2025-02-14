from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from transformers import pipeline
import threading

app = FastAPI()

# Блокировка для потокобезопасности модели
model_lock = threading.Lock()
sentiment_pipeline = None

def load_sentiment_model():
    global sentiment_pipeline  # Используем глобальную переменную
    if sentiment_pipeline is None:
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
    return sentiment_pipeline

load_sentiment_model()

class TextRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    label: str
    score: float

@app.post("/analyze_sentiment/", response_model=SentimentResponse)
async def analyze_sentiment(request: Request, text_request: TextRequest):
    try:
        with model_lock:  # Блокировка для потокобезопасности модели
            model = load_sentiment_model() # Получаем загруженную модель
            result = model(text_request.text)[0]
            return {"label": result["label"], "score": result["score"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)