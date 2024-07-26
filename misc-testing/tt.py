import json

# Specify the filename
filename = 'hospitals.json'

# Read and parse the JSON data from the file
with open(filename, 'r') as file:
    data = json.load(file)

for i, h in enumerate(data):
    h['name'] = h['name'].split('[')[0].strip()
    if h['core_name'] is None:
        h['core_name'] = h['name']
    data[i] = h 

with open('hos.json','w') as f:
    f.write(json.dumps(data,indent=2))


