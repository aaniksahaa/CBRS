from collections import Counter
import re

def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def tokenize(text):
    # Matches Bengali (U+0980 to U+09FF) and English word characters
    return re.findall(r'[\u0980-\u09FF\w]+', text.lower())

def top_frequent_words(text, top_n=50):
    words = tokenize(text)
    counter = Counter(words)
    return counter.most_common(top_n)

def save_to_file(word_freqs, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for word, count in word_freqs:
            f.write(f"{word}\n")

def main():
    input_file = 'messages_500.txt'       # Replace with your input filename
    output_file = 'top_words.txt'  # Output filename
    text = load_text(input_file)
    top_words = top_frequent_words(text)
    save_to_file(top_words, output_file)
    print(f"Top {len(top_words)} words written to {output_file}")

if __name__ == '__main__':
    main()
