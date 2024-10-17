from dotenv import load_dotenv
load_dotenv()
import os 
import calendar
import json 

from openai import OpenAI
import tiktoken

from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_community.callbacks.manager import get_openai_callback

llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

TG_TOKEN = os.getenv('TG_TOKEN')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_API_KEY = os.getenv('LLAMA_API_KEY')
ENV = os.getenv('ENV')

import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def debug(x):
    if ENV == 'development':
        print(x)


def read_json(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_json(filename, data):
    j = json.dumps(data, indent=4)
    with open(filename, 'w') as json_file:
        json_file.write(j)

def write_txt(filename, text, mode='w'):
    with open(filename, mode, encoding='utf-8') as f:
        f.write(text)

def read_txt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    return content




def get_date_text(month, year):
    return f'{calendar.month_name[month]}, {year}'

def get_full_name(user):
    first_name = user.first_name
    last_name = user.last_name if user.last_name else ''
    
    # Format the user's name
    full_name = f"{first_name} {last_name}".strip()

    return full_name


def count_tokens(text, model_name="gpt-3.5-turbo"):
    encoder = tiktoken.encoding_for_model(model_name)
    tokens = encoder.encode(text)
    return len(tokens)


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

    prompt = f""" 
{sample_text}

See I have this text message, and from it, i manually generated this json

{json.dumps(sample_json)}

observe carefully how i skipped the info that are not mentioned in the text.

Similarly make a json for this text,

<START>

{user_text}

<END>

remember that the json format, must be the same, you can only change the contents. Do not make up anything as it is sensitive. If a information is not mentioned, ,keep it blank, output ONLY a json, nothing else

Some instructions
- For bags needed, give the number as a string. If the text does not specify it, keep the string empty
- If there is something like আজ, today, আগামীকাল, কাল, tomorrow etc, relative dates, convert it to actual date with respect to today's date
- Keep the contact numbers and info exact and do not change to the slightest extent
- In case of monetary compensation  fields, write either "Y"/"N"/empty string
    """

    # print(prompt)

    # exit()

    prompt_token_count = count_tokens(prompt)
    debug(f'\nToken count of prompt = {prompt_token_count}')

    client = None 

    openai_models = ["gpt-3.5-turbo", "gpt-4o"]
    llama_models = ["llama2-7b", "llama2-13b", "llama2-70b"]

    # CHAT_MODEL = "llama2-70b"
    # CHAT_MODEL = "gpt-3.5-turbo"
    CHAT_MODEL = "gpt-4o"

    if CHAT_MODEL in llama_models:
        client = OpenAI(
            api_key = LLAMA_API_KEY,
            base_url = "https://api.llama-api.com"
        )
    elif CHAT_MODEL in openai_models:
        client = OpenAI(
            api_key = OPENAI_API_KEY,
        )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    message = response.choices[0].message.content
    message_token_count = count_tokens(message)

    total_token_count = prompt_token_count + message_token_count

    output = message

    response = {
        'text': output,
        'input_token_count': prompt_token_count,
        'output_token_count': message_token_count,
        'total_token_count': total_token_count,
    }

    # print(f"\nQuery:\n{query_text}\n")
    # print(f"Answer:\n{answer['text']}")
    # print(f"\nToken Count of input = {answer['input_token_count']}")
    # print(f"Token Count of output = {answer['output_token_count']}")
    # print(f"Total Token Count = {answer['total_token_count']}\n\n")

    return response

def get_info(user_text):
    response = get_response(user_text)

    data = response['text'].replace('```','').replace('json','')

    data = json.loads(data)

    return data