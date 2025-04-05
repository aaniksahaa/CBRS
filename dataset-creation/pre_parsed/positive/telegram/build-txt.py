from util import *

ms = read_json('raw/messages.json')

ts = []

for m in ms:
    ts.append(m['text'])

sep = "\n\n\n" + 20*"*" + "\n\n\n" 

s = sep.join(ts)

write_txt('raw/messages-prev.txt', s)

