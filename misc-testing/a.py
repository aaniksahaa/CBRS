import csv
import re

# The input SQL insert statement
sql_insert = """INSERT INTO `districts`(`id`,`division`,`district`,`thana`,`postoffice`,`postcode`,`created_at`,`updated_at`) 
                VALUES 
                (1,'Dhaka','Dhaka','Demra','Demra','1360','2015-06-25 11:41:13','2015-06-25 11:41:13'),
                (2,'Dhaka','Dhaka','Demra','Matuail','1362','2015-06-25 11:41:13','2015-06-25 11:41:13');"""

# Extracting the columns from the SQL insert statement
columns_pattern = re.compile(r'`([^`]*)`')
columns = columns_pattern.findall(sql_insert)

# Extracting the values part from the SQL insert statement
values_part = sql_insert.split("VALUES")[1].strip().rstrip(';')

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

# Writing to CSV
with open('districts.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(columns)  # Writing the header
    csvwriter.writerows(values_list)  # Writing the data rows

print("CSV file 'districts.csv' generated successfully.")
