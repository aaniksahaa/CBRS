import json
from collections import Counter
from util import *

# Your JSON array
data = read_json('./dataset/parsed_merged.json')

# Count languages
language_counts = Counter(item["metadata"]["language"] for item in data)

# Display the distribution
print("Language Distribution:")
for language, count in language_counts.items():
    print(f"{language}: {count}")

# hello