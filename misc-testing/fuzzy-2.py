from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Define some example phrases
phrase1 = "The quick brown fox jumps over the lazy dog"
phrase2 = "The quick brown fox jumps over the lazy dogs"
phrase3 = "A quick brown fox leaped over the lazy hound"

# Compare two phrases using fuzz.ratio
similarity1 = fuzz.ratio(phrase1, phrase2)
similarity2 = fuzz.ratio(phrase1, phrase3)

print(f"Similarity between phrase1 and phrase2: {similarity1}%")
print(f"Similarity between phrase1 and phrase3: {similarity2}%")

# List of phrases to search from
phrases = [
    "The quick brown fox jumps over the lazy dog",
    "A fast dark fox leaps over the sleepy canine",
    "A quick brown fox leaped over the lazy hound",
    "The quick brown fox jumps over the lazy dogs"
]

# Find the best match for a given phrase
query = "The quick brown fox jumps over a lazy cat"
best_match = process.extractOne(query, phrases)

print(f"Best match for the query: {best_match}")
