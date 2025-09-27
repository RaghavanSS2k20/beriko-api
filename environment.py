import os
from dotenv import load_dotenv
load_dotenv()

def get_env(env):
    return os.getenv(env)

GEMINI_API_KEY = get_env("GEMINI_API_KEY")
ENGINE_URL = get_env("ENGINE_URL")
