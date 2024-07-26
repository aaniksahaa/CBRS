import re

def extract_hospital_names(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Define the regex pattern to match all spans with class "OSrXXb"
    pattern = r'<span class="OSrXXb">(.*?)</span>'
    
    # Find all matches of the pattern in the HTML content
    matches = re.findall(pattern, html_content)

    return matches

# Replace 'path/to/your/file.html' with the actual path to your HTML file
file_path = 'gmap.html'
hospital_names = extract_hospital_names(file_path)

if hospital_names:
    print("Hospital Names:")
    for name in hospital_names:
        print(name)
else:
    print("No hospital names found.")
