import streamlit as st

def show_homepage():
    import streamlit as st

    st.markdown("""
    <h1 style='text-align: center; margin-bottom: 5px;'>
        🐼 SentimentPanda: Твой детектив эмоций в текстах
    </h1>
    """, unsafe_allow_html=True)
    
    st.markdown(
        """
        <h4 style='text-align: center;'>
        Универсальная платформа для обработки и анализа текстовых данных 
         </h4> 
        """, unsafe_allow_html=True
    )
    st.markdown('\n\n')

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("""
        <style>
            .stButton>button {
                background: linear-gradient(45deg, #4CAF50, #8BC34A);
                color: white;
                border: none;
                padding: 20px 45px;
                border-radius: 25px;
                font-size: 1.4rem;
                height: 70px;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(76,175,80,0.4);
            }
            .stButton>button:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(76,175,80,0.6);
            }
        </style>
        """, unsafe_allow_html=True)

        if st.button("🚀 Начать анализ прямо сейчас!", use_container_width=True):
            st.query_params.from_dict({"page": "app"})

    st.markdown("\n---")

    # Блок возможностей с иконками
    st.markdown("""
    <div style='margin: 40px 0;'>
        <h2 style='text-align: center; color: white; margin-bottom: 30px;'>🔍 Что умеет наш анализатор</h2>""", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        .feature-card {
            padding: 1.5rem;
            border-radius: 15px;
            background-color: var(--secondary-background-color);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            min-height: 200px;
            margin: 10px;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            background-color: var(--secondary-background-color);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        .feature-title {
            color: var(--primary-text-color);
            margin-bottom: 0.8rem;
            font-weight: 600;
            font-size: 1.2rem;
        }
        .feature-description {
            color: var(--primary-text-color);
            font-size: 1rem;
            line-height: 1.4;
            opacity: 0.9;
        }
    </style>
    """, unsafe_allow_html=True)

    # Первый ряд
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3 class="feature-title">Анализ текста</h3>
            <p class="feature-description">
                Классификация вашего текста по трем классам 
                POSITIVE/NEUTRAL/NEGATIVE с точностью от 90%
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧹</div>
            <h3 class="feature-title">Подготовка данных</h3>
            <p class="feature-description">
                Автоматическая обработка CSV: очистка от стоп-слов, леммантизация, 
                удаление имен, чисел и спецсимволов
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">Анализ CSV данных</h3>
            <p class="feature-description">
                Разметьте весь ваш набор данных с визуализацией 
                результатов в виде графиков и облаков слов
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Второй ряд
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">Кастомизация модели</h3>
            <p class="feature-description">
                Персональное дообучение нейросети 
                на ваших данных за 5 кликов
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3 class="feature-title">Анализ чатов</h3>
            <p class="feature-description">
                Визуализация эмоциональной динамики 
                в Telegram-диалогах
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("\n---")

    st.markdown("""
    <div style='margin: 40px 0;'>
        <h2 style='text-align: center; color: white; margin-bottom: 30px;'>🛠️ Как работать с платформой</h2>""", unsafe_allow_html=True)
    

    custom_expander_style = """
    <style>
        .stExpander {
            border: 2px solid #e0e0e0 !important;
            border-radius: 15px !important;
            margin: 15px 0 !important;
            background: var(--secondary-background-color) !important;
        }
        .stExpander summary {
            padding: 1.2rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
        .stExpander summary:hover {
            background-color: rgba(76,175,80,0.1) !important;
        }
        .stExpander summary:after {
            color: var(--primary-color) !important;
        }
    </style>
    """
    st.markdown(custom_expander_style, unsafe_allow_html=True)

    st.markdown("""
    <style>
        video {
            max-width: 1000px;
            border-radius: 10px;
        }                
    </style>
    """, unsafe_allow_html=True)
    
    with st.expander("📊 Анализ текста", expanded=False):
        st.markdown("""
        **Шаги:**
        1. Введите текст в поле ввода
        2. Нажмите "Анализировать"
        3. Ознакомтесь с результатами в правой части экрана
        """)
        st.video("static/analisys_text.mp4", muted=True)

    with st.expander("🧹 Подготовка данных", expanded=False):
        st.markdown("""
        **Шаги:**
        1. Загрузите CSV-файл
        2. Выберите столбец с текстовыми данными
        3. Нажмите "Очистить CSV"
        4. Ознакомтесь с результатами и скачайте итоговый файл
        """)
        st.video("static/clean_csv.mp4", muted=True)

    with st.expander("🔍 Анализ CSV данных", expanded=False):
        st.markdown("""
        **Шаги:**
        1. Загрузите CSV-файл
        2. Выберите столбец для классификации
        3. Нажмите "Анализировать данные"
        4. Ознакомтесь с результатами и скачайте размеченный файл
        """)
        st.video("static/analisys_csv.mp4", muted=True)

    with st.expander("🤖 Кастомизация модели", expanded=False):
        st.markdown("""
        **Шаги:**
        1. Загрузите CSV-файл
        2. Нажмите "Обучить модель"
        3. Ознакомтесь с результатами
        """)
        st.image("static/Training05.png", width = 1000)

    with st.expander("💬 Анализ чатов", expanded=False):
        st.markdown("""
        **Шаги:**
        1. Экспортируйте нужный вам чат по инструкции ниже
        2. Загрузите HTML-файл чата
        3. Нажмите "Анализировать чат"
        4. Ознакомтесь с результатами
        """)
        st.video("static/analisys_chat.mp4", muted=True)
        st.markdown("Как скачать чат из telegram в формате HTML для анализа активности?")
        st.video("static/tgHTML.mp4", muted=True)




