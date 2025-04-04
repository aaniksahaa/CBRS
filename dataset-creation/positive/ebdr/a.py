from util import *

def get_requests_from_txt(path):
    j = read_txt(path)
    data = json.loads(j)
    return data

paths = ['raw/BDC.txt', 'raw/HO.txt', 'raw/PDR.txt']

r = []

for path in paths:
    r.extend(get_requests_from_txt(path))

out_path = 'merged.json'

# Step 3: Save it as a clean .json file
write_json(out_path, r)

print(len(r))

print(f"✅ JSON successfully parsed and written to {out_path}")