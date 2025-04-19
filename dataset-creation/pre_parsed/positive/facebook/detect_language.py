import string
import enchant

english_dict = enchant.Dict("en_US")

def detect_language(text, word_threshold=0.7, ascii_threshold=0.8):
    """
    Classify a given string as one of the following:
    
    - "bn"  : Bengali (Unicode Bangla script characters)
    - "en"  : English (ASCII characters, high proportion of dictionary-valid English words)
    - "tbn" : Transliterated Bengali (ASCII characters, but words mostly not valid English)
    
    Logic:
    - If ≥30% of characters are in Bengali Unicode block → return "bn"
    - If mostly ASCII:
        - If ≥60% of words are valid English → return "en"
        - Otherwise → return "tbn"
    - If all else fails, default fallback is "en"
    
    Args:
        text (str): Input text to classify
        word_threshold (float): Minimum ratio of English dictionary words for "en"
        ascii_threshold (float): Minimum ASCII character ratio to consider for en/tbn
    
    Returns:
        str: One of "bn", "en", or "tbn"
    """
    text = text.strip()
    if not text:
        return "en"

    total_chars = len(text)
    if total_chars == 0:
        return "en"

    # Count Bengali characters using Unicode block
    bengali_chars = sum(0x0980 <= ord(c) <= 0x09FF for c in text)
    bengali_ratio = bengali_chars / total_chars

    if bengali_ratio > 0.3:
        return "bn"

    # Process ASCII / English detection
    # words = [w.strip(string.punctuation).lower() for w in text.split()]
    import re
    possible_english_words = [re.sub(r'[^\w\s]', ' ', w).lower() for w in text.split()]
    possible_english_words = [w for w in possible_english_words if w]

    nw = []

    for w in possible_english_words:
        nw.extend(w.split())

    possible_english_words = nw

    import re

    def filter_words(words):
        # Return a list of words that contain only English letters
        return [word for word in words if re.match(r'^[a-zA-Z]+$', word) and len(word) > 1]
    
    possible_english_words = filter_words(possible_english_words)

    # print(possible_english_words)

    if not possible_english_words:
        return "en"

    valid_english_words = sum(english_dict.check(w) for w in possible_english_words)
    english_ratio = valid_english_words / len(possible_english_words)

    ascii_chars = sum(ord(c) < 128 for c in text)
    ascii_ratio = ascii_chars / total_chars

    if ascii_ratio < ascii_threshold:
        return "en"

    if english_ratio > word_threshold:
        return "en"
    else:
        return "tbn"


test_cases = {
    "আমি বাংলায় গান গাই": "bn",
    "This is a simple English sentence.": "en",
    "ami banglay gan gai": "tbn",
    "আমি English mix করছি": "bn",
    "I went to the bazar to buy some mangsho": "en",  # borderline tbn but still acceptable en
    "onekdin dhore tomake khujchi": "tbn",
    "Life is beautiful and unpredictable.": "en",
    "এই sentence এ কিছু Bengali কিছু English আছে": "bn",
    "kothay tumi gelo bolo": "tbn",
    "Laptop, charger, mouse sob niye asho": "tbn",
    "What is the weather today?": "en",
    "বিকেলে খেলা আছে": "bn",
    "Gachh-gulo onek boro chhilo": "tbn",
    "1234567890": "en",  # no meaningful text, default to "en"
    "ami jani na ei kotha gulo kothay likhbo": "tbn",
    "I know not where these words should be written": "en",
    "ami tomar sonar bangla valobashi": "tbn",
    "Today is a good day": "en",
    "খাবার খুবই সুস্বাদু ছিল": "bn",
    "bhalo chhilo kintu beshi spicy chhilo": "tbn",
    "Random gibberish fjdskljf ksjdfkjs": "en",  # no Bengali chars, mostly invalid English, still ASCII
    "ami ami ami ami ami ami": "tbn",  # repetition of one transliterated word
}

test_cases = {
    "apple\nbanana\ngrape": "en",
    "O+ blood needed 124 373738 01234": "en",
    "O+ blood needed , dhanmondi 27\nContact:01536207177 আমি": "en"
}

if __name__ == "__main__":
    for txt, expected in test_cases.items():
        pred = detect_language(txt)
        print(f"Text: {txt!r}\nPredicted: {pred} | Expected: {expected} | {'✔️' if pred == expected else '❌'}")
        print('-' * 60)
