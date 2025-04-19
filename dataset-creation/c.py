import json
import re
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bnunicodenormalizer import Normalizer  # Optional for Bengali text normalization

# Step 1: Load the JSON data
# Replace 'your_file.json' with the path to your JSON file
with open('./pre_parsed_merged.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data = [entry for entry in data if entry['is_blood_donation_request'] is True]

# Step 2: Group texts by language
texts_by_language = defaultdict(list)
for entry in data:
    language = entry['metadata']['language']
    text = entry['text']
    texts_by_language[language].append(text)

# Step 3: Function to clean and split text
import string

def clean_and_split_text(text, language):
    # Define punctuation to remove
    # Start with string.punctuation, which includes common English punctuation
    punctuation = string.punctuation  # Includes !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    
    # For Bengali, add language-specific punctuation like '।' and '॥'
    if language == 'bn':
        punctuation += '।॥'
    
    # Create a regex pattern to match any character in the punctuation set
    # Escape special characters in the punctuation string for regex
    punctuation_pattern = '[' + re.escape(punctuation) + '\n#]'  # Also remove newlines and hashtags
    
    # Replace punctuation with spaces
    text = re.sub(punctuation_pattern, ' ', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Split into words
    words = text.split()
    return words

# s = "আমি বাংলায় গান গাই"

# print(clean_and_split_text(s, "bn"))

# exit(0)

# Step 4: Process each language and generate word clouds
for language, texts in texts_by_language.items():
    # Combine all texts for this language
    combined_text = ' '.join(texts)
    
    # Clean and split the text
    words = clean_and_split_text(combined_text, language)
    
    # Join words back into a single string for the word cloud
    cleaned_text = ' '.join(words)

    font_path = None 
    
    # Step 5: Generate the word cloud
    # Set font path for Bengali if needed
    if language == 'bn':
        font_path = 'kalpurush.ttf'  # e.g., 'NotoSansBengali-Regular.ttf'
    else:
        font_path = None  # Default font for English
    
    # Create the word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        font_path=font_path,  # Specify font for Bengali
        min_font_size=10
    ).generate(cleaned_text)
    
    # Step 6: Display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud for Language: {language}')
    plt.show()

    # Optionally, save the word cloud to a file
    wordcloud.to_file(f'stats/figures/wordcloud_{language}.png')