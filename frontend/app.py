import streamlit as st
import os
from utilities import sentiment_analysis, data_preprocessing

st.set_page_config(
    page_title="Анализ Тональности Текста",
    page_icon=":last_quarter_moon:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* --- Основные цвета --- */
    :root {
        --primary-color: #2c3e50; /* Темно-серый, основной цвет текста и заголовков */
        --secondary-color: #27ae60; /* Красивый зеленый цвет для кнопок (измененный) */
        --accent-color: #f39c12; /* Оранжевый/Золотой, для выделения */
        --background-color: #f4f6f8; /* Светло-серый, фон приложения */
        --sidebar-color: #e6e8eb; /* Светлый серый, фон боковой панели */
        --text-color: #333333; /* Основной цвет текста */
        --light-text-color: #777777; /* Вторичный цвет текста, менее важный */
        --button-color: var(--secondary-color); /* Цвет кнопки, используем вторичный цвет (зеленый) */
        --button-text-color: white; /* Цвет текста на кнопке */
        --button-hover-color: #2ecc71; /* Более светлый зеленый цвет при наведении (измененный) */
        --button-radius: 0.5rem; /* Радиус скругления углов кнопок */
        --border-color: #d4d4d4; /* Цвет границ элементов */
    }

  
    /* --- Кнопки --- */
    .stButton > button {
        background-color: var(--button-color) !important; /* Зеленый цвет кнопки */
        color: var(--button-text-color) !important;
        font-size: 1rem !important;
        padding: 0.75rem 1.5rem !important; /* Увеличим отступы */
        border-radius: var(--button-radius) !important;
        border: none; /* Уберем стандартную рамку */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Легкая тень */
        transition: background-color 0.3s ease; /* Плавный переход цвета */
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: var(--button-hover-color) !important; /* Светло-зеленый цвет при наведении */
        color: var(--button-text-color) !important; /* Белый текст при наведении (оставили белым) */
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* Тень при наведении */
    }

    .stDownloadButton > button { /* Стили для кнопки скачивания, если есть */
        background-color: var(--accent-color) !important; /* Используем акцентный цвет для скачивания */
        color: var(--button-text-color) !important;
    }

    .stDownloadButton > button:hover {
        background-color: #e08e0b !important; /* Более темный оттенок акцентного цвета */
    }

</style>
""",  unsafe_allow_html=True)

# URL бэкенда через ngrok (или локальный URL для тестов)
BACKEND_URL = os.environ.get("BACKEND_URL") # URL по умолчанию и из переменной окружения

st.title("Анализ Тональности Текста")
st.write(
    "Определите эмоциональную окраску текста с использованием современных алгоритмов обработки естественного языка.")

st.sidebar.header("Режим работы")
app_mode = st.sidebar.radio(
    "Выберите режим:",
    ["Анализ тональности текста", "Подготовка CSV данных"]
)

if app_mode == "Подготовка CSV данных":
    data_preprocessing.data_preprocessing_ui(BACKEND_URL) # Вызываем UI функцию для data preprocessing

elif app_mode == "Анализ тональности текста":
    sentiment_analysis.sentiment_analysis_ui(BACKEND_URL) # Вызываем UI функцию для sentiment analysis