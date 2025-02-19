import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import io


def chat_analysis(backend_url):
    st.sidebar.header("Настройки анализа чатов")
    uploaded_file = st.sidebar.file_uploader("Загрузите HTML файл", type="html")
    analyze_button = st.sidebar.button("Анализировать чат")

    # Инициализируем df как None (будет присвоено значение, если анализ выполнится успешно)
    df = None

    if analyze_button:
        if uploaded_file is not None:
            with st.spinner("Идет анализ..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, "text/html")}
                    response = requests.post(f"{backend_url}/chat_analysis/", files=files)
                    data = response.json()

                    if isinstance(data, dict):
                        data = [data]

                    mapping = {
                        "LABEL_0": "Neutral",
                        "LABEL_1": "Positive",
                        "LABEL_2": "Negative"
                    }

                    df = pd.DataFrame(data)
                    df["label"] = df["label"].map(mapping).fillna(df["label"])
                    df['datetime'] = pd.to_datetime(
                        df['Date'] + ' ' + df['Time'],
                        format='%d.%m.%Y %H:%M'
                    )

                    st.subheader("Полученный DataFrame")
                    df_filtered = df.drop(columns=["datetime"], errors="ignore")
                    st.dataframe(df_filtered.tail())

                    st.subheader("Распределение предсказанных меток")
                    fig1 = px.histogram(df, x="label", title="Распределение меток")
                    st.plotly_chart(fig1)

                    # Дополнительные графики можно добавить здесь

                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла: {e}")
        else:
            st.error("Пожалуйста, загрузите HTML файл.")

    # Если анализ прошёл успешно и df получен, выводим кнопку для скачивания CSV
    if df is not None:
        df_filtered = df.drop(columns=["datetime"], errors="ignore")
        csv_buffer = io.StringIO()
        df_filtered.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_bytes = csv_buffer.getvalue().encode()
        st.sidebar.header("Скачать размеченный DataFrame в формате CSV")
        st.sidebar.download_button(
            label="Скачать",
            data=csv_bytes,
            file_name="labeled_chat.csv",
            mime="text/csv"
        )
