import re
from pymorphy3 import MorphAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from natasha import NamesExtractor, MorphVocab


class DataPreprocessor:
    def __init__(self, text_column='MessageText'):
        self.text_column = text_column
        self.morph = MorphAnalyzer(lang='ru')

    def clean_text(self, text):
        try:
            text = re.sub(r'<[^>]*>', ' ', text, flags=re.MULTILINE)
            text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
            text = re.sub(r'[^а-яА-ЯёЁ\s-]', ' ', text, flags=re.IGNORECASE)
            text = re.sub(r'[\s-]+', ' ', text)
            return text.strip().lower()
        except Exception as e:
            print(f"Error in clean_text with text: {text}\n{e}")
            raise

    def remove_stopwords(self, text, language='russian'):
        try:
            base_stopwords = set(stopwords.words(language))
            keep_words = {
                'не', 'ни', 'нет', 'без', 'никак', 'вовсе', 'отнюдь',  # Отрицания
                'очень', 'совсем', 'абсолютно', 'совершенно', 'крайне',  # Интенсификаторы
                'ли', 'ведь', 'либо', 'даже',  # Модальные частицы
                'хорошо', 'плохо', 'ужасно', 'прекрасно'  # Оценочные прилагательные
            }
            final_stopwords = base_stopwords - keep_words
            words = word_tokenize(text, language=language)
            return ' '.join([w for w in words if w.lower() not in final_stopwords])
        except Exception as e:
            print(f"Error in remove_stopwords with text: {text}\n{e}")
            raise

    def lemmatize_text(self, text):
        try:
            words = word_tokenize(text, language='russian')
            lemmas = []
            for word in words:
                parsed = self.morph.parse(word)[0]
                lemmas.append(parsed.normal_form)
            return ' '.join(lemmas)
        except Exception as e:
            print(f"Error in lemmatize_text with text: {text}\n{e}")
            raise

    def remove_names_natasha(self, text):
        try:
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
        except Exception as e:
            print(f"Error in remove_names_natasha with text: {text}\n{e}")
            raise

    def preprocess_dataset(self, df):
        # Функция-обёртка для отлавливания ошибок на каждом шаге
        def safe_apply(func, text):
            try:
                return func(text)
            except Exception as e:
                print(f"Error in function {func.__name__} for text: {text}\n{e}")
                raise

        # Проверка наличия нужного столбца
        if self.text_column not in df.columns:
            raise ValueError(
                f"Column '{self.text_column}' not found in CSV. Available columns: {df.columns.tolist()}"
            )

        try:
            # Приводим столбец к строковому типу и удаляем пустые строки
            df[self.text_column] = df[self.text_column].astype(str)
            df = df[df[self.text_column].str.strip() != '']
        except Exception as e:
            print("Error converting or filtering text column:", e)
            raise

        # Удаление имен
        try:
            df[self.text_column] = df[self.text_column].apply(lambda x: safe_apply(self.remove_names_natasha, x))
        except Exception as e:
            print("Error during remove_stopwords stage:", e)
            raise

        # Замена цифр на пустую строку
        try:
            df[self.text_column] = df[self.text_column].str.replace(r'\b\d+\b', '', regex=True)
        except Exception as e:
            print("Error in regex replacement:", e)
            raise

        # Применяем по очереди функции очистки, удаления стоп-слов и лемматизации
        try:
            df[self.text_column] = df[self.text_column].apply(lambda x: safe_apply(self.clean_text, x))
        except Exception as e:
            print("Error during clean_text stage:", e)
            raise

        try:
            df[self.text_column] = df[self.text_column].apply(lambda x: safe_apply(self.remove_stopwords, x))
        except Exception as e:
            print("Error during remove_stopwords stage:", e)
            raise

        try:
            df[self.text_column] = df[self.text_column].apply(lambda x: safe_apply(self.lemmatize_text, x))
        except Exception as e:
            print("Error during lemmatize_text stage:", e)
            raise

        # Удаляем записи, где итоговый текст пустой
        df = df.dropna(subset=[self.text_column])
        return df

    def preprocess_text(self, text):
        try:
            text = re.sub(r'\b\d+\b', '', text)
            text = self.clean_text(text)
            text = self.remove_stopwords(text)
            text = self.lemmatize_text(text)
            return text
        except Exception as e:
            print("Error in preprocess_text:", e)
            raise