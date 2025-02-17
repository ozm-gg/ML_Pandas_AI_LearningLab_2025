from fastapi import FastAPI, HTTPException, Request,  UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from transformers import pipeline, TrainingArguments, Trainer
from datasets import Dataset
import threading
import pandas as pd
import io

from utilities.data_preprocessing import DataPreprocessor

app = FastAPI()

# Блокировка для потокобезопасности модели
model_lock = threading.Lock()

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="ozm-gg/ML_Pandas_AI_LearningLab_2025"
)

class TextRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    label: str
    score: float

@app.post("/analyze_sentiment/", response_model=SentimentResponse)
async def analyze_sentiment(request: Request, text_request: TextRequest):
    data_preprocessor = DataPreprocessor(text_column="MessageText")
    cleaned_text = data_preprocessor.preprocess_text(text_request.text)
    try:
        with model_lock:  # Блокировка для потокобезопасности модели
            result = sentiment_pipeline(cleaned_text)[0]
            return {"label": result["label"], "score": result["score"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preprocess_csv/")
async def preprocess_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8'))) # Читаем CSV из UploadFile

        data_preprocessor = DataPreprocessor() # Создаем экземпляр DataPreprocessor
        cleaned_df = data_preprocessor.preprocess_dataset(df.copy()) # Используем preprocess_dataset для очистки

        # Конвертируем DataFrame обратно в CSV строку
        output_stream = io.StringIO()
        cleaned_df.to_csv(output_stream, index=False)
        cleaned_csv_string = output_stream.getvalue()

        # Возвращаем CSV файл как StreamingResponse
        return StreamingResponse(
            io.StringIO(cleaned_csv_string),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=cleaned_data.csv"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")
    
def train_model(data):
    try:
        model = sentiment_pipeline.model
        tokenizer = sentiment_pipeline.tokenizer

        dataset = Dataset.from_pandas(data)
        
        def tokenize_function(examples):
            tokenized = tokenizer(
                [str(text) for text in examples["MessageText"]],
                padding="max_length",
                truncation=True,
                max_length=256,
            )

            label_dict = {
                "G" : 1,
                "N" : 0,
                "B" : 2
            }
            tokenized["labels"] = [label_dict[label] for label in examples["Class"]]
    
            return tokenized
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        training_args = TrainingArguments(
            output_dir="./training_results",
            learning_rate=3e-6,  
            num_train_epochs=3,
            per_device_train_batch_size=1,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
        )

        trainer.train()

        with model_lock:
            sentiment_pipeline.model = model

    except Exception as e:
        raise RuntimeError(f"Ошибка обучения: {str(e)}")

@app.post("/train/")
async def training(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8'))) \

        data_preprocessor = DataPreprocessor(text_column="MessageText") 
        cleaned_df = data_preprocessor.preprocess_dataset(df.copy()) 

        background_tasks.add_task(train_model, cleaned_df)
        return {"message": "Дообучение начато."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)