from util import * 

data = read_json('data/raw.json')

hospitals = []

n = len(data)

for i in range(n):
    # print(i)
    d = data[i]
    h = {
            'name': d[1].strip(),
            'reg_code': d[2].strip(),
            'facility_type': d[3].strip(),
            'facility_category': d[4].strip(),
            'district': d[5].strip(),
            'upazila': d[6].strip(),
            'address': d[7].strip() 
        }

    hospitals.append(h)


print(len(hospitals))

print(json.dumps(hospitals[:3],indent=2))

write_json('data/private-hospitals-bd.json',hospitals)