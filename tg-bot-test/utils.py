from dotenv import load_dotenv
import os 
import calendar

load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')

import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_date_text(month, year):
    return f'{calendar.month_name[month]}, {year}'

def get_full_name(user):
    first_name = user.first_name
    last_name = user.last_name if user.last_name else ''
    
    # Format the user's name
    full_name = f"{first_name} {last_name}".strip()

    return full_name