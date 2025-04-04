from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Initialize the ChatOpenAI model with OpenRouter's endpoint
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="",
    model="deepseek/deepseek-chat-v3-0324:free"
)

# Create a message to send
messages = [HumanMessage(content="What is the meaning of life?")]

# Invoke the model and get the response
response = llm.invoke(messages)

# Print the content of the response
print(response.content)