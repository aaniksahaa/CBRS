import json
from collections import Counter

path = "merged-en.json"
top_n = 50

# Read the JSON file
try:
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: path file not found in the current directory.")
    exit(1)
except json.JSONDecodeError:
    print("Error: path file contains invalid JSON.")
    exit(1)

# Extract all text from the "text" field
all_texts = [entry["text"] for entry in data if "text" in entry]

# Split texts by whitespace and combine into a single list of words
all_words = []
for text in all_texts:
    # Split on any whitespace (spaces, tabs, newlines, etc.)
    words = text.split()
    all_words.extend(words)

# Count word frequencies
word_counts = Counter(all_words)

# Get the top 20 most frequent words
top_words = word_counts.most_common(top_n)

# Print the results
print(f"Top {top_n} most frequent words and their frequencies:")
for word, freq in top_words:
    print(f"{word}: {freq}")

# Optionally, save the results to a file
with open(f"top_words-{path.split('.')[0]}.txt", 'w', encoding='utf-8') as f:
    f.write(f"Top {top_n} most frequent words and their frequencies:\n")
    for word, freq in top_words:
        f.write(f"{word}: {freq}\n")