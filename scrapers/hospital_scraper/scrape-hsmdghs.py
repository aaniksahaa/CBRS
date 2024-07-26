import requests
from util import * 
import time 

url = "http://103.247.238.81/hsmdghs/registration/server_side.php?type=&organization_type=&current_bed_no=&division=&district=&upazila=&user_type=public&user_id=&show=&application_status=&is_checked=&is_checked_final=&is_this_facility_new=&application_year=&application_type="

headers = {
    "Host": "103.247.238.81",
    "Connection": "keep-alive",
    "Content-Length": "1777",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "http://103.247.238.81",
    "Referer": "http://103.247.238.81/hsmdghs/registration/hsm_facility_show_public.php",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "_ga=GA1.1.255730040.1721971253; _gid=GA1.1.62774543.1721971253; _ga_04748DDHSQ=GS1.1.1721974129.1.0.1721974129.0.0.0; PHPSESSID=9ujdr0btc1bsddnoe8u1ibsa85; _gat=1; _ga_W9DDFGC4Y8=GS1.1.1721976438.3.1.1721977546.0.0.0"
}

data = {
    "draw": "2",
    "columns[0][data]": "0",
    "columns[0][name]": "",
    "columns[0][searchable]": "true",
    "columns[0][orderable]": "true",
    "columns[0][search][value]": "",
    "columns[0][search][regex]": "false",
    "columns[1][data]": "1",
    "columns[1][name]": "",
    "columns[1][searchable]": "true",
    "columns[1][orderable]": "true",
    "columns[1][search][value]": "",
    "columns[1][search][regex]": "false",
    "columns[2][data]": "2",
    "columns[2][name]": "",
    "columns[2][searchable]": "true",
    "columns[2][orderable]": "true",
    "columns[2][search][value]": "",
    "columns[2][search][regex]": "false",
    "columns[3][data]": "3",
    "columns[3][name]": "",
    "columns[3][searchable]": "true",
    "columns[3][orderable]": "true",
    "columns[3][search][value]": "",
    "columns[3][search][regex]": "false",
    "columns[4][data]": "4",
    "columns[4][name]": "",
    "columns[4][searchable]": "true",
    "columns[4][orderable]": "true",
    "columns[4][search][value]": "",
    "columns[4][search][regex]": "false",
    "columns[5][data]": "5",
    "columns[5][name]": "",
    "columns[5][searchable]": "true",
    "columns[5][orderable]": "true",
    "columns[5][search][value]": "",
    "columns[5][search][regex]": "false",
    "columns[6][data]": "6",
    "columns[6][name]": "",
    "columns[6][searchable]": "true",
    "columns[6][orderable]": "true",
    "columns[6][search][value]": "",
    "columns[6][search][regex]": "false",
    "columns[7][data]": "7",
    "columns[7][name]": "",
    "columns[7][searchable]": "true",
    "columns[7][orderable]": "true",
    "columns[7][search][value]": "",
    "columns[7][search][regex]": "false",
    "order[0][column]": "0",
    "order[0][dir]": "asc",
    "start": "0",
    "length": "100",
    "search[value]": "",
    "search[regex]": "false"
}

start = 1
end = 162

for i in range(start, end+1):
    data["draw"] = str(i)
    data["start"] = str((i-1)*100)
    response = requests.post(url, headers=headers, data=data)

    j = response.json()

    write_json(f'responses/{i}.json',j)

    status = response.status_code

    if(status == 200):
        print(f'Request for chunk {i} successful')
    else:
        print(f'\nError !!! Chunk {i} not received\n')

    time.sleep(0.5)