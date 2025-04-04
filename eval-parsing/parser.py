from util import *

from samples import *

def build_prompt(user_text):
    return f"""
You will be given a text message from a sender that is most possibly a blood donation seeking message.
If not, then just output that it is not related.
If it is blood donation related, you need to extract information correctly from it in the exact format shown in examples.

You must output a correctly formatted json containing the following fields:

blood_group: must be one of the 8 groups A+ , A- , B+ , B- , O+ , O- , AB+ , AB-
bags_needed: a number in English as a string, like "3" or hyphen-separated two numbers denoting a range like "3-4"
patient: it has three fields name, gender, age_group
        name: the name of patient
        gender: "M" or "F" or ""
        age_group: any of the four :- child / teenager / young / adult
condition: the patient condition in English
location: the stated location exactly as it is in the message
hospital_name: the full name of hospital as stated in the message
location_markers: an array of specific location markers
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
{sample_inp_1}
Your reponse json:
{json.dumps(sample_out_1)}

Text Message:
{sample_inp_2}
Your reponse json:
{json.dumps(sample_out_2)}

Text Message:
{sample_inp_3}
Your reponse json:
{json.dumps(sample_out_3)}

Text Message:
{sample_inp_4}
Your reponse json:
{json.dumps(sample_out_4)}

Now output the correctly formatted json for the following Text Message:

{user_text}

Reminders:
- Following the exact json format as example is mandatory
- Do not use any greetings etc. You must output ONLY the required correctly formatted json, nothing else
- Do not hallucinate. If you think, a piece of information is not present, keep that an empty string
"""


def parse_blood_donation_request_text(msg: str, provider: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    prompt = build_prompt(msg)
    try:
        print('called and waiting...')
        content, input_toks, output_toks, total_toks, cost = call_model(prompt, provider=provider, model=model)
        print('result came')
        clean = content.replace('```', '').replace('json', '')
        clean = re.sub(r'\\u[0-9a-fA-F]{0,3}[^0-9a-fA-F]', '', clean)
        try:
            parsed_json = json.loads(clean)
        except Exception:
            parsed_json = None
    except Exception as e:
        parsed_json = None
        content = str(e)
        input_toks = output_toks = total_toks = 0
        cost = 0.0

    result = {
        "input_text": msg,
        "output_text": content,
        "output_json": parsed_json,
        "input_tokens": input_toks,
        "output_tokens": output_toks,
        "total_tokens": total_toks,
        "cost_usd": round(cost, 6),
        "provider": provider,
        "model": model
    }
    return result
