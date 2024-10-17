from utils import *

def get_response(user_text):
    sample_text = """
জরুরী ভিত্তিতে  AB(-)রক্তের প্রয়োজন।

💁রোগীর সমস্যা: কিডনি সমস্যা
🔴রক্তের গ্রুপ: AB নেগেটিভ
💉রক্তের পরিমাণ: 2 ব্যাগ
📆রক্তদানের তারিখ: 15/02/2024
⌚রক্তদানের সময় : সকাল ৯-১২ টা
🏥রক্তদানের স্থান : কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট, মিরপুর,   ঢাকা।
☎যোগাযোগঃ মার্জান
মোবাইলঃ 01915955585
01928317021
"""

    sample_json = {
    "blood_group": "AB-",
    "bags_needed": "2",
    "mediator": {
        "username": ""
    },
    "patient": {
        "name":"",
        "age-group":""
    },
    "condition": "কিডনি সমস্যা",
    "location": "কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট, মিরপুর, ঢাকা",
    "probable_day": "15/02/2024",
    "probable_time":"9am-12pm",
    "contacts": [
        {
            "name": "মার্জান",
            "contact_numbers": ["01915955585", "01928317021"],
            "relation_with_patient": ""
        }
    ],
    "compensation": {
        "transportation": "",
        "allowance": ""
    }
}

    prompt = PromptTemplate(
        template="""
    {sample_input}

    See I have this text message, and from it, i manually generated this json

    {sample_output}

    observe carefully how i skipped the info that are not mentioned in the text.
Similarly make a json for this text,

<START>

{input}

<END>

remember that the json format, must be the same, you can only change the contents. Do not make up anything as it is sensitive. 
If a information is not mentioned, ,keep it blank, output ONLY a correctly-formatted json, nothing else.

Some instructions
- For bags needed, give the number as a string. If the text does not specify it, keep the string empty
- If there is something like আজ, today, আগামীকাল, কাল, tomorrow etc, relative dates, convert it to actual date with respect to today's date
- Keep the contact numbers and info exact and do not change to the slightest extent
- In case of monetary compensation  fields, write either "Y"/"N"/empty string
    """,
        input_variables=["sample_input", "sample_output", "input"]
    )

    chain = prompt | llm 

    with get_openai_callback() as cb:
        # place_name = "Uttara 11, Mansur Ali Medical College"
        response = chain.invoke({
            "sample_input": sample_text,
            "sample_output": json.dumps(sample_json),
            "input": user_text
            })
        print(cb)
        print(response)
        return response

def get_info(user_text):
    response = get_response(user_text)

    data = response.content.replace('```','').replace('json','')

    data = json.loads(data)

    return data

# Example of how to call the function
user_text = """
জরুরী ভিত্তিতে AB(-)রক্তের প্রয়োজন। 
💁রোগীর সমস্যা: কিডনি সমস্যা
🔴রক্তের গ্রুপ: AB নেগেটিভ
💉রক্তের পরিমাণ: 2 ব্যাগ
📆রক্তদানের তারিখ: 15/02/2024
⌚রক্তদানের সময় : সকাল ৯-১২ টা
🏥রক্তদানের স্থান : কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট, মিরপুর, ঢাকা।
☎যোগাযোগঃ মার্জান
মোবাইলঃ 01915955585
01928317021
"""

print(json.dumps(get_info(user_text), indent=4))
