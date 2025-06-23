import pandas as pd
import re
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s፡፣።]', '', text)
    return text.strip()

def tokenize(text):
    return word_tokenize(text, preserve_line=True)

def preprocess():
    df = pd.read_csv("data/raw/telegram_messages.csv")
    df['normalized'] = df['text'].apply(normalize_text)
    df['tokens'] = df['normalized'].apply(tokenize)
    df.to_csv("data/processed/preprocessed_messages.csv", index=False)
    print("Saved to data/processed/preprocessed_messages.csv")

if __name__ == "__main__":
    preprocess()
