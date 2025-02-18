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


                    # Создаём прогресс-бар
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Ожидание обновлений статуса обучения с бэкенда
                    while True:
                        status_response = requests.get(f"{backend_url}/train_status/")
                        status_data = status_response.json()

                        progress = status_data["progress"]
                        status = status_data["status"]

                        # Обновляем UI
                        progress_bar.progress(progress)
                        status_text.text(f"Обучение модели: {progress}%")

                        # Если обучение завершено - выходим из цикла
                        if status == "completed":
                            st.success("✅ Обучение завершено! Модель на сайте обновилась.")
                            break

                        # Если что-то пошло не так
                        if status == "failed":
                            st.error("❌ Ошибка при обучении модели!")
                            break

                        time.sleep(1)  # Запрашиваем обновление каждую секунду

                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка при отправке файла на бэкенд: {e}")
        else:
            st.error("Пожалуйста, загрузите CSV файл.")