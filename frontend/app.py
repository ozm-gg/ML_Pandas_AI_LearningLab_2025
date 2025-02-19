import streamlit as st
import os
import base64
# Импортируем домашнюю страницу
from homepage import show_homepage
# Импортируем ваши модули функционала (предполагается, что они находятся в папке utilities)
from utilities import sentiment_analysis, data_preprocessing, training, chat_analysis, csv_analysis

def show_functional_page():
    st.title("Анализ тональности текстовых данных")
    st.write(
        "Добро пожаловать, выберите один из предложенных режимов и начните свою работу")

    with open("SentimentPanda.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    with st.sidebar:
        st.markdown(
            f"""
            <a href="?page=home" target="_self" style="
                display: flex; 
                align-items: center; 
                width: 100%; 
                padding: 20px 0;
                text-decoration: none;
                background-color: transparent;">
                <img src="data:image/png;base64,{encoded_string}" style="width: 50px; height: auto; margin-right: 15px;" />
                <span style="font-size: 24px; font-weight: bold; color: white;">SentimentPanda</span>
            </a>
            """,
            unsafe_allow_html=True
        )

    app_mode = st.sidebar.radio(
        "Выберите режим:",
        [
            "Анализ тональности текста",
            "Подготовка CSV данных",
            "Анализ CSV данных",
            "Обучение",
            "Анализ чатов"
        ]
    )

    if app_mode == "Подготовка CSV данных":
        cleaned_csv_data, text_column = data_preprocessing.data_preprocessing_ui(BACKEND_URL)
        if cleaned_csv_data:
            data_preprocessing.analyze_csv_data(cleaned_csv_data, text_column)
    elif app_mode == "Анализ тональности текста":
        sentiment_analysis.sentiment_analysis_ui(BACKEND_URL)
    elif app_mode == "Обучение":
        training.training(BACKEND_URL)
    elif app_mode == "Анализ чатов":
        chat_analysis.chat_analysis(BACKEND_URL)
    elif app_mode == "Анализ CSV данных":
        csv_analysis.csv_analysis(BACKEND_URL)

def main():
    st.set_page_config(
        page_title="SentimentPanda - Анализ Тональности Текста",
        page_icon="SentimentPanda.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )


    st.markdown("""  
    <style>  
        /* --- Основные цвета --- */    :root {        --primary-color: #2c3e50; /* Темно-серый, основной цвет текста и заголовков */        --secondary-color: #27ae60; /* Красивый зеленый цвет для кнопок (измененный) */        --accent-color: #f39c12; /* Оранжевый/Золотой, для выделения */        --background-color: #f4f6f8; /* Светло-серый, фон приложения */        --sidebar-color: #e6e8eb; /* Светлый серый, фон боковой панели */        --text-color: #333333; /* Основной цвет текста */        --light-text-color: #777777; /* Вторичный цвет текста, менее важный */        --button-color: var(--secondary-color); /* Цвет кнопки, используем вторичный цвет (зеленый) */        --button-text-color: white; /* Цвет текста на кнопке */        --button-hover-color: #2ecc71; /* Более светлый зеленый цвет при наведении (измененный) */        --button-radius: 0.5rem; /* Радиус скругления углов кнопок */        --border-color: #d4d4d4; /* Цвет границ элементов */    }  
        /* --- Кнопки --- */    .stButton > button {        background-color: var(--button-color) !important; /* Зеленый цвет кнопки */        color: var(--button-text-color) !important;        font-size: 1rem !important;        padding: 0.75rem 1.5rem !important; /* Увеличим отступы */        border-radius: var(--button-radius) !important;        border: none; /* Уберем стандартную рамку */        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Легкая тень */        transition: background-color 0.3s ease; /* Плавный переход цвета */        font-weight: 500;    }  
        .stButton > button:hover {        background-color: var(--button-hover-color) !important; /* Светло-зеленый цвет при наведении */        color: var(--button-text-color) !important; /* Белый текст при наведении (оставили белым) */        cursor: pointer;        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* Тень при наведении */    }  
        .stDownloadButton > button { /* Стили для кнопки скачивания, если есть */        background-color: var(--accent-color) !important; /* Используем акцентный цвет для скачивания */        color: var(--button-text-color) !important;    }  
        .stDownloadButton > button:hover {        background-color: #e08e0b !important; /* Более темный оттенок акцентного цвета */    }  
    </style>  
    """, unsafe_allow_html=True)

    global BACKEND_URL

    BACKEND_URL = os.environ.get("BACKEND_URL", "https://436b-193-239-160-82.ngrok-free.app")


    # Чтение query-параметров с использованием нового API (без круглых скобок)
    query_params = st.query_params
    page = query_params.get("page", "home")  # Если параметр "page" отсутствует, по умолчанию "home"



    # Отображаем страницу в зависимости от query-параметра "page"
    if page == "home":
        show_homepage()
    else:
        show_functional_page()

if __name__ == "__main__":
    main()