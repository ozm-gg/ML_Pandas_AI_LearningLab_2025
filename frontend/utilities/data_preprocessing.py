import streamlit as st
import requests

def data_preprocessing_ui(backend_url):
    st.sidebar.header("Настройки очистки CSV")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type="csv")
    preprocess_button = st.sidebar.button("Очистить CSV")

    cleaned_csv_data = None # Локальная переменная для хранения данных

    if preprocess_button:
        if uploaded_file is not None:
            files = {"file": uploaded_file}
            with st.spinner("Очищаем данные..."):
                try:
                    response = requests.post(f"{backend_url}/preprocess_csv/", files=files)
                    response.raise_for_status()
                    cleaned_csv_data = response.content
                    st.success("CSV файл успешно очищен!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла на бэкенд: {e}")
                    cleaned_csv_data = None
        else:
            st.error("Пожалуйста, загрузите CSV файл.")

    if cleaned_csv_data:
        st.sidebar.markdown("---")
        st.sidebar.header("Скачать очищенный CSV")
        st.sidebar.download_button(
            label="Скачать очищенный CSV",
            data=cleaned_csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )