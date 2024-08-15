from utils import *

filename = 'messages_500.txt'

content = read_txt(DATASET_DIR, filename)

messages = content.split('*'*20)

print(len(messages))

for i, m in enumerate(messages[:]):
    m = m.strip()
    print(show_banner(f'At message {i+1}'))
    data = {
        'message': m 
    }
    info = parse_blood_seeking_message(m)
    data.update(info)
    write_json('./dataset/out/raw/demo_500', f'{i}.json', data)

print(f'\n\n\nTotal cost = {OpenAIClient().cost} dollars\n\n\n')
