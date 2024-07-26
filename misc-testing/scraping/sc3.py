import requests

url = "http://103.247.238.81/hsmdghs/registration/server_side.php"
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
    "Cookie": "_ga=GA1.1.255730040.1721971253; _gid=GA1.1.62774543.1721971253; _ga_04748DDHSQ=GS1.1.1721974129.1.0.1721974129.0.0.0; _ga_W9DDFGC4Y8=GS1.1.1721976438.3.0.1721976438.0.0.0; PHPSESSID=9ujdr0btc1bsddnoe8u1ibsa85"
}
data = {
    "type": "",
    "organization_type": "",
    "current_bed_no": "",
    "division": "",
    "district": "",
    "upazila": "",
    "user_type": "public",
    "user_id": "",
    "show": "",
    "application_status": "",
    "is_checked": "",
    "is_checked_final": "",
    "is_this_facility_new": "",
    "application_year": "",
    "application_type": ""
}

response = requests.post(url, headers=headers, data=data)
print(response.status_code)
print(response.text)
