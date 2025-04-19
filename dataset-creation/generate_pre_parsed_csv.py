import json
import csv
from util import * 

json_data = read_json('./pre_parsed_merged.json')

# Step 2: Prepare the CSV file
csv_file = "pre_parsed_dataset.csv"
csv_columns = ["text", "language", "source", "label"]

# Step 3: Write to CSV
try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()  # Write the header row

        for entry in json_data:
            # Map is_blood_donation_request to label (0 or 1)
            label = 1 if entry["is_blood_donation_request"] else 0

            # Create a row dictionary with the required fields
            row = {
                "text": entry["text"],
                "language": entry["metadata"]["language"],
                "source": entry["metadata"]["source"],
                "label": label
            }
            writer.writerow(row)

    print(f"✅ CSV file '{csv_file}' has been created successfully.")

except Exception as e:
    print(f"An error occurred: {e}")