import tabula
import pandas as pd

# Path to the PDF file
pdf_path = 'data/dhaka-hospitals.pdf'

# Extract tables from the PDF
tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

# Save each table to a separate CSV file
for i, table in enumerate(tables):
    csv_path = f'output_table_{i + 1}.csv'
    table.to_csv(csv_path, index=False)
    print(f'Saved table {i + 1} to {csv_path}')
