import csv
import re

# Function to process the SQL file and extract data
def process_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql_content = file.read()

    # Extracting the columns from the SQL insert statement
    columns_pattern = re.compile(r'`([^`]*)`')
    columns = columns_pattern.findall(sql_content.split("insert")[1])

    # Extracting the values part from the SQL insert statement
    values_part = sql_content.split("values")[1].strip().rstrip(';')

    # Extracting individual value tuples
    values_pattern = re.compile(r'\((.*?)\)')
    values_tuples = values_pattern.findall(values_part)

    # Parsing each tuple into a list of values
    values_list = []
    for value_tuple in values_tuples:
        # Removing single quotes around values and splitting by comma
        values = re.findall(r"'(.*?)'|(\d+)", value_tuple)
        # Flattening the tuple and filtering out None entries
        values = [val for sublist in values for val in sublist if val]
        values_list.append(values)

    return columns, values_list

# Writing data to CSV
def write_to_csv(columns, values_list, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns)  # Writing the header
        csvwriter.writerows(values_list)  # Writing the data rows

    print(f"CSV file '{output_file}' generated successfully.")

# Main function
def main():
    input_file = 'districts.sql'  # Replace with your input SQL file name
    output_file = 'districts.csv'

    columns, values_list = process_sql_file(input_file)
    write_to_csv(columns, values_list, output_file)

if __name__ == "__main__":
    main()
