import streamlit as st
import requests
import time


def training(backend_url):
    st.sidebar.header("Настройки обучения")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл для обучения", type="csv")
    train_button = st.sidebar.button("Обучить модель")

    if train_button:
        if uploaded_file is not None:
            files = {"file": uploaded_file}
            with st.spinner("Запуск обучения..."):
                try:
                    response = requests.post(f"{backend_url}/train/", files=files)
                    response.raise_for_status()

                    # Создаем прогресс-бар и текст для отображения статуса
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Запрашиваем статус обучения каждую секунду
                    while True:
                        status_response = requests.get(f"{backend_url}/train_status/")
                        status_data = status_response.json()

                        progress = status_data.get("progress", 0)
                        status = status_data.get("status", "")

                        progress_bar.progress(progress)
                        status_text.text(f"Обучение модели: {progress}%")

                        if status == "completed":
                            st.success("✅ Обучение завершено! Модель на сайте обновилась.")
                            break
                        if status == "failed":
                            st.error("❌ Ошибка при обучении модели!")
                            break

                        time.sleep(1)

                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла на бэкенд: {e}")
        else:
            st.error("Пожалуйста, загрузите CSV файл.")


import streamlit as st
import requests
import time


def training(backend_url):
    st.sidebar.header("Настройки обучения")
    uploaded_file = st.sidebar.file_uploader("Загрузите CSV файл для обучения", type="csv")
    train_button = st.sidebar.button("Обучить модель")

    if train_button:
        if uploaded_file is not None:
            files = {"file": uploaded_file}
            with st.spinner("Запуск обучения..."):
                try:
                    response = requests.post(f"{backend_url}/train/", files=files)
                    response.raise_for_status()

                    # Создаем прогресс-бар и текст для отображения статуса
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Запрашиваем статус обучения каждую секунду
                    while True:
                        status_response = requests.get(f"{backend_url}/train_status/")
                        status_data = status_response.json()

                        progress = status_data.get("progress", 0)
                        status = status_data.get("status", "")

                        progress_bar.progress(progress)
                        status_text.text(f"Обучение модели: {progress}%")

                        if status == "completed":
                            st.success("✅ Обучение завершено! Модель на сайте обновилась.")
                            break
                        if status == "failed":
                            st.error("❌ Ошибка при обучении модели!")
                            break

                        time.sleep(1)

                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла на бэкенд: {e}")
        else:
            st.error("Пожалуйста, загрузите CSV файл.")



