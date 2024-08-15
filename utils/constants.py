from dotenv import load_dotenv
import os 

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENV = os.getenv('ENV')

DEBUG = (ENV == 'development')

OPENAI_CHAT_MODELS = ['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4o']

DEFAULT_OPENAI_CHAT_MODEL = OPENAI_CHAT_MODELS[1]

DATASET_DIR = './dataset' 
PARSING_OUTPUT_DIR = './dataset/out/raw'