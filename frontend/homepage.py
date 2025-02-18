import streamlit as st

def show_homepage():
    import streamlit as st

    st.markdown("<h1 style='text-align: center;'>Добро пожаловать в SentimentPanda!</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <h5 style='text-align: center;'>
        SentimentPanda – это универсальная платформа для обработки и анализа текстовых данных.  
         </h5> 
         
         
         
        """, unsafe_allow_html=True
    )
    st.markdown('\n\n')

    col1, col2, col3 = st.columns([1, 2, 1])  # Центральная колонка в 2 раза шире
    with col2:
        if st.button("Перейти к анализу", key="center_button", use_container_width=True):
            st.query_params.from_dict({"page": "app"})

    st.markdown("\n---")
    # Первый ряд: две колонки
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            ### 1. Анализ тональности текста  
            Определить эмоциональную окраску текста с использованием современных алгоритмов обработки естественного языка.
            """
        )
        video_file = open("static/SenAn1.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, muted =True)
    with col2:
        st.markdown(
            """
            ### 2. Подготовка CSV данных  
            Очистить и предварительно обработать CSV‑файлы, чтобы подготовить их для дальнейшего анализа и обучения моделей.
            """
        )
        video_file = open("static/cvc02.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, muted=True)

    # Второй ряд: две колонки
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('\n\n')
        st.markdown(
            """
            ### 3. Анализ CSV данных  
            
            Провести детальный анализ загруженных CSV данных, получить сводную информацию и визуализировать распределение различных параметров.
            """
        )
        video_file = open("static/cvcPrepare03.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, muted=True)

    with col4:
        st.markdown('\n\n')
        st.markdown(
            """
            ### 4. Обучение  
            Дообучить модель на основе ваших данных для более точного анализа тональности текста.
            """
        )
        st.write("")
        st.write("")
        st.write("")
        st.image("static/Training05.png")

    # Третий ряд: две колонки (одна для описания, другая для GIF-демонстрации)
    col5, col6 = st.columns(2)
    with col5:
        st.markdown(
            """
            ### 5. Анализ чатов  
            Проанализировать переписки из Telegram для выявления тональности и эмоциональной окраски сообщений.
            """
        )
        video_file = open("static/chat05.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, muted=True)

    with col6:
        st.write("")
        st.write("")
        st.write("")
        st.write("")


        st.markdown("###### Как скачать чат из telegram в формате HTML для анализа активности?")
        video_file = open("static/tgHTML.mp4", "rb")
        video_bytes = video_file.read()
        st.video(video_bytes, muted=True)




