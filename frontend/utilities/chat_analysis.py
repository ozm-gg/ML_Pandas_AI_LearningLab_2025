import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import tempfile

def generate_pdf_report(df, fig1, fig_top, fig_top_neg, fig_hour):
    pdf = FPDF()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    pdf.add_page()
    try:
        pdf.image("SentimentPanda.png", x=10, y=8, w=30)
    except Exception as e:
        st.error(f"Ошибка при загрузке логотипа: {e}")
    pdf.set_font("DejaVu", "B", 32)
    pdf.cell(0, 10, "SentimentPanda", ln=True, align="C")
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "Анализ Тональности Текста", ln=True, align="C")
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Дата анализа: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align="C")
    pdf.ln(20)
    
    def add_fig_page(fig, title):
        try:
            pdf.add_page()
            pdf.set_font("DejaVu", "B", 14)
            pdf.cell(0, 10, title, ln=True, align="C")
            pdf.ln(5)
            
            if not fig or not hasattr(fig, 'write_image'):
                raise ValueError("Invalid figure object")
                
            img_bytes = fig.to_image(format="png", scale=1, width=1000)

            temp_dir = "/tempfile"
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=temp_dir) as tmpfile:
                tmpfile.write(img_bytes)
                tmpfile.flush()
                image_path = tmpfile.name
    
            pdf.image(image_path, x=15, y=30, w=pdf.w - 30)

                
        except Exception as e:
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(0, 10, f"Ошибка при добавлении графика {title}: {str(e)}")
            st.error(f"PDF Error: {str(e)}")
    
    # if fig1 is not None:
    #     add_fig_page(fig1, "Распределение предсказанных меток")
    # if fig_top is not None:
    #     add_fig_page(fig_top, "Топ-3 позитивных участников")
    # if fig_top_neg is not None:
    #     add_fig_page(fig_top_neg, "Топ-3 негативных участников")
    # if fig_hour is not None:
    #     add_fig_page(fig_hour, "Активность и настроения по часам")
    
    pdf_str = pdf.output(dest="S")
    pdf_bytes = pdf_str.encode("latin-1", errors="replace")
    return pdf_bytes

def chat_analysis(backend_url):
    st.sidebar.header("Настройки анализа чатов")
    uploaded_file = st.sidebar.file_uploader("Загрузите HTML файл", type="html")
    analyze_button = st.sidebar.button("Анализировать чат")
    saved = False

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
                    saved = True

                    COLOR_SCHEME = {
                        "Негативный": "#EF553B",
                        "Нейтральный": "#636EFA",
                        "Позитивный": "#00CC96"
                    }

                    # Гистограмма распределения по классам
                    st.subheader("Распределение предсказанных меток")
                    fig1 = px.histogram(df, x="label", title="Распределение меток")
                    st.plotly_chart(fig1)

                    # Счет очков настроения
                    sentiment_map = {'Negative': 1, 'Neutral': 2, 'Positive': 3}
                    df['sentiment_score'] = df['label'].map(sentiment_map)

                    df_grouped = df.groupby('Sender').agg(
                        total_sentiment=('sentiment_score', 'sum'),
                        avg_sentiment=('sentiment_score', 'mean'),
                        message_count=('sentiment_score', 'count')
                    ).reset_index()

                    top_positive = df_grouped.nlargest(3, 'avg_sentiment')
                    top_negative = df_grouped.nsmallest(3, 'avg_sentiment')

                    # Топ участников
                    st.subheader("Активность участников по настроению")
                    col1, col2 = st.columns(2)

                    with col1:
                        top_positive = df.groupby('Sender')['sentiment_score'] \
                                        .mean().nlargest(3).reset_index()
                        fig_top = px.bar(top_positive, 
                                        x='sentiment_score', 
                                        y='Sender',
                                        orientation='h',
                                        title='Топ-3 позитивных участников',
                                        color='sentiment_score',
                                        color_continuous_scale=['#D3D3D3', '#00CC96'],
                                        text_auto='.2f')
                        fig_top.update_layout(showlegend=False)
                        st.plotly_chart(fig_top, use_container_width=True)

                    with col2:
                        top_negative = df.groupby('Sender')['sentiment_score'] \
                                        .mean().nsmallest(3).reset_index()
                        fig_top_neg = px.bar(top_negative, 
                                            x='sentiment_score', 
                                            y='Sender',
                                            orientation='h',
                                            title='Топ-3 негативных участников',
                                            color='sentiment_score',
                                            color_continuous_scale=['#EF553B', '#D3D3D3'],
                                            text_auto='.2f')
                        fig_top_neg.update_layout(showlegend=False)
                        st.plotly_chart(fig_top_neg, use_container_width=True)

                    # График распределения активности и настроений по времени
                    st.subheader("Распределение активности и настроений")
                    fig_time = px.histogram(df, 
                                            x='datetime', 
                                            nbins=50,
                                            color='label',
                                            color_discrete_map=COLOR_SCHEME,
                                            labels={'datetime': 'Дата и время'},
                                            hover_data=['Message'],
                                            title='История сообщений с настроями')
                    fig_time.update_layout(barmode='stack', xaxis_title=None)
                    st.plotly_chart(fig_time)

                    # График активности и настроений по часам
                    df['hour'] = df['datetime'].dt.hour
                    hourly_stats = df.groupby('hour')['sentiment_score'].agg(['mean', 'count']).reset_index()

                    fig_hour = px.bar(hourly_stats, 
                                      x='hour', 
                                      y='count',
                                      color='mean',
                                      color_continuous_scale='RdYlGn',
                                      labels={'count': 'Кол-во сообщений', 'mean': 'Средний настрой'},
                                      title='Активность и настроения по часам суток',
                                      height=400)
                    fig_hour.update_layout(coloraxis_colorbar=dict(title="Средний балл"))
                    st.plotly_chart(fig_hour)

                    # Тепловая карта
                    st.subheader("Тепловая карта настроений")
                    try:
                        heatmap_data = df.pivot_table(
                            index=df['datetime'].dt.date,
                            columns=df['datetime'].dt.hour,
                            values='sentiment_score',
                            aggfunc='mean'
                        )
                        
                        fig_heatmap = px.imshow(
                            heatmap_data,
                            labels=dict(x="Час", y="Дата", color="Настрой"),
                            color_continuous_scale='RdYlGn',
                            title='Средняя тональность по дням и часам'
                        )
                        st.plotly_chart(fig_heatmap)
                    except Exception as e:
                        st.error(f"Ошибка при построении тепловой карты: {str(e)}")
                    
                except requests.exceptions.RequestException as e:
                    saved = False
                    st.error(f"Ошибка при отправке файла: {e}")
        else:
            st.error("Пожалуйста, загрузите HTML файл.")

    if saved:
        st.sidebar.header("Скачать PDF отчет")
        try:
            pdf_bytes = generate_pdf_report(df, fig1, fig_top, fig_top_neg, fig_hour)
            st.sidebar.download_button(
                label="Скачать PDF отчет",
                data=pdf_bytes,
                file_name="report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Ошибка при генерации PDF: {e}")