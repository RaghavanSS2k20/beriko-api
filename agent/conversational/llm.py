from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from .prompt import prompt
# from profile_service import handle_engine_call  # your ProfileBuilder agent
from environment import GEMINI_API_KEY
import asyncio

# Conversation Agent
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.7,
     google_api_key=GEMINI_API_KEY,
     max_retries=0
)

# prompt_template = ChatPromptTemplate.from_template(
#     "{history}\nUser: {content}\nBeriko:"
# )