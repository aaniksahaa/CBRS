import pandas as pd
import random

# List of confusing words to embed alongside random words
confusing_words_bengali = [
    "ব্লাড", "ব্যাগ", "ইমারজেন্সি", "হাসপাতাল", "রোগী", "রক্ত", 
    "অপারেশন", "গ্রুপ", "প্রয়োজন", "ক্যান্সার", "যোগাযোগ", "লাগবে", 
    "ঠিকানা", "মোবাইল", "রেফারেন্স", "দান", "স্থান", "সময়"
]

# List of random words to increase vocabulary
random_words_bengali = [
    "বই", "কফি", "গাছ", "মেলা", "মুভি", "বাড়ি", "বৃষ্টি", "গান", 
    "পাখি", "রেস্তোরাঁ", "বন্ধু", "স্কুল", "ক্লাস", "ভ্রমণ", "খেলা", 
    "বিস্কুট", "ট্রেন", "সাইকেল", "কম্পিউটার", "ছবি"
]

# Function to generate 200 Bengali negative samples with random vocabulary
def generate_vocabulary_rich_bengali_samples():
    templates = [
        "আমি {random_word} নিয়ে খুব ব্যস্ত ছিলাম, কিন্তু {confusing_word} নিয়ে ভাবিনি।",
        "আজকের দিনে {random_word} আর {confusing_word} নিয়ে অনেক কথা হলো।",
        "{random_word} নিয়ে ভাবছিলাম যখন কেউ {confusing_word} ঘরে চলে এলো।",
        "আমার {random_word} হারিয়ে গেছে, এটা হয়তো {confusing_word} রুমে আছে।",
        "আপনি কি {random_word} নিয়ে পড়াশোনা করেছেন? আমি কিছু {confusing_word} নিয়ে জানতে চাই।",
        "বৃষ্টির মধ্যে {random_word} হাতে নিয়ে দাঁড়িয়েছিলাম, আর কেউ {confusing_word} বলে ডাকছিল।",
        "আমরা একসাথে {random_word} খেতে যাচ্ছিলাম এবং পথে {confusing_word} রুমের পাশ দিয়ে গিয়েছিলাম।",
        "আমার {random_word} ব্যাগ হারিয়ে গেছে, আর {confusing_word} রুমে নেই।",
        "বন্ধুর সাথে {random_word} দেখতে বসেছিলাম, হঠাৎ {confusing_word} নিয়ে মেসেজ পেলাম।",
        "{random_word} কেনার সময় দোকানে {confusing_word} নিয়ে একটি আলোচনার মধ্যে পড়ে গেলাম।"
    ]
    
    negative_samples = []
    for _ in range(200):
        template = random.choice(templates)
        random_word = random.choice(random_words_bengali)
        confusing_word = random.choice(confusing_words_bengali)
        sentence = template.format(random_word=random_word, confusing_word=confusing_word)
        negative_samples.append(sentence)
    
    return negative_samples

# Generate diverse negative samples with a rich vocabulary
vocabulary_rich_negative_samples = generate_vocabulary_rich_bengali_samples()

# Create DataFrame and label them as 0 (non-blood donation messages)
df_vocabulary_rich_bengali = pd.DataFrame({"message": vocabulary_rich_negative_samples, "label": [0] * 200})

# Save the DataFrame to CSV
csv_path = "./negative-samples/vocabulary_rich_bengali_negative_samples.csv"
df_vocabulary_rich_bengali.to_csv(csv_path, index=False)