from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from environment import GEMINI_API_KEY

class ProfileUpdate(BaseModel):
    psy: dict = Field(default_factory=dict, description="Psychological traits with scores 0–1")
    demo: dict = Field(default_factory=dict, description="Demographic attributes (raw values)")
    beh: dict = Field(default_factory=dict, description="Behavioral patterns with scores 0–1")
    int: dict = Field(default_factory=dict, description="Interests with scores 0–1")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=GEMINI_API_KEY
)

parser = PydanticOutputParser(pydantic_object=ProfileUpdate)

template = """{prompt_text}"""
prompt_template = ChatPromptTemplate.from_template(template)
