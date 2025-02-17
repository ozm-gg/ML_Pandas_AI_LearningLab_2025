import streamlit as st
import requests
import pandas as pd
import io

def data_preprocessing_ui(backend_url):
    st.sidebar.header("Настройки подготовки CSV")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type="csv")

    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(file_contents))
        text_column = st.sidebar.selectbox("Выберите столбец для очистки", options=df.columns)
    else:
        text_column = None

    preprocess_button = st.sidebar.button("Очистить CSV")

    cleaned_csv_data = None # Локальная переменная для хранения данных

    if preprocess_button:
        if uploaded_file is not None:
            files = {"file": uploaded_file}
            data = {"text_column": text_column}
            with st.spinner("Очищаем данные..."):
                try:
                    response = requests.post(f"{backend_url}/preprocess_csv/", files=files, data=data)
                    response.raise_for_status()
                    cleaned_csv_data = response.content
                    st.success("CSV файл успешно очищен!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла на бэкенд: {e}")
                    cleaned_csv_data = None
        else:
            st.error("Пожалуйста, загрузите CSV файл.")

    if cleaned_csv_data:
        st.sidebar.header("Скачать очищенный CSV")
        st.sidebar.download_button(
            label="Скачать очищенный CSV",
            data=cleaned_csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )