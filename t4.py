from utils import * 

q = """
B(-) Ve blood needed.
Amount :2 bag

Date: 07.06.24(Tomorrow )
Time: After 5 pm
Location: পঙ্গু হাসপাতাল, আগারগাঁও, ঢাকা।
Contact: 01728108552
Note:  Surgery hbe  blood arrange krte bola hoise.(RTA case)

আমার ফুপা এর অপারেশন। প্লীজ কেউ পারলে অ্যারেঞ্জ করে দেন। খুব urgent।
"""

q = "hi"

d = parse_blood_seeking_message(q)

write_json('','test.json',d)


