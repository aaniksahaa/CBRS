from util import * 

c = read_txt('msg.txt')
separator = '***'
parts = c.split(separator)

messages = [msg.strip() for msg in parts]

write_json('demo-messages.json',messages)

