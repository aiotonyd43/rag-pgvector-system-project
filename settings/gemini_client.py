from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI

from settings.config import settings

class GeminiClientService:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.gemini_api_key)
        self.langchain_gemini = ChatGoogleGenerativeAI(
            google_api_key=settings.gemini_api_key,
            model="gemini-2.0-flash", 
            temperature=0.1, 
            max_retries=2
        )