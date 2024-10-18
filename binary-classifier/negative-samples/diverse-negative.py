import pandas as pd
import random

# List of confusing words to embed in Bengali negative samples
confusing_words_bengali = [
    "ব্লাড", "ব্যাগ", "ইমারজেন্সি", "হাসপাতাল", "রোগী", "রক্ত", 
    "অপারেশন", "গ্রুপ", "প্রয়োজন", "ক্যান্সার", "যোগাযোগ", "লাগবে", 
    "ঠিকানা", "মোবাইল", "রেফারেন্স", "দান", "স্থান", "সময়"
]

# Function to generate 200 diverse Bengali negative samples
def generate_diverse_bengali_negative_samples():
    templates = [
        "আমার {word} নিয়ে সমস্যা হচ্ছে। আপনি কি একটু সাহায্য করতে পারবেন?",
        "{word} নিয়ে অনেক চিন্তিত। এই বিষয়টি দ্রুত সমাধান করা দরকার।",
        "রাস্তায় আমার {word} পড়ে গেছে। খুঁজে পাওয়া যাচ্ছে না।",
        "{word} নিয়ে ক্লাসে আজকের লেকচারটি খুব ইন্টারেস্টিং ছিল।",
        "কেউ কি {word} নিয়ে কোন বই পড়েছে? আমাকে সাজেশন দিতে পারবেন?",
        "মেডিকেল কলেজে {word} নিয়ে একটি সেমিনার হবে।",
        "রাতের বেলা {word} ঘরে ঢুকিয়ে রাখতে ভুলে গেছি।",
        "কফি খাওয়ার সময় {word} নিয়ে আলোচনা করছিলাম।",
        "আমার বন্ধুর বাড়িতে {word} পাওয়া গেছে।",
        "দোকানে {word} নিয়ে ডিসকাউন্ট চলছে। আপনি কি জানতে চেয়েছিলেন?",
        "পরীক্ষার সময় {word} ভুলে গেছি। খুব অসুবিধায় পড়েছি।",
        "বন্ধুর বিয়েতে {word} নিয়ে অনেক মজা হয়েছে।",
        "সপ্তাহের শেষে {word} নিয়ে একটি আড্ডা দেওয়ার পরিকল্পনা করছি।",
        "ক্লাবের মিটিংয়ে {word} নিয়ে আজকে আলোচনা হলো।",
        "ভ্রমণের সময় {word} হারিয়ে ফেলেছি।",
        "ক্লাসের প্রোজেক্টে {word} নিয়ে একটি পেপার লিখতে হবে।",
        "{word} নিয়ে আমাদের পরবর্তী অনুষ্ঠানটি হবে।",
        "সকালে {word} দিয়ে শুরু করেছিলাম। বিকালে সবকিছু গুছিয়েছি।",
        "তোমার মোবাইলে {word} সংক্রান্ত মেসেজ এসেছে?",
        "আমাদের রুমে {word} নিয়ে আড্ডা দিচ্ছিলাম।"
    ]
    
    negative_samples = []
    for _ in range(200):
        template = random.choice(templates)
        word = random.choice(confusing_words_bengali)
        sentence = template.format(word=word)
        negative_samples.append(sentence)
    
    return negative_samples

# Generate diverse negative samples
diverse_negative_samples = generate_diverse_bengali_negative_samples()

# Create DataFrame and label them as 0 (non-blood donation messages)
df_diverse_neg_bengali = pd.DataFrame({"message": diverse_negative_samples, "label": [0] * 200})

# Save the DataFrame to CSV
csv_path = "./negative-samples/diverse_bengali_negative_samples.csv"
df_diverse_neg_bengali.to_csv(csv_path, index=False)
