import json
import re
import string
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bnlp import BengaliCorpus as bn_corpus

# Step 1: Load the JSON data
with open('./pre_parsed_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter for entries where is_blood_donation_request is true
data = [entry for entry in data if entry['is_blood_donation_request'] is True]

# Step 2: Group texts by language
texts_by_language = defaultdict(list)
for entry in data:
    language = entry['metadata']['language']
    text = entry['text']
    texts_by_language[language].append(text)

# Step 3: Function to clean and split text
def clean_and_split_text(text, language):
    if language == 'bn':
        # Use bnlp_toolkit's punctuations for Bengali
        text = re.sub('[%s]' % re.escape(bn_corpus.punctuations), ' ', text)
        # Remove newlines, digits, and specific Unicode artifacts
        text = re.sub('\n', ' ', text)
        text = re.sub(r'\w*\d\w*', ' ', text)  # Remove words with digits
        text = re.sub('\xa0', ' ', text)
        # Keep only Bengali characters (Unicode range for Bengali: \u0980-\u09FF)
        text = ' '.join(re.findall(r'[\u0980-\u09FF]+', text))
    else:  # For 'en' and 'tbn'
        # Use string.punctuation for English and transliterated text
        punctuation = string.punctuation
        punctuation_pattern = '[' + re.escape(punctuation) + '\n#]'
        text = re.sub(punctuation_pattern, ' ', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Split into words
    words = text.split()
    return words

# Step 4: Process each language and generate word clouds
for language, texts in texts_by_language.items():
    print(language)

    # Combine all texts for this language
    combined_text = ' '.join(texts)
    
    # Clean and split the text
    words = clean_and_split_text(combined_text, language)
    
    # Filter out stopwords for Bengali
    if language == 'bn':
        words = [word for word in words if word not in bn_corpus.stopwords]
    
    # Join words back into a single string for the word cloud
    cleaned_text = ' '.join(words)

    if language == 'bn':
        from util import *
        print(len(cleaned_text))
        write_txt("bn.txt", cleaned_text[:19990])
    
    # Step 5: Generate the word cloud
    # Set font path for Bengali
    if language == 'bn':
        font_path = 'kalpurush.ttf'  # Path to the downloaded Bengali font
    else:
        font_path = None  # Default font for English
    
    # Create the word cloud (no mask, just a rectangle)
    wordcloud = WordCloud(
        width=2560,
        height=1440,
        background_color='white',
        font_path=font_path,  # Specify font for Bengali
        min_font_size=10,
        stopwords=bn_corpus.stopwords if language == 'bn' else None,  # Use Bengali stopwords
        regexp=r'[\u0980-\u09FF]+' if language == 'bn' else None  # Regex for Bengali characters
    ).generate(cleaned_text)
    
    # Step 6: Display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud for Language: {language}')
    # plt.show()

    if language != "bn":
        # Optionally, save the word cloud to a file
        wordcloud.to_file(f'./dataset_stats/figures/wordcloud_{language}.pdf')