from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Dummy data
thana_names = [
    "Demra", "Matuail", "Sarulia", "Dholairpar", "Mirpur"
]
full_address = "The address is located in the area of Domra, which is near Matyail. Also close to Sorulia."

def extract_multiple_thanas(full_address, thana_names, limit=5):
    # Extract all possible matches
    matches = process.extractBests(full_address, thana_names, scorer=fuzz.partial_ratio, limit=limit)
    
    # Filter out any matches with a score below a certain threshold if needed
    threshold = 80
    filtered_matches = [match for match in matches if match[1] >= threshold]
    
    return filtered_matches

# Extract thana names from the full address
thana_matches = extract_multiple_thanas(full_address, thana_names)

print("Extracted thana names:")
for thana_name, score in thana_matches:
    print(f"Thana Name: {thana_name}, Score: {score}")
