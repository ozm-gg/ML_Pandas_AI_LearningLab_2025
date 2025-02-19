from fastapi import FastAPI, HTTPException, Request, UploadFile, File, BackgroundTasks, Form
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from transformers import (
    pipeline,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from datasets import Dataset
import threading
import pandas as pd
import io
import time

from utilities.data_preprocessing import DataPreprocessor
from utilities.HTML_parser import TelegramChatParser

app = FastAPI()

# Блокировка для потокобезопасности модели
model_lock = threading.Lock()

# Путь к локальной модели (директория, где лежат файлы модели)
LOCAL_MODEL_PATH = "training_results/checkpoint-102"


def load_local_pipeline(model_path: str):
    """
    Загружает локальную модель и токенайзер.
    Здесь в качестве токенайзера используется базовая модель "cointegrated/rubert-tiny2".
    Если в папке с моделью есть файлы токенайзера, можно изменить параметр на model_path.
    """
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    # Если токенайзер не сохранён в папке с моделью, можно указать имя базовой модели:
    tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
    local_pipeline = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer
    )
    return local_pipeline


# Глобальная переменная для пайплайна
sentiment_pipeline = load_local_pipeline(LOCAL_MODEL_PATH)


# ======== Схемы данных (Pydantic) ========
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
        with model_lock:
            result = sentiment_pipeline(cleaned_text)[0]
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


# ======== Обновление глобального sentiment_pipeline ========
def update_sentiment_pipeline(new_model_path: str):
    global sentiment_pipeline
    with model_lock:
        sentiment_pipeline = load_local_pipeline(new_model_path)


# ======== Глобальная переменная для статуса обучения ========
training_progress = {"progress": 0, "status": "not_started"}


# ======== Тренировка модели с обновлением прогресса ========
def train_model(data: pd.DataFrame):
    global training_progress
    training_progress = {"progress": 0, "status": "in_progress"}

    # Получаем текущую модель и токенайзер
    with model_lock:
        model = sentiment_pipeline.model
        tokenizer = sentiment_pipeline.tokenizer

    # Преобразуем DataFrame в Dataset
    dataset = Dataset.from_pandas(data)

    def tokenize_function(examples):
        tokenized = tokenizer(
            [str(text) for text in examples["MessageText"]],
            padding="max_length",
            truncation=True,
            max_length=256,
        )
        label_dict = {"G": 1, "N": 0, "B": 2}
        tokenized["labels"] = [label_dict[label] for label in examples["Class"]]
        return tokenized

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    training_args = TrainingArguments(
        output_dir="./training_results",  # Общая папка для чекпоинтов
        learning_rate=3e-6,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        overwrite_output_dir=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # Запускаем реальное обучение в отдельном потоке
    training_finished = threading.Event()

    def run_training():
        trainer.train()
        training_finished.set()

    training_thread = threading.Thread(target=run_training)
    training_thread.start()

    # Параллельно обновляем training_progress (симуляция прогресса на основе времени)
    estimated_duration = 50  # Ожидаемое время обучения в секундах (примерно)
    start_time = time.time()
    while not training_finished.is_set():
        elapsed = time.time() - start_time
        progress = min(100, int((elapsed / estimated_duration) * 100))
        training_progress["progress"] = progress
        time.sleep(1)

    training_thread.join()  # Убедимся, что обучение завершилось
    training_progress["progress"] = 100
    training_progress["status"] = "completed"

    # Обновляем глобальный pipeline новой моделью из LOCAL_MODEL_PATH
    update_sentiment_pipeline(LOCAL_MODEL_PATH)


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
            predictions = sentiment_pipeline(list(cleaned_df["Message"]))

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
            predictions = sentiment_pipeline(list(cleaned_df[text_column]))

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
