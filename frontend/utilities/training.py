import streamlit as st
import requests

def training(backend_url):
    st.sidebar.header("Настройки обучения")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл для обучения", type="csv")
    train_button = st.sidebar.button("Обучить модель")

    cleaned_csv_data = None 

    if train_button:
        if uploaded_file is not None:
            files = {"file": uploaded_file}
            with st.spinner("Запуск обучения..."):
                try:
                    response = requests.post(f"{backend_url}/train/", files=files)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла на бэкенд: {e}")
                    cleaned_csv_data = None
        else:
            st.error("Пожалуйста, загрузите CSV файл.")