from utils import * 

messages = read_json('./dataset/demo-messages.json')

for i,m in enumerate(messages):
    info = get_info(m)
    write_json(f'./out/raw/{i}.json',info)
