from bs4 import BeautifulSoup
import pandas as pd

class TelegramChatParser:
    def __init__(self, html_path):
        self.html_path = html_path
        self.messages = []
    
    def extract_name(self, from_name_tag):
        if from_name_tag:
            for span in from_name_tag.find_all('span', class_='date details'):
                span.extract()
            return from_name_tag.get_text(strip=True)
        return None
    
    def parse(self):
        with open(self.html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        
        sender_name = None
        for message in soup.find_all('div', class_='message'):
            sender = message.find('div', class_='from_name')
            text = message.find('div', class_='text')
            
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
                
                self.messages.append([sender_name, text_content])
    
    def to_csv(self, output_path):
        self.parse()
        df = pd.DataFrame(self.messages, columns=['Sender', 'Message'])
        df = df[df['Message'].str.strip() != ""]
        df.to_csv(output_path, index=False, encoding='utf-8')

if __name__ == "__main__":
    TelegramChatParser("messages.html").to_csv("chat_messages.csv")
