import csv

def read_csv(file_path):
    """
    Reads a CSV file and returns its contents as a list of dictionaries.

    :param file_path: The path to the CSV file.
    :return: A list of dictionaries representing the rows in the CSV file.
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data

# Example usage
csv_data = read_csv('output.csv')
for row in csv_data:
    print(row)
