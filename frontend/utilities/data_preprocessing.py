import streamlit as st
import requests
import pandas as pd
import io
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px


def data_preprocessing_ui(backend_url):
    st.sidebar.header("Настройки подготовки CSV")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type="csv")

    text_column = None  # Инициализируем переменную
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(file_contents))
        text_column = st.sidebar.selectbox("Выберите столбец для очистки", options=df.columns)

    preprocess_button = st.sidebar.button("Очистить CSV")
    cleaned_csv_data = None  # Локальная переменная для хранения очищённых данных

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

    # Всегда возвращаем кортеж, даже если данные отсутствуют
    return cleaned_csv_data, text_column


def analyze_csv_data(cleaned_csv_data, text_column):
    if not cleaned_csv_data or len(cleaned_csv_data) == 0:
        return
    try:
        # Чтение очищённого CSV-файла
        df = pd.read_csv(io.BytesIO(cleaned_csv_data))
    except Exception as e:
        st.error(f"Ошибка чтения CSV: {e}")
        return

        # Создаём две колонки в одном ряду
    col1, col2 = st.columns(2)

    with col1:
        st.header("Обзор данных")
        st.dataframe(df.head())
        st.write(f"**Всего записей:** {len(df)}")

    if text_column in df.columns:
        # Анализ текстового столбца: вычисляем длину текста
        df['text_length'] = df[text_column].astype(str).apply(len)

        with col2:
            st.subheader("Статистика по длине текстов")
            st.write(df['text_length'].describe())

        # Гистограмма длин текстов с помощью Altair
        st.subheader("Распределение длин текстов")
        hist_chart = alt.Chart(df).mark_bar(color='skyblue').encode(
            x=alt.X("text_length:Q", bin=alt.Bin(maxbins=30), title="Длина текста (символы)"),
            y=alt.Y("count()", title="Количество записей")
        ).properties(width=600, height=400)
        st.altair_chart(hist_chart)

        # Boxplot длин текстов с помощью Plotly
        st.subheader("Boxplot длин текстов")
        box_fig = px.box(df, x='text_length', title="Boxplot длин текстов",
                         labels={"text_length": "Длина текста (символы)"})
        st.plotly_chart(box_fig)
    else:
        st.error("Выбранный столбец не найден в данных.")