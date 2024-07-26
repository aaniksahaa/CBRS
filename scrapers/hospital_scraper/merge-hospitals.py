from util import *

start = 1
end = 162

hospitals = []

for i in range(start,end+1):
    filename = f'responses/{i}.json'

    data = read_json(filename)
    data = data['data']

    hospitals += data

    # print(len(data))

write_json('data/raw.json',hospitals)

print(len(hospitals))