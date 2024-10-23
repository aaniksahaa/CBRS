import pandas as pd
import random

# Expanded list of positive samples with varied phrasing and structure
positive_samples = [
    "Urgent! A- blood required at City Hospital for surgery. Contact: +8801234567890",
    "Help needed: B+ blood for a patient in ICU at Dhaka Medical. Please reach out: +880987654321",
    "Patient in critical condition requires O- blood. Location: Crescent Hospital, Dhaka. Contact immediately: +8801923456789",
    "Looking for AB+ blood donors. Child patient in emergency care at Apollo Hospital. Contact: +880156789234",
    "Blood needed: 2 bags of O+ required urgently at Suhrawardy Hospital. Please respond quickly: +8801112233445",
    "A- blood urgently needed at the Cancer Institute for an operation. Contact if available: +8809988776655",
    "Immediate requirement: AB- blood for trauma patient at Enam Medical College. Contact: +8805556667778",
    "Critical condition! Patient requires 3 units of B+ blood at Square Hospital. Please help: +8801223344556",
    "Emergency blood request: O+ needed at Green Life Hospital. Contact number: +8801711223344",
    "Help save a life: Blood group A+ required for a patient at Delta Hospital. Reach out: +8801999887766"
]

# Expanded list of negative samples with varied topics and contexts
negative_samples = [
    "Planning a road trip this weekend. Who's joining?",
    "Had a great time at the music festival last night!",
    "Does anyone know a good restaurant near Dhanmondi?",
    "Just finished a 5k run! Feeling amazing.",
    "Meeting postponed to next Monday at 3 PM.",
    "Reading an interesting book about machine learning.",
    "The football game last night was thrilling!",
    "I'm planning to go hiking next month.",
    "Can someone recommend a good movie to watch?",
    "Went to the park today; it was so peaceful.",
    "Birthday celebrations coming up this weekend!",
    "Enjoying my coffee at a new café near my house.",
    "Trying to learn a new recipe. Any tips?",
    "Anyone interested in joining a book club?",
    "Attending a workshop on public speaking tomorrow.",
    "The sunset view from the rooftop was amazing.",
    "Grocery shopping done! Ready for the week.",
    "Spending some quality time with family today.",
    "Does anyone play chess? Looking for a partner.",
    "Is anyone available for a call this evening?"
]

# Function to generate samples with random variations
def generate_samples(samples, n):
    generated_samples = []
    for _ in range(n):
        sample = random.choice(samples)
        variation = random.choice(["!", ".", ""])  # Add minor variations
        generated_samples.append(sample + variation)
    return generated_samples


num_samples = 400
# Generate 400 positive and 400 negative samples with diversity
positive_samples_final = generate_samples(positive_samples, num_samples)
negative_samples_final = generate_samples(negative_samples, num_samples)

# Create DataFrame with the generated samples
data = {
    "message": positive_samples_final + negative_samples_final,
    "label": [1] * num_samples + [0] * num_samples
}
df = pd.DataFrame(data)

# Save the dataset to CSV
csv_path = "./english_dataset.csv"
df.to_csv(csv_path, index=False)