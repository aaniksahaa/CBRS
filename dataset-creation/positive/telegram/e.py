from util import *

path = 'raw/messages.json'

a = read_json(path)

for d in a:
    del d['is_blood_donation_request']
    d['is_blood_donation_request'] = True

write_json(path, a)