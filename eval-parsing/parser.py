from util import *

from samples import *


def build_zero_shot_prompt(user_text):
    return f"""
You will be provided with a message, typically sent by an individual or organization, which may pertain to a request for blood donation.  
Your task is to determine whether the message is a blood donation request, and if yes, then to extract the necessary information.

- If the message is **not** a blood donation request, respond with:  
  `"{json.dumps(negative_sample_out_1)}"`
  In this case, you do not need to include any other fields in the json.

- If the message is a blood donation request, extract the relevant information and present it in a **well-structured, valid JSON object** that conforms exactly to the schema defined below.

Carefully analyze the content to ensure that all fields are correctly inferred and appropriately formatted.

blood_group: must be one of the 8 groups A+ , A- , B+ , B- , O+ , O- , AB+ , AB- or ""
bags_needed: a number in English as a string, like "3" or hyphen-separated two numbers denoting a range like "3-4"
patient: it has three fields name, gender, age_group
        name: the name of patient or ""
        gender: "M" or "F" or ""
        age_group: any of the four :- child / teenager / young / adult or ""
condition: the patient condition in correct English, as inferred from the message, it may consist of small-letter key words or key phrases separated by comma
location: the stated location exactly as it is stated in the message
hospital_name: the full name of hospital exactly as it is stated in the message
location_markers: an array of specific location markers, preferably the names of cities or such regions stated in the message
probable_day: can be in 5 formats, choose as is appropriate according to the message, opt for the more specific date options(DD/MM or DD/MM/YYYY) if you have choices
                DD/MM or DD/MM/YYYY or "today" or "tomorrow" or "n days later"
probable_time: can be in 6 formats, choose as is appropriate according to the message, opt for the more specific time options(HH:MM) if you have choices
                HH:MM or before HH:MM or after HH:MM or HH:MM-HH:MM or "in n hours"
               here you are expected to give the times in 24-hour format
contacts: an array of the contacts you find, each element will be object with 3 fields
            name: the name of person
            contact_numbers: an array of the contact numbers, the numbers should be exact as it is in the message
            relation_with_patient: the relation as stated in message
compensation: will have two fields, they should be either "Y" or "N" or ""
            transportation: whether any compensation for transportation will be provided
            allowance: whether any extra money will be provided

Now output the correctly formatted json for the following Text Message:

{user_text}

**Reminders:**
- Adhering strictly to the JSON schema is **mandatory**.
- Do **not** include any greetings, explanations, or additional text. Output **only** the correctly formatted JSON.
- Do **not** fabricate or hallucinate information. If a particular field is missing in the message, set its value to an empty string `""`.

Ensure your output is precise, complete, and formatted in a manner suitable for automated parsing.

"""


def build_few_shot_prompt(user_text):
    return f"""
You will be provided with a message, typically sent by an individual or organization, which may pertain to a request for blood donation.  
Your task is to determine whether the message is a blood donation request, and if yes, then to extract the necessary information.

- If the message is **not** a blood donation request, respond with:  
  `"{json.dumps(negative_sample_out_1)}"`
  In this case, you do not need to include any other fields in the json.

- If the message is a blood donation request, extract the relevant information and present it in a **well-structured, valid JSON object** that conforms exactly to the schema defined below.

Carefully analyze the content to ensure that all fields are correctly inferred and appropriately formatted.

blood_group: must be one of the 8 groups A+ , A- , B+ , B- , O+ , O- , AB+ , AB- or ""
bags_needed: a number in English as a string, like "3" or hyphen-separated two numbers denoting a range like "3-4"
patient: it has three fields name, gender, age_group
        name: the name of patient or ""
        gender: "M" or "F" or ""
        age_group: any of the four :- child / teenager / young / adult or ""
condition: the patient condition in correct English, as inferred from the message, it may consist of small-letter key words or key phrases separated by comma
location: the stated location exactly as it is stated in the message
hospital_name: the full name of hospital exactly as it is stated in the message
location_markers: an array of specific location markers, preferably the names of cities or such regions stated in the message
probable_day: can be in 5 formats, choose as is appropriate according to the message, opt for the more specific date options(DD/MM or DD/MM/YYYY) if you have choices
                DD/MM or DD/MM/YYYY or "today" or "tomorrow" or "n days later"
probable_time: can be in 6 formats, choose as is appropriate according to the message, opt for the more specific time options(HH:MM) if you have choices
                HH:MM or before HH:MM or after HH:MM or HH:MM-HH:MM or "in n hours"
               here you are expected to give the times in 24-hour format
contacts: an array of the contacts you find, each element will be object with 3 fields
            name: the name of person
            contact_numbers: an array of the contact numbers, the numbers should be exact as it is in the message
            relation_with_patient: the relation as stated in message
compensation: will have two fields, they should be either "Y" or "N" or ""
            transportation: whether any compensation for transportation will be provided
            allowance: whether any extra money will be provided

Examples:

Text Message:
{positive_sample_inp_1}
Your reponse json:
{json.dumps(positive_sample_out_1)}

Text Message:
{positive_sample_inp_2}
Your reponse json:
{json.dumps(positive_sample_out_2)}

Text Message:
{positive_sample_inp_3}
Your reponse json:
{json.dumps(positive_sample_out_3)}

Text Message:
{negative_sample_inp_1}
Your reponse json:
{json.dumps(negative_sample_out_1)}

Text Message:
{negative_sample_inp_2}
Your reponse json:
{json.dumps(negative_sample_out_2)}

Now output the correctly formatted json for the following Text Message:

{user_text}

**Reminders:**
- Adhering strictly to the example JSON structure is **mandatory**.
- Do **not** include any greetings, explanations, or additional text. Output **only** the correctly formatted JSON.
- Do **not** fabricate or hallucinate information. If a particular field is missing in the message, set its value to an empty string `""`.

Ensure your output is precise, complete, and formatted in a manner suitable for automated parsing.

"""


def parse_blood_donation_request_text(msg: str, provider: str, model: str = DEFAULT_MODEL, method: str = "few_shot") -> Dict[str, Any]:
    prompt = ""
    if method == "zero_shot":
        prompt = build_zero_shot_prompt(msg)
    else:
        prompt = build_few_shot_prompt(msg)
    print(prompt)
    try:
        # print('called and waiting...')
        response = get_response(prompt, provider=provider, model=model)
        content = response.get("output_text", "")
        # print('result came')
        clean = content.replace('```', '').replace('json', '')
        clean = re.sub(r'\\u[0-9a-fA-F]{0,3}[^0-9a-fA-F]', '', clean)
        try:
            parsed_json = parse_json_from_output(content)
        except Exception:
            parsed_json = None
        response['blood_donation_request_message'] = msg 
        response['parsed_json'] = parsed_json
        if "is_blood_donation_request" in parsed_json and parsed_json["is_blood_donation_request"] == "false":
            response["is_blood_donation_request"] = False
        else:
            response["is_blood_donation_request"] = True
    except Exception as e:
        parsed_json = None
        content = str(e)
        input_toks = output_toks = total_toks = 0
        cost = 0.0
        response = {
            "input_text": msg,
            "output_text": content,
            "input_tokens": input_toks,
            "output_tokens": output_toks,
            "total_tokens": total_toks,
            "cost_usd": round(cost, 6),
            "provider": provider,
            "model": model,
            'blood_donation_request_message': msg,
            "parsed_json": parsed_json,
            "is_blood_donation_request": None 
        }

    return response
