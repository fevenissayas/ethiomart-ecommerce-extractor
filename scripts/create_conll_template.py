import pandas as pd
import re
from nltk.tokenize import word_tokenize
import os

def normalize_text(text):
    text = re.sub(r'\s+', ' ', str(text))
    text = re.sub(r'[^\w\s፡፣።]', '', text)
    return text.strip()

# Load the preprocessed data
df = pd.read_csv("data/processed/preprocessed_messages.csv")

# Sample 40 messages for manual NER labeling
sample = df.sample(40)

# Ensure output folder exists
os.makedirs("data/labeled", exist_ok=True)

with open("data/labeled/unlabeled_conll.txt", "w", encoding="utf-8") as f:
    for row in sample.itertuples():
        text = normalize_text(row.text)
        tokens = word_tokenize(text, preserve_line=True)  # FIX applied here!
        for token in tokens:
            f.write(f"{token}\tO\n")
        f.write("\n")  # Separate messages
