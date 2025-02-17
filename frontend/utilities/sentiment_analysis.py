import streamlit as st
import plotly.express as px
import pandas as pd
import requests

def sentiment_analysis_ui(backend_url):
    st.sidebar.header("Настройки анализа тональности")
    input_text = st.sidebar.text_area(
        "Введите текст для анализа:",
        "Отличная погода!"
    )

    analyze_button = st.sidebar.button("Анализировать текст")

    st.sidebar.markdown("---")
    st.sidebar.header("Демо-анализ")
    demo_button = st.sidebar.button("Анализировать демо-тексты")

    def analyze_text_from_backend(text):
        api_url = f"{backend_url}/analyze_sentiment/" # Уточненный URL
        try:
            response = requests.post(api_url, json={"text": text})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка при запросе к бэкенду: {e}")
            return None

    if analyze_button:
        if not input_text.strip():
            st.error("Пожалуйста, введите текст для анализа.")
        else:
            with st.spinner("Анализируем текст..."):
                result = analyze_text_from_backend(input_text)
                if result:
                    mapping = {
                        "LABEL_0": "Neutral",
                        "LABEL_1": "Positive",
                        "LABEL_2": "Negative"
                    }
                    sentiment = mapping.get(result["label"], result["label"])
                    score = result["score"]

                    st.markdown("### Результат анализа")
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write("**Тональность:**", sentiment)
                        st.write("**Уверенность:**", f"{score * 100:.2f}%")
                    with col2:
                        st.progress(int(score * 100))
                    st.markdown("#### Исходный текст")
                    st.info(input_text)

    if demo_button:
        sample_texts = [
            "Грустно!",
            "Так весело что плакать хочется(",
            "Продукт оправдывает ожидания.",
            "Скучная книга.",
            "Эта новость вызывает негативные эмоции."
        ]

        demo_results = []
        with st.spinner("Обрабатываем демо-тексты..."):
            for text in sample_texts:
                result = analyze_text_from_backend(text)
                if result:
                    demo_results.append({"text": text, **result})

        if demo_results:
            df_demo = pd.DataFrame(demo_results)

            mapping = {
                "LABEL_0": "Neutral",
                "LABEL_1": "Positive",
                "LABEL_2": "Negative"
            }
            df_demo["label"] = df_demo["label"].map(mapping).fillna(df_demo["label"])

            st.markdown("### Анализ демо-текстов")
            st.dataframe(df_demo)

            sentiment_counts = df_demo["label"].value_counts().reset_index()
            sentiment_counts.columns = ["label", "count"]

            fig = px.bar(
                sentiment_counts,
                x="label",
                y="count",
                color="label",
                title="Распределение тональностей",
                labels={"label": "Тональность", "count": "Количество"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Не удалось получить результаты демо-анализа от бэкенда.")