import io
import pandas as pd
import streamlit as st
import requests
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def csv_analysis(backend_url):
    st.sidebar.header("Настройки анализа CSV данных")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл", type="csv")
    saved = False

    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(file_contents))
        text_column = st.sidebar.selectbox("Выберите столбец для классификации", options=df.columns)
    else:
        text_column = None

    analyze_button = st.sidebar.button("Анализировать данные")

    if analyze_button:
        if uploaded_file is not None and text_column is not None:
            with st.spinner("Идет анализ..."):
                try:
                    files = {
                        "file": (uploaded_file.name, file_contents, "text/csv")
                    }
                    data = {"text_column": text_column}

                    response = requests.post(f"{backend_url}/csv_analysis/", files=files, data=data)
                    data = response.json()

                    if isinstance(data, dict):
                        data = [data]
                    df_result = pd.DataFrame(data)

                    mapping = {
                        "LABEL_0": "Neutral",
                        "LABEL_1": "Positive",
                        "LABEL_2": "Negative"
                    }

                    df_result["label"] = df_result["label"].map(mapping).fillna(df_result["label"])

                    columns_to_display = [text_column, "label", "score"]
                    st.subheader("Полученный DataFrame")
                    st.dataframe(df_result[columns_to_display].tail())

                    df_filtered = df_result.drop(columns=["clean_message"], errors="ignore")
                    saved = True

                    st.subheader("Распределение предсказанных меток")
                    fig1 = px.histogram(df_result, x="label")
                    st.plotly_chart(fig1)

                    st.subheader("Облако слов для каждого класса")
                    text_source = "clean_message" if "clean_message" in df_result.columns else text_column

                    unique_labels = sorted(df_result["label"].unique())
                    cols = st.columns(len(unique_labels))

                    for i, label in enumerate(unique_labels):
                        text = " ".join(df_result[df_result["label"] == label][text_source].astype(str))
                        with cols[i]:
                            st.write(f"{label}")
                            if text.strip():
                                wordcloud = WordCloud(
                                    width=300,
                                    height=200,
                                    background_color='white',
                                    colormap='Greens',
                                    max_font_size=50,
                                    random_state=42
                                ).generate(text)

                                fig, ax = plt.subplots(figsize=(3, 2))
                                ax.imshow(wordcloud, interpolation="bilinear")
                                ax.axis("off")
                                st.pyplot(fig)
                            else:
                                st.write("Нет текста для построения облака слов.")

                except requests.exceptions.RequestException as e:
                    saved = False
                    st.error(f"Ошибка при отправке файла: {e}")
        else:
            st.error("Пожалуйста, загрузите CSV файл и выберите столбец.")

    if saved:
        st.sidebar.header("Скачать размеченный CSV")
        st.sidebar.download_button(
            label="Скачать размеченный CSV",
            data=df_filtered.to_csv(index=False).encode("utf-8"),
            file_name="analysis_data.csv",
            mime="text/csv"
        )