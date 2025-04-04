from util import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

text = 'hello, how you?'

# print(call_model(text, provider='google', model='gemini-2.0-flash'))

print(call_model(text, provider='openai', model='gpt-4o-mini'))

# # Create the chat object for Gemini Flash 2.0
# chat = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     temperature=0.7,
#     google_api_key=GOOGLE_API_KEY
# )

# # Send a message and get the response
# response = chat.invoke([
#     HumanMessage(content="What's a fun fact about quantum physics?")
# ])

# # Print the output
# print(response.content)
