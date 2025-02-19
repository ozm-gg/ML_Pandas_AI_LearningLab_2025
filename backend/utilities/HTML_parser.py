from bs4 import BeautifulSoup
import pandas as pd


class TelegramChatParser:
    def __init__(self, html_content, is_file=True):
        self.html_content = html_content
        self.is_file = is_file
        self.messages = []

    def extract_name(self, from_name_tag):
        try:
            if from_name_tag:
                for span in from_name_tag.find_all('span', class_='date details'):
                    span.extract()
                return from_name_tag.get_text(strip=True)
            return None
        except Exception as e:
            print(f"Error in extract_name: {e}")
            raise

    def parse(self):
        try:
            if self.is_file:
                with open(self.html_content, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
            else:
                soup = BeautifulSoup(self.html_content, 'html.parser')

            sender_name = None
            for message in soup.find_all('div', class_='message'):
                sender = message.find('div', class_='from_name')
                text = message.find('div', class_='text')
                date_tag = message.find('div', class_='pull_right date details')

                # Обработка даты и времени
                date_str = ''
                time_display = ''
                if date_tag and date_tag.has_attr('title'):
                    title = date_tag['title']
                    if ' ' in title:
                        date_split = title.split(' ', 1)
                        date_str = date_split[0]
                        time_part = date_split[1].split(' ', 1)[0]
                        time_display = time_part[:5]  # Берем часы и минуты

                if sender:
                    sender_name = sender.get_text(strip=True)

                if text:
                    text_content = text.get_text(" ", strip=True)

                    forwarded = message.find('div', class_='forwarded body')
                    if forwarded:
                        forwarded_sender = forwarded.find('div', class_='from_name')
                        extracted_name = self.extract_name(forwarded_sender)
                        if extracted_name:
                            sender_name = extracted_name

                    self.messages.append([sender_name, text_content, date_str, time_display])
        except Exception as e:
            print(f"Error in parse: {e}")
            raise

    def to_dataframe(self):
        try:
            self.parse()
            df = pd.DataFrame(self.messages, columns=['Sender', 'Message', 'Date', 'Time'])
            return df[df['Message'].str.strip() != ""]
        except Exception as e:
            print(f"Error in to_dataframe: {e}")
            raise