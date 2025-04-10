import json
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bnlp import BengaliCorpus as bn_corpus

# Load Bengali font (ensure this file exists in your directory)
FONT_PATH = "kalpurush.ttf"  # Or any other well-supported Bengali font

# Load the JSON data
with open('pre_parsed_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter for blood donation requests in Bengali
bn_texts = [
    entry['text'] for entry in data
    if entry['is_blood_donation_request'] is True and entry['metadata']['language'] == 'bn'
]

# Combine all Bengali texts
combined_text = ' '.join(bn_texts)

# Clean Bengali text
def clean_bengali_text(text):
    # Remove Bengali punctuations
    text = re.sub('[%s]' % re.escape(bn_corpus.punctuations), ' ', text)

    # Remove newlines, non-Bengali characters, digits, weird unicode chars
    text = re.sub(r'\n|\xa0', ' ', text)
    text = re.sub(r'[0-9০-৯]', '', text)  # Remove digits (both English and Bengali)
    text = ' '.join(re.findall(r'[\u0980-\u09FF]+', text))  # Keep only Bengali words

    # Remove stopwords
    words = text.split()
    filtered_words = [word for word in words if word not in bn_corpus.stopwords]
    return ' '.join(filtered_words)

cleaned_text = clean_bengali_text(combined_text)

# Generate word cloud
wordcloud = WordCloud(
    width=2560,
    height=1440,
    background_color='white',
    font_path=FONT_PATH,
    regexp=r'[\u0980-\u09FF]+',
    min_font_size=10
).generate(cleaned_text)

# Display
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('', fontsize=16)
plt.show()

# Optional: Save it
wordcloud.to_file("wordcloud_bn.png")
