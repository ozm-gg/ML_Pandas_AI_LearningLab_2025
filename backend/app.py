from fastapi import FastAPI, HTTPException, Request, UploadFile, File, BackgroundTasks, Form
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from transformers import pipeline, TrainingArguments, Trainer
from torch.utils.data import Dataset
import torch
import threading
import pandas as pd
import io
import time

from utilities.data_preprocessing import DataPreprocessor
from utilities.HTML_parser import TelegramChatParser

app = FastAPI()

# Блокировка для потокобезопасности модели
model_lock = threading.Lock()

sentiment_pipeline = pipeline("text-classification", model="ozm-gg/ML_Pandas_AI_LearningLab_2025")
  
def classify(text):
    def f(x):
        if x < -0.01:
            return "Negative"
        elif x > 0.10:
            return "Positive"
        else:
            return "Neutral"
    res = sentiment_pipeline(text)
    return {"label" : f(res[0]['score']), "score" : res[0]['score']}

class TextRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    label: str
    score: float


# ======== Анализ тональности текста ========
@app.post("/analyze_sentiment/", response_model=SentimentResponse)
async def analyze_sentiment(request: Request, text_request: TextRequest):
    data_preprocessor = DataPreprocessor(text_column="MessageText")
    cleaned_text = data_preprocessor.preprocess_text(text_request.text)
    try:
        with model_lock:  # Блокировка для потокобезопасности модели
            result = classify(cleaned_text)
            return {"label": result["label"], "score": result["score"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======== Предобработка CSV ========
@app.post("/preprocess_csv/")
async def preprocess_csv(file: UploadFile = File(...), text_column: str = Form(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        data_preprocessor = DataPreprocessor(text_column=text_column)
        cleaned_df = data_preprocessor.preprocess_dataset(df.copy())

        output_stream = io.StringIO()
        cleaned_df.to_csv(output_stream, index=False)
        cleaned_csv_string = output_stream.getvalue()

        return StreamingResponse(
            io.StringIO(cleaned_csv_string),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=cleaned_data.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")


# ======== Тренировка модели с обновлением прогресса ========
def train_model(data):
    try:
        model = sentiment_pipeline.model
        tokenizer = sentiment_pipeline.tokenizer

        data["score"] = data["Class"].map({'N': 0, "G": 1, "B": -1})
        
        class SentimentDataset(Dataset):
            def __init__(self, texts, labels, tokenizer, max_length=512):
                self.texts = texts
                self.labels = labels
                self.tokenizer = tokenizer
                self.max_length = max_length

            def __len__(self):
                return len(self.texts)

            def __getitem__(self, idx):
                text = self.texts[idx]
                label = self.labels[idx]
                encoding = self.tokenizer(
                    text,
                    padding="max_length",
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt"
                )
                return {
                    "input_ids": encoding["input_ids"].squeeze(),
                    "attention_mask": encoding["attention_mask"].squeeze(),
                    "labels": torch.tensor(label, dtype=torch.float32)
                }
                
        train_dataset = SentimentDataset(
            texts=data["MessageText"].tolist(),
            labels=data["score"].tolist(),
            tokenizer=tokenizer
        )

        training_args = TrainingArguments(
            output_dir="./training_results",
            learning_rate=3e-6,  
            num_train_epochs=3,
            per_device_train_batch_size=3,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
        )

        trainer.train()

        with model_lock:
            sentiment_pipeline.model = model

    except Exception as e:
        raise RuntimeError(f"Ошибка обучения: {str(e)}")


# ======== Эндпоинты для обучения и статуса ========
@app.post("/train/")
async def training(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    global training_progress
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        training_progress = {"progress": 0, "status": "starting"}
        background_tasks.add_task(train_model, df)

        return {"message": "Обучение началось!"}
    except Exception as e:
        training_progress["status"] = "failed"
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/train_status/")
async def get_training_status():
    return training_progress


# ======== Анализ чатов (Telegram) ========
@app.post("/chat_analysis/")
async def chat_analysis(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = contents.decode("utf-8")
        html_content = str(result)

        parser = TelegramChatParser(html_content, is_file=False)
        df = parser.to_dataframe()

        data_preprocessor = DataPreprocessor(text_column="Message")
        cleaned_df = data_preprocessor.preprocess_dataset(df.copy())

        with model_lock:
            predictions = list(cleaned_df["Message"].map(classify))

        df["label"] = [pred.get("label") for pred in predictions]
        df["score"] = [pred.get("score") for pred in predictions]

        return df.to_dict(orient="records")
    except Exception as e:
        print("Ошибка:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ======== Анализ CSV ========
@app.post("/csv_analysis/")
async def csv_analysis(file: UploadFile = File(...), text_column: str = Form(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        data_preprocessor = DataPreprocessor(text_column=text_column)
        cleaned_df = data_preprocessor.preprocess_dataset(df.copy())

        with model_lock:
            predictions = list(cleaned_df[text_column].map(classify))

        df["label"] = [pred.get("label") for pred in predictions]
        df["score"] = [pred.get("score") for pred in predictions]
        df["clean_message"] = cleaned_df[text_column]

        return df.to_dict(orient="records")
    except Exception as e:
        print("Ошибка:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
