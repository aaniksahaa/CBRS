import json 
from utils import * 

t = read_txt('','./a.txt')
# Replace invalid Unicode escape sequences with a placeholder or correct them
t = re.sub(r'\\u[0-9a-fA-F]{0,3}[^0-9a-fA-F]', '', t)
d = json.loads(t)

write_json('','test.json',d)

print(d)

