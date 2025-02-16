import re
import pandas as pd
from pymorphy3 import MorphAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from natasha import NamesExtractor, MorphVocab

class DataPreprocessor:
    def __init__(self, text_column = 'text'):
        self.text_column = text_column
        self.morph = MorphAnalyzer(lang='ru')

    def clean_text(self, text):
        text = re.sub(r'<[^>]*>', ' ', text, flags=re.MULTILINE)
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        text = re.sub(r'[^а-яА-ЯёЁ\s-]', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'[\s-]+', ' ', text)
        return text.strip().lower()
    
    def remove_stopwords(self, text, language = 'russian'):
        base_stopwords = set(stopwords.words(language))
        keep_words = {
            'не', 'ни', 'нет', 'без', 'никак', 'вовсе', 'отнюдь',  # Отрицания
            'очень', 'совсем', 'абсолютно', 'совершенно', 'крайне',  # Интенсификаторы
            'ли', 'ведь', 'либо', 'даже',  # Модальные частицы
            'хорошо', 'плохо', 'ужасно', 'прекрасно'  # Оценочные прилагательные
        }
        final_stopwords = base_stopwords - keep_words
        words = word_tokenize(text, language='russian')
        return ' '.join([w for w in words if w.lower() not in final_stopwords])

    def lemmatize_text(self, text):
        words = word_tokenize(text, language='russian')
        lemmas = []
        for word in words:
            parsed = self.morph.parse(word)[0]
            lemmas.append(parsed.normal_form)
        return ' '.join(lemmas)
    
    def remove_names_natasha(self, text):
        extractor = NamesExtractor(MorphVocab())
        matches = extractor(text)
        spans = []
        
        for match in matches:
            fact = match.fact
            if fact.first or fact.middle:  
                spans.append((match.start, match.stop))
        
        cleaned_text = []
        last_end = 0
        for start, end in sorted(spans):
            cleaned_text.append(text[last_end:start])
            last_end = end
        cleaned_text.append(text[last_end:])
        
        return ''.join(cleaned_text)

    def preprocess_dataset(self, df):
        df[self.text_column] = df[self.text_column].apply(self.remove_names_natasha)
        df[self.text_column] = df[self.text_column].str.replace(r'\b\d+\b', '')
        df[self.text_column] = df[self.text_column].apply(self.clean_text)
        df[self.text_column] = df[self.text_column].apply(self.remove_stopwords)
        df[self.text_column] = df[self.text_column].apply(self.lemmatize_text)
        df.dropna(subset=[self.text_column])
        return df
    
    def preprocess_text(self, text):
        text = self.remove_names_natasha(text)
        text = re.sub(r'\b\d+\b', '', text)
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        text = self.lemmatize_text(text)
        return text
    
if __name__ == "__main__":
    print("Выберите режим:\n 0 - текст\n 1 - датасет")
    mode = int(input())

    if mode == 0:
        print("Введите ваш текст:")
        text = input()
        clean_text = DataPreprocessor().preprocess_text(text)
        print("Очищенный текст: ", clean_text)

    if mode == 1:
        data = pd.read_csv('datasets.csv')
        print("Идет очистка датасета:\n")
        data_clean = DataPreprocessor().preprocess_dataset(data.copy())
        data_clean.to_csv('data_clean.csv', index=False)
    