import pandas as pd
import random

# List of Banglish positive samples with diverse structure
positive_samples_banglish = [
    "B (-) Negative Blood urgent darkar.\n\nPatient Ghatal hospital e admit.\nকেউ ডোনেট করতে ইচ্ছুক থাকে Please যোগাযোগ করুন.",
    "Urgent A- blood dorkar\nLocation: Mirpur 10 Ajmol hospital\nContact: 01932993314\nAdmin please approve this post fast, urgent.",
    "আমার বন্ধু Jannatu Nayem Evan এর জন্য ইমার্জেন্সি O+ blood লাগবে\nEmergency 10 bag O+ blood lagbe\nOnk serious obostha amar friend er.\nBlood group: O+\nAmount: 10 bag\nHospital: Evercare Hospital\nLocation: Bashundhara\nPlease help. It's urgent.\nMobile: 01719337179",
    "Emergency O- blood dorkar!\nPatient ICU te admit, Dhaka Medical College\nContact: 01812345678, please respond quickly.",
    "AB+ blood lagbe operation er jonno, Central Hospital Dhaka te.\nContact: 01677123456, urgent need.",
    "Urgent need of 3 bags of A+ blood at Green Life Hospital.\nPatient critical condition, please help!\nContact: 01723456789.",
    "Rokto dorkar ekta patient er jonno ICU te.\nGroup: B+\nLocation: Square Hospital, Dhanmondi.\nContact: 01823456789.",
    "Please donate AB- blood, operation cholche Ekushey Medical e.\nNeed 2 bags.\nContact: 01512345678, urgent!",
    "Emergency! Need O+ blood for a 10-year-old child at Mirpur Child Hospital.\nContact: 01987654321.",
    "Friend er father er jonno B+ blood lagbe quickly!\nLocation: Apollo Hospital, Bashundhara.\nContact: 01887654321."
]

# List of Banglish negative samples with diverse topics
negative_samples_banglish = [
    "Aj kalke amader plan ache ekta cricket match khelar.",
    "Friend der shathe coffee khawar jonno jabo kal.",
    "Office e agamikal ekta presentation dite hobe.",
    "Movie night korbo ajke rat e, ke ke interested?",
    "Amar naya backpack khub joss lagse.",
    "Kalke ekta new book store visit korlam.",
    "The food festival last night was amazing!",
    "Ei shomoy te travel kora khub moja hobe.",
    "Amra shobai picnic e jabo next week.",
    "Kothay valo coffee shop ache? Kew bolte paro?",
    "Raat e amar friend er shathe ekta movie dekhbo.",
    "New restaurant ta khub valo chilo.",
    "Exam er preparation chalche pura din.",
    "Bhalo thakish, dekha hobe kobe ke jane!",
    "Ei rain ta ekdom unexpected!",
    "Reading books keeps me relaxed.",
    "Amader agamikal cricket practice ache.",
    "Lunch e meet korbo ajke shobai mile.",
    "Raat e ekta concert e jabo.",
    "Next camp ta Dhaka te hobe."
]

# Function to generate samples with random variations
def generate_samples(samples, n):
    generated_samples = []
    for _ in range(n):
        sample = random.choice(samples) + random.choice(["", "!", "."])
        generated_samples.append(sample)
    return generated_samples

num_samples = 200
# Generate 100 positive and 100 negative Banglish samples
positive_samples_final = generate_samples(positive_samples_banglish, num_samples)
negative_samples_final = generate_samples(negative_samples_banglish, num_samples)

# Create DataFrame with generated samples
data = {
    "message": positive_samples_final + negative_samples_final,
    "label": [1] * num_samples + [0] * num_samples
}
df = pd.DataFrame(data)

# Save the dataset to CSV
csv_path = "./banglish_dataset.csv"
df.to_csv(csv_path, index=False)
