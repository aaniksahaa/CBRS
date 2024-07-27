from utils import * 
import json

data = read_json('res.json')

data = data['text']

data = data.replace('```','').replace('json','')

print(data)

j = json.loads(data)

write_json('data.json',j)

print(j)
