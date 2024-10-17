from dotenv import load_dotenv
load_dotenv()

from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_community.callbacks.manager import get_openai_callback

llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

def get_coordinates(place_name):
    class Coordinates(BaseModel):
        latitude: float = Field(description="Latitude of the location")
        longitude: float = Field(description="Longitude of the location")

    parser = JsonOutputParser(pydantic_object=Coordinates)

    prompt = PromptTemplate(
        template="""
    You have to correctly provide the latitude and longitude of a place in Bangladesh in
    a JSON format.

    Name of the place: {place_name}

    Now provide nothing but the required JSON.
    {format_instructions}
    """,
        input_variables=["place_name"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    with get_openai_callback() as cb:
        # place_name = "Uttara 11, Mansur Ali Medical College"
        response = chain.invoke({"place_name": place_name})
        print(cb)
        return response
    
print(get_coordinates("Dhaka Medical College"))
